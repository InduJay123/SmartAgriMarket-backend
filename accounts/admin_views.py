import csv
from decimal import Decimal
from io import BytesIO, StringIO

from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework import status
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.db import DatabaseError
from django.db.models import Avg, Max, Sum, Count
from django.db.models.functions import Coalesce, TruncMonth
from datetime import date
from rest_framework_simplejwt.tokens import RefreshToken

from .models import ActivityLog, FarmerDetails, BuyerDetails
from .serializers_admin import ActivityLogSerializer, FarmerAdminSerializer, BuyerAdminSerializer
from crops.models import Crop
from ml_api.models import PredictionHistory
from prices.models import CropPrice
from marketplace.models import Marketplace


def _parse_report_format(request):
    report_format = (request.query_params.get("format") or "csv").strip().lower()
    if report_format not in {"csv", "pdf"}:
        return None, Response({"detail": "Unsupported format"}, status=400)
    return report_format, None


def _parse_report_filters(request):
    crop = (request.query_params.get("crop") or "all").strip()
    start_value = request.query_params.get("startDate") or request.query_params.get("start_date")
    end_value = request.query_params.get("endDate") or request.query_params.get("end_date")

    start_date = parse_date(start_value) if start_value else None
    end_date = parse_date(end_value) if end_value else None

    if start_value and not start_date:
        return None, Response({"error": "Invalid startDate. Use YYYY-MM-DD."}, status=400)

    if end_value and not end_date:
        return None, Response({"error": "Invalid endDate. Use YYYY-MM-DD."}, status=400)

    if start_date and end_date and start_date > end_date:
        return None, Response(
            {"error": "Start date must be earlier than or equal to the end date."},
            status=400,
        )

    return {
        "crop": crop,
        "start_date": start_date,
        "end_date": end_date,
    }, None


def _apply_marketplace_filters(queryset, filters):
    crop = filters["crop"]
    start_date = filters["start_date"]
    end_date = filters["end_date"]

    if crop and crop.lower() != "all":
        queryset = queryset.filter(crop__crop_name__iexact=crop)

    if start_date:
        queryset = queryset.filter(created_at__date__gte=start_date)

    if end_date:
        queryset = queryset.filter(created_at__date__lte=end_date)

    return queryset


def _apply_prediction_filters(queryset, filters):
    crop = filters["crop"]
    start_date = filters["start_date"]
    end_date = filters["end_date"]

    if crop and crop.lower() != "all":
        queryset = queryset.filter(crop_name__iexact=crop)

    if start_date:
        queryset = queryset.filter(created_at__date__gte=start_date)

    if end_date:
        queryset = queryset.filter(created_at__date__lte=end_date)

    return queryset


def _build_report_filename(prefix, filters, extension="csv"):
    crop = filters["crop"] if filters["crop"].lower() != "all" else "all-crops"
    start_date = filters["start_date"].isoformat() if filters["start_date"] else "all-time"
    end_date = filters["end_date"].isoformat() if filters["end_date"] else "today"
    return f"{prefix}_{crop}_{start_date}_{end_date}.{extension}".replace(" ", "-").lower()


def _csv_response(filename, fieldnames, rows):
    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
    writer.writeheader()

    for row in rows:
        writer.writerow(row)

    response = HttpResponse(buffer.getvalue(), content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


def _escape_pdf_text(value):
    escaped = str(value).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    return escaped.encode("latin-1", errors="replace").decode("latin-1")


def _build_simple_pdf_bytes(lines):
    if not lines:
        lines = ["No data available"]

    max_lines_per_page = 45
    pages = [lines[i:i + max_lines_per_page] for i in range(0, len(lines), max_lines_per_page)]

    content_streams = []
    for page_lines in pages:
        stream_lines = ["BT", "/F1 10 Tf", "50 800 Td", "14 TL"]
        for line in page_lines:
            stream_lines.append(f"({_escape_pdf_text(line)}) Tj")
            stream_lines.append("T*")
        stream_lines.append("ET")
        content_streams.append("\n".join(stream_lines).encode("latin-1", errors="replace"))

    objects = []

    # 1: catalog
    objects.append(b"<< /Type /Catalog /Pages 2 0 R >>")

    # 2: pages (kids filled after page objects are counted)
    page_count = len(content_streams)
    page_obj_numbers = [3 + (i * 2) for i in range(page_count)]
    font_obj_number = 3 + (page_count * 2)
    kids = " ".join(f"{obj_no} 0 R" for obj_no in page_obj_numbers)
    objects.append(f"<< /Type /Pages /Count {page_count} /Kids [ {kids} ] >>".encode("latin-1"))

    # Page/content pairs
    for index, stream_bytes in enumerate(content_streams):
        page_obj_number = 3 + (index * 2)
        content_obj_number = page_obj_number + 1

        page_obj = (
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 842] "
            f"/Resources << /Font << /F1 {font_obj_number} 0 R >> >> "
            f"/Contents {content_obj_number} 0 R >>"
        ).encode("latin-1")
        objects.append(page_obj)

        content_obj_prefix = f"<< /Length {len(stream_bytes)} >>\nstream\n".encode("latin-1")
        content_obj_suffix = b"\nendstream"
        objects.append(content_obj_prefix + stream_bytes + content_obj_suffix)

    # Font object
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")

    buffer = BytesIO()
    buffer.write(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")

    offsets = [0]
    for obj_index, obj_body in enumerate(objects, start=1):
        offsets.append(buffer.tell())
        buffer.write(f"{obj_index} 0 obj\n".encode("latin-1"))
        buffer.write(obj_body)
        buffer.write(b"\nendobj\n")

    xref_position = buffer.tell()
    buffer.write(f"xref\n0 {len(objects) + 1}\n".encode("latin-1"))
    buffer.write(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        buffer.write(f"{offset:010d} 00000 n \n".encode("latin-1"))

    buffer.write(
        (
            f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
            f"startxref\n{xref_position}\n%%EOF"
        ).encode("latin-1")
    )

    return buffer.getvalue()


def _pdf_response(filename, fieldnames, rows, title):
    lines = [title, ""]
    if not rows:
        lines.append("No records found for selected filters.")
    else:
        header_line = " | ".join(fieldnames)
        lines.append(header_line)
        lines.append("-" * min(len(header_line), 120))

        for row in rows:
            values = [str(row.get(field, "")) for field in fieldnames]
            line = " | ".join(values)
            lines.append(line[:180])

    pdf_bytes = _build_simple_pdf_bytes(lines)
    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


def _decimal_to_string(value):
    if value is None:
        return ""
    if not isinstance(value, Decimal):
        value = Decimal(str(value))
    return f"{value.quantize(Decimal('0.01'))}"


def _float_to_string(value):
    if value is None:
        return ""
    return f"{float(value):.2f}"


def _log_activity(*, user, action_type, module, message, metadata=None):
    try:
        ActivityLog.objects.create(
            actor=user,
            actor_username=user.username if user else "",
            action_type=action_type,
            module=module,
            message=message,
            metadata=metadata or {},
        )
    except DatabaseError:
        return


def _to_bool(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "1", "yes", "y", "on"}:
            return True
        if normalized in {"false", "0", "no", "n", "off", ""}:
            return False
    if value in (0, 1):
        return bool(value)
    return None


def _shift_month_start(month_start: date, delta_months: int) -> date:
    total = (month_start.year * 12 + month_start.month - 1) + delta_months
    year = total // 12
    month = (total % 12) + 1
    return date(year, month, 1)


def _rolling_month_starts(months: int = 6) -> list[date]:
    anchor = date.today().replace(day=1)
    return [_shift_month_start(anchor, i) for i in range(-(months - 1), 1)]


class AdminLoginAPI(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"error": "Username and password are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(username=username, password=password)
        if not user:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

        if not (user.is_staff or user.is_superuser):
            return Response({"error": "Not an admin account"}, status=status.HTTP_403_FORBIDDEN)

        refresh = RefreshToken.for_user(user)
        _log_activity(
            user=user,
            action_type=ActivityLog.ActionType.ADMIN_LOGIN_SUCCESS,
            module="accounts",
            message="Admin logged in successfully",
            metadata={"user_id": user.id},
        )
        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "role": "Admin",
                },
            },
            status=status.HTTP_200_OK,
        )


class AdminFarmersListAPI(APIView):
    """
    GET /api/auth/admin/farmers/
    Optional query param: ?status=pending|active|rejected  (default: all)

    pending  — registered, awaiting review  (profile.is_active=False, user.is_active=True)
    active   — approved by admin            (profile.is_active=True)
    rejected — rejected by admin            (profile.is_active=False, user.is_active=False)
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        status_param = request.query_params.get("status", "all")
        qs = FarmerDetails.objects.select_related("user").order_by("-id")

        if status_param == "pending":
            qs = qs.filter(is_active=False, user__is_active=True)
        elif status_param == "active":
            qs = qs.filter(is_active=True)
        elif status_param == "rejected":
            qs = qs.filter(is_active=False, user__is_active=False)

        serializer = FarmerAdminSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdminBuyersListAPI(APIView):
    """
    GET /api/auth/admin/buyers/
    Optional query param: ?status=pending|active|rejected  (default: all)
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        status_param = request.query_params.get("status", "all")
        qs = BuyerDetails.objects.select_related("user").order_by("-id")

        if status_param == "pending":
            qs = qs.filter(is_active=False, user__is_active=True)
        elif status_param == "active":
            qs = qs.filter(is_active=True)
        elif status_param == "rejected":
            qs = qs.filter(is_active=False, user__is_active=False)

        serializer = BuyerAdminSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdminPendingUsersAPI(APIView):
    """
    GET /api/auth/admin/pending-users/
    Returns all farmers and buyers who registered but have not yet been approved or rejected.
    pending = profile.is_active=False AND user.is_active=True
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        pending_farmers = FarmerDetails.objects.filter(
            is_active=False, user__is_active=True
        ).select_related("user").order_by("-id")

        pending_buyers = BuyerDetails.objects.filter(
            is_active=False, user__is_active=True
        ).select_related("user").order_by("-id")

        return Response(
            {
                "farmers": FarmerAdminSerializer(pending_farmers, many=True).data,
                "buyers": BuyerAdminSerializer(pending_buyers, many=True).data,
            },
            status=status.HTTP_200_OK,
        )


class AdminVerifyUserAPI(APIView):
    """
    PATCH /api/auth/admin/verify/
    Body: { "role": "Farmer"|"Buyer", "user_id": <int>, "is_active": true|false }

    Approve (is_active=true):  profile.is_active=True,  user.is_active=True
    Reject  (is_active=false): profile.is_active=False, user.is_active=False
    This lets the pending list distinguish between "not yet reviewed" and "rejected".
    """
    permission_classes = [IsAdminUser]

    def patch(self, request):
        role = request.data.get("role")
        user_id = request.data.get("user_id")
        is_active = request.data.get("is_active")

        if not role or user_id is None:
            return Response({"error": "role and user_id are required"}, status=400)

        role_normalized = str(role).strip().lower()

        if role_normalized in ["farmer", "farmers", "f"]:
            model = FarmerDetails
        elif role_normalized in ["buyer", "buyers", "b"]:
            model = BuyerDetails
        else:
            return Response({"error": "role must be Farmer or Buyer"}, status=400)

        profile = model.objects.filter(user_id=user_id).select_related("user").first()
        if not profile:
            return Response({"error": "Profile not found"}, status=404)

        approved = _to_bool(is_active)
        if approved is None:
            return Response({"error": "is_active must be true or false"}, status=400)

        # Update profile status
        profile.is_active = approved
        profile.deactivate_at = None if approved else timezone.now()
        profile.save()

        # Sync Django User.is_active so the pending filter works correctly:
        #   approved  → user can log in (user.is_active=True)
        #   rejected  → user cannot log in (user.is_active=False)
        profile.user.is_active = approved
        profile.user.save(update_fields=["is_active"])

        action_type = (
            ActivityLog.ActionType.USER_APPROVED
            if approved
            else ActivityLog.ActionType.USER_REJECTED
        )
        role_label = "Farmer" if model is FarmerDetails else "Buyer"
        display_name = profile.fullname or profile.user.username
        _log_activity(
            user=request.user,
            action_type=action_type,
            module="accounts",
            message=f"{role_label} {display_name} was {'approved' if approved else 'rejected'}",
            metadata={
                "target_user_id": profile.user_id,
                "target_profile_id": profile.id,
                "target_role": role_label,
                "is_active": approved,
            },
        )

        return Response({"message": "Updated", "is_active": profile.is_active})


class AdminDashboardStatsAPI(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        total_farmers = FarmerDetails.objects.count()
        verified_farmers = FarmerDetails.objects.filter(is_active=True).count()
        # pending = registered but not yet reviewed (excludes rejected users)
        pending_approvals = FarmerDetails.objects.filter(
            is_active=False, user__is_active=True
        ).count()
        blocked_farmers = FarmerDetails.objects.filter(is_active=False).count() - pending_approvals
        buyers = BuyerDetails.objects.count()
        verified_buyers = BuyerDetails.objects.filter(is_active=True).count()
        blocked_buyers = BuyerDetails.objects.filter(is_active=False).count()
        crops = Crop.objects.count()
        
        top_region = FarmerDetails.objects.filter(is_active=True).exclude(region='').exclude(region__isnull=True).values('region').annotate(count=Count('region')).order_by('-count').first()
        most_farmers_region = top_region['region'] if top_region else "None"

        top_buyer_city = BuyerDetails.objects.filter(is_active=True).exclude(city='').exclude(city__isnull=True).values('city').annotate(count=Count('city')).order_by('-count').first()
        most_buyers_city = top_buyer_city['city'] if top_buyer_city else "None"

        return Response(
            {
                "verified_farmers": verified_farmers,
                "pending_approvals": pending_approvals,
                "blocked_farmers": blocked_farmers,
                "buyers": buyers,
                "verified_buyers": verified_buyers,
                "blocked_buyers": blocked_buyers,
                "most_buyers_city": most_buyers_city,
                "crops": crops,
                "total_farmers": total_farmers,
                "most_farmers_region": most_farmers_region,
            }
        )


class AdminDashboardChartsAPI(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        month_starts = _rolling_month_starts(months=6)
        start_date = month_starts[0]

        price_rows = (
            CropPrice.objects.filter(date__gte=start_date)
            .annotate(month=TruncMonth("date"))
            .values("month")
            .annotate(avg_price=Avg("price"))
            .order_by("month")
        )

        price_map = {}
        for row in price_rows:
            month = row["month"]
            if month is None:
                continue
            month_key = month.date() if hasattr(month, "date") else month
            price_map[month_key] = float(row["avg_price"] or 0)

        price_labels = [m.strftime("%b") for m in month_starts]
        price_values = [round(price_map.get(m, 0.0), 2) for m in month_starts]

        supply_labels = []
        supply_values = []
        try:
            supply_rows = (
                Marketplace.objects.filter(status="Available")
                .values("crop__crop_name")
                .annotate(total_supply=Coalesce(Sum("quantity"), 0))
                .order_by("-total_supply")[:6]
            )

            for row in supply_rows:
                supply_labels.append(row["crop__crop_name"] or "Unknown")
                supply_values.append(int(row["total_supply"] or 0))
        except DatabaseError:
            # In environments where the external market table is unavailable,
            # return empty supply data instead of failing the whole dashboard.
            supply_labels = []
            supply_values = []

        return Response(
            {
                "price_trend": {
                    "labels": price_labels,
                    "values": price_values,
                },
                "supply_by_crop": {
                    "labels": supply_labels,
                    "values": supply_values,
                },
            },
            status=status.HTTP_200_OK,
        )


class AdminTransactionReportAPI(APIView):
    permission_classes = [IsAdminUser]
    format_kwarg = None

    def get(self, request):
        report_format, format_error = _parse_report_format(request)
        if format_error:
            return format_error

        filters, error_response = _parse_report_filters(request)
        if error_response:
            return error_response

        queryset = _apply_marketplace_filters(
            Marketplace.objects.select_related("crop").filter(status="Sold").order_by("created_at", "market_id"),
            filters,
        )

        rows = []
        for listing in queryset:
            estimated_total_value = Decimal(listing.price) * Decimal(listing.quantity)
            sold_at = timezone.localtime(listing.created_at) if timezone.is_aware(listing.created_at) else listing.created_at

            rows.append(
                {
                    "sold_at": sold_at.isoformat() if sold_at else "",
                    "market_id": listing.market_id,
                    "crop": listing.crop.crop_name if listing.crop_id else "",
                    "farmer_id": listing.farmer_id,
                    "region": listing.region,
                    "district": listing.district,
                    "farming_season": listing.farming_season,
                    "farming_method": listing.farming_method,
                    "quantity": listing.quantity,
                    "unit": listing.unit,
                    "unit_price": _decimal_to_string(listing.price),
                    "estimated_total_value": _decimal_to_string(estimated_total_value),
                    "status": listing.status,
                    "predicted_date": listing.predicted_date.isoformat() if listing.predicted_date else "",
                }
            )

        fieldnames = [
            "sold_at",
            "market_id",
            "crop",
            "farmer_id",
            "region",
            "district",
            "farming_season",
            "farming_method",
            "quantity",
            "unit",
            "unit_price",
            "estimated_total_value",
            "status",
            "predicted_date",
        ]

        _log_activity(
            user=request.user,
            action_type=ActivityLog.ActionType.TRANSACTIONS_REPORT_GENERATED,
            module="reports",
            message="Generated market transactions report",
            metadata={
                "format": report_format,
                "crop": filters["crop"],
                "start_date": filters["start_date"].isoformat() if filters["start_date"] else None,
                "end_date": filters["end_date"].isoformat() if filters["end_date"] else None,
                "row_count": len(rows),
            },
        )

        if report_format == "pdf":
            return _pdf_response(
                _build_report_filename("market-transactions-report", filters, extension="pdf"),
                fieldnames,
                rows,
                title="Market Transactions Report",
            )

        return _csv_response(
            _build_report_filename("market-transactions-report", filters, extension="csv"),
            fieldnames,
            rows,
        )


class AdminCombinedMarketReportAPI(APIView):
    permission_classes = [IsAdminUser]
    format_kwarg = None

    def get(self, request):
        report_format, format_error = _parse_report_format(request)
        if format_error:
            return format_error

        filters, error_response = _parse_report_filters(request)
        if error_response:
            return error_response

        sold_listings = _apply_marketplace_filters(
            Marketplace.objects.select_related("crop").filter(status="Sold").order_by("created_at", "market_id"),
            filters,
        )
        prediction_rows = _apply_prediction_filters(
            PredictionHistory.objects.filter(prediction_type__in=["price", "price_forecast"]),
            filters,
        ).order_by("created_at", "id")

        combined_by_crop = {}

        for listing in sold_listings:
            crop_name = listing.crop.crop_name if listing.crop_id else "Unknown"
            entry = combined_by_crop.setdefault(
                crop_name,
                {
                    "crop": crop_name,
                    "sold_listing_count": 0,
                    "sold_quantity": 0,
                    "avg_listing_price_sum": Decimal("0.00"),
                    "estimated_total_value": Decimal("0.00"),
                    "latest_sold_at": None,
                    "ml_prediction_count": 0,
                    "ml_predicted_value_sum": 0.0,
                    "latest_ml_prediction_at": None,
                    "latest_ml_predicted_price": None,
                },
            )

            sold_at = listing.created_at
            entry["sold_listing_count"] += 1
            entry["sold_quantity"] += int(listing.quantity or 0)
            entry["avg_listing_price_sum"] += Decimal(listing.price)
            entry["estimated_total_value"] += Decimal(listing.price) * Decimal(listing.quantity)
            if sold_at and (entry["latest_sold_at"] is None or sold_at > entry["latest_sold_at"]):
                entry["latest_sold_at"] = sold_at

        for prediction in prediction_rows:
            crop_name = prediction.crop_name or "Unknown"
            entry = combined_by_crop.setdefault(
                crop_name,
                {
                    "crop": crop_name,
                    "sold_listing_count": 0,
                    "sold_quantity": 0,
                    "avg_listing_price_sum": Decimal("0.00"),
                    "estimated_total_value": Decimal("0.00"),
                    "latest_sold_at": None,
                    "ml_prediction_count": 0,
                    "ml_predicted_value_sum": 0.0,
                    "latest_ml_prediction_at": None,
                    "latest_ml_predicted_price": None,
                },
            )

            entry["ml_prediction_count"] += 1
            entry["ml_predicted_value_sum"] += float(prediction.predicted_value or 0)
            if entry["latest_ml_prediction_at"] is None or prediction.created_at > entry["latest_ml_prediction_at"]:
                entry["latest_ml_prediction_at"] = prediction.created_at
                entry["latest_ml_predicted_price"] = float(prediction.predicted_value or 0)

        rows = []
        for crop_name in sorted(combined_by_crop.keys()):
            entry = combined_by_crop[crop_name]
            sold_listing_count = entry["sold_listing_count"]
            ml_prediction_count = entry["ml_prediction_count"]
            avg_listing_price = (
                entry["avg_listing_price_sum"] / sold_listing_count
                if sold_listing_count
                else None
            )
            ml_avg_predicted_price = (
                entry["ml_predicted_value_sum"] / ml_prediction_count
                if ml_prediction_count
                else None
            )

            latest_sold_at = entry["latest_sold_at"]
            latest_ml_prediction_at = entry["latest_ml_prediction_at"]

            rows.append(
                {
                    "crop": crop_name,
                    "report_start_date": filters["start_date"].isoformat() if filters["start_date"] else "",
                    "report_end_date": filters["end_date"].isoformat() if filters["end_date"] else "",
                    "sold_listing_count": sold_listing_count,
                    "sold_quantity": entry["sold_quantity"],
                    "avg_listing_price": _decimal_to_string(avg_listing_price) if avg_listing_price is not None else "",
                    "estimated_total_value": _decimal_to_string(entry["estimated_total_value"]),
                    "latest_sold_at": latest_sold_at.isoformat() if latest_sold_at else "",
                    "ml_prediction_count": ml_prediction_count,
                    "ml_avg_predicted_price": _float_to_string(ml_avg_predicted_price),
                    "latest_ml_predicted_price": _float_to_string(entry["latest_ml_predicted_price"]),
                    "latest_ml_prediction_at": latest_ml_prediction_at.isoformat() if latest_ml_prediction_at else "",
                }
            )

        fieldnames = [
            "crop",
            "report_start_date",
            "report_end_date",
            "sold_listing_count",
            "sold_quantity",
            "avg_listing_price",
            "estimated_total_value",
            "latest_sold_at",
            "ml_prediction_count",
            "ml_avg_predicted_price",
            "latest_ml_predicted_price",
            "latest_ml_prediction_at",
        ]

        _log_activity(
            user=request.user,
            action_type=ActivityLog.ActionType.COMBINED_REPORT_GENERATED,
            module="reports",
            message="Generated combined market report",
            metadata={
                "format": report_format,
                "crop": filters["crop"],
                "start_date": filters["start_date"].isoformat() if filters["start_date"] else None,
                "end_date": filters["end_date"].isoformat() if filters["end_date"] else None,
                "row_count": len(rows),
            },
        )

        if report_format == "pdf":
            return _pdf_response(
                _build_report_filename("combined-market-report", filters, extension="pdf"),
                fieldnames,
                rows,
                title="Combined Market Report",
            )

        return _csv_response(
            _build_report_filename("combined-market-report", filters, extension="csv"),
            fieldnames,
            rows,
        )


class AdminUserDetailAPI(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, user_id):
        # Frontend currently sends list item `id` from admin lists.
        # Accept both user_id and profile PK to keep the existing button behavior working.
        farmer = FarmerDetails.objects.filter(user_id=user_id).select_related("user").first()
        if not farmer:
            farmer = FarmerDetails.objects.filter(pk=user_id).select_related("user").first()
        if farmer:
            return Response({
                "id": farmer.user_id,
                "profile_id": farmer.id,
                "role": "Farmer",
                "email": farmer.user.email,
                "username": farmer.user.username,
                "fullname": farmer.fullname,
                "contact_number": farmer.contact_number,
                "region": farmer.region,
                "farm_name": farmer.farm_name,
                "address": farmer.address,
                "about": farmer.about,
                "profile_image": farmer.profile_image,
                "is_active": farmer.is_active,
                "is_verified": getattr(farmer.user, 'is_active', True), # Wait, verified usually tied to something else, checking soon
            })

        buyer = BuyerDetails.objects.filter(user_id=user_id).select_related("user").first()
        if not buyer:
            buyer = BuyerDetails.objects.filter(pk=user_id).select_related("user").first()
        if buyer:
            return Response({
                "id": buyer.user_id,
                "profile_id": buyer.id,
                "role": "Buyer",
                "email": buyer.user.email,
                "username": buyer.user.username,
                "fullname": buyer.fullname,
                "contact_number": buyer.contact_number,
                "company_name": buyer.company_name,
                "company_email": buyer.company_email,
                "company_phone": buyer.company_phone,
                "address": buyer.address,
                "city": buyer.city,
                "profile_image": buyer.profile_image,
                "is_active": buyer.is_active,
                "is_verified": getattr(buyer.user, 'is_active', True),
            })

        return Response({"error": "Profile not found"}, status=404)

    def put(self, request, user_id):
        is_active = _to_bool(request.data.get("is_active"))
        is_verified = _to_bool(request.data.get("is_verified"))
        
        user = User.objects.filter(id=user_id).first()
        if not user:
            # Maybe the user_id passed was a profile ID.
            farmer = FarmerDetails.objects.filter(pk=user_id).select_related("user").first()
            if farmer:
                user = farmer.user
            else:
                buyer = BuyerDetails.objects.filter(pk=user_id).select_related("user").first()
                if buyer:
                    user = buyer.user

        if not user:
            return Response({"error": "User not found"}, status=404)

        changed = False

        if is_active is not None:
            # Update Farmer or Buyer profile is_active
            farmer = FarmerDetails.objects.filter(user=user).first()
            if farmer:
                farmer.is_active = is_active
                farmer.save()
            
            buyer = BuyerDetails.objects.filter(user=user).first()
            if buyer:
                buyer.is_active = is_active
                buyer.save()
            changed = True

        if is_verified is not None:
            # We assume user is_active acts as verification/active. We update user.
            user.is_active = is_verified
            user.save()
            changed = True
            
        if changed:
            # Log the change
            try:
                action_text = "Verified" if (is_verified or is_active) else "Disabled"
                _log_activity(
                    user=request.user,
                    action_type="USER_STATUS_UPDATE",
                    module="User Management",
                    message=f"{action_text} account for {user.username} ({user.email})"
                )
            except Exception as e:
                pass
            return Response({"message": "User status updated successfully", "is_active": is_active, "is_verified": is_verified})
        else:
            return Response({"error": "No valid fields provided to update"}, status=400)


class AdminActivityLogAPI(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        limit_value = request.query_params.get("limit", "50")

        try:
            limit = int(limit_value)
        except (TypeError, ValueError):
            return Response({"error": "limit must be an integer"}, status=400)

        if limit < 1 or limit > 100:
            return Response({"error": "limit must be between 1 and 100"}, status=400)

        queryset = ActivityLog.objects.select_related("actor").all()[:limit]
        serializer = ActivityLogSerializer(queryset, many=True)
        return Response(
            {
                "results": serializer.data,
                "count": len(serializer.data),
            },
            status=status.HTTP_200_OK,
        )


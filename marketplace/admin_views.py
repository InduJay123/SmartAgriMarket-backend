from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework import status
from django.db.models import Sum, Count, Case, When, IntegerField, Value, Q
from django.db.models.functions import Coalesce

from .models import Marketplace


class AdminCropOverviewAPI(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        # Optional filters (useful for dashboard)
        status_filter = request.query_params.get("status")  # Available/Sold/Pending
        qs = Marketplace.objects.select_related("crop")

        if status_filter:
            qs = qs.filter(status=status_filter)

        # ---- 1) Per-crop totals + season split + farmer count ----
        crop_rows = (
            qs.values("crop_id", "crop__crop_name")
            .annotate(
                total_quantity=Coalesce(Sum("quantity"), Value(0)),
                yala_quantity=Coalesce(
                    Sum(
                        Case(
                            When(farming_season__iexact="Yala", then="quantity"),
                            default=Value(0),
                            output_field=IntegerField(),
                        )
                    ),
                    Value(0),
                ),
                maha_quantity=Coalesce(
                    Sum(
                        Case(
                            When(farming_season__iexact="Maha", then="quantity"),
                            default=Value(0),
                            output_field=IntegerField(),
                        )
                    ),
                    Value(0),
                ),
                farmers_count=Count("farmer_id", distinct=True),
            )
            .order_by("crop__crop_name")
        )

        # ---- 2) Region breakdown per crop (counts + total quantity per region) ----
        region_rows = (
            qs.values("crop_id", "region")
            .annotate(
                farmers_count=Count("farmer_id", distinct=True),
                total_quantity=Coalesce(Sum("quantity"), Value(0)),
            )
            .order_by("crop_id", "region")
        )

        # Assemble region_rows into a dict: {crop_id: [ {region,...}, ... ]}
        region_map = {}
        for r in region_rows:
            region_map.setdefault(r["crop_id"], []).append(
                {
                    "region": r["region"] or "Unknown",
                    "farmers_count": r["farmers_count"],
                    "total_quantity": r["total_quantity"],
                }
            )

        # Final payload
        result = []
        for row in crop_rows:
            crop_id = row["crop_id"]
            result.append(
                {
                    "crop_id": crop_id,
                    "crop_name": row["crop__crop_name"],
                    "total_quantity": row["total_quantity"],
                    "season_split": {
                        "Yala": row["yala_quantity"],
                        "Maha": row["maha_quantity"],
                    },
                    "farmers_count": row["farmers_count"],
                    "regions": region_map.get(crop_id, []),
                }
            )

        return Response(result, status=status.HTTP_200_OK)
import csv
import os
from datetime import datetime
from openpyxl import load_workbook

from rest_framework import generics, permissions, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response

from .models import PriceUpload, CropPrice
from .serializers import PriceUploadSerializer


class IsAdminOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser)


class PriceUploadListCreateAPI(generics.ListCreateAPIView):
    queryset = PriceUpload.objects.all().order_by("-created_at")
    serializer_class = PriceUploadSerializer
    permission_classes = [IsAdminOnly]
    parser_classes = [MultiPartParser, FormParser]

    def create(self, request, *args, **kwargs):
        file = request.FILES.get("file")
        if not file:
            return Response({"detail": "file is required"}, status=status.HTTP_400_BAD_REQUEST)

        upload = PriceUpload.objects.create(
            file=file,
            original_name=file.name,
            uploaded_by=request.user,
            status="PENDING",
        )

        try:
            rows = self._parse_and_save(upload)
            upload.status = "PROCESSED"
            upload.processed_rows = rows
            upload.save()
        except Exception as e:
            upload.status = "FAILED"
            upload.error_message = str(e)
            upload.save()

        serializer = self.get_serializer(upload, context={"request": request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def _parse_and_save(self, upload: PriceUpload) -> int:
        """
        Expected columns (recommended):
        crop_name, date, price, unit, market

        date format: YYYY-MM-DD
        """
        path = upload.file.path
        ext = os.path.splitext(path)[1].lower()

        data_rows = []

        if ext == ".csv":
            with open(path, "r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                for r in reader:
                    data_rows.append(r)

        elif ext in [".xlsx", ".xlsm"]:
            wb = load_workbook(path)
            ws = wb.active
            headers = [str(cell.value).strip() for cell in next(ws.iter_rows(min_row=1, max_row=1))]
            for row in ws.iter_rows(min_row=2, values_only=True):
                r = {headers[i]: row[i] for i in range(len(headers))}
                data_rows.append(r)

        else:
            raise Exception("Only CSV and Excel files are supported")

        created = 0
        for r in data_rows:
            crop_name = (r.get("crop_name") or r.get("Crop Name") or r.get("crop") or "").strip()
            date_raw = r.get("date") or r.get("Date")
            price_raw = r.get("price") or r.get("Price")
            unit = r.get("unit") or r.get("Unit")
            market = r.get("market") or r.get("Market")

            if not crop_name or not date_raw or price_raw in [None, ""]:
                continue

            # date parsing
            if isinstance(date_raw, datetime):
                date_val = date_raw.date()
            else:
                date_val = datetime.strptime(str(date_raw).strip(), "%Y-%m-%d").date()

            price_val = float(str(price_raw).strip())

            CropPrice.objects.create(
                crop_name=crop_name,
                date=date_val,
                price=price_val,
                unit=str(unit).strip() if unit else None,
                market=str(market).strip() if market else None,
                upload=upload,
            )
            created += 1

        return created

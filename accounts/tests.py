from django.contrib.auth.models import User
from datetime import date, timedelta
import csv
from io import StringIO

from django.db import connection
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase, APITransactionTestCase

from accounts.models import ActivityLog, BuyerDetails, FarmerDetails
from crops.models import Crop
from marketplace.models import Marketplace
from ml_api.models import PredictionHistory
from prices.models import CropPrice, PriceUpload


class AdminDashboardStatsAPITests(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="admin_user",
            email="admin@example.com",
            password="StrongPass123!",
            is_staff=True,
        )

        farmer_active_user = User.objects.create_user(
            username="farmer_active",
            email="farmer.active@example.com",
            password="StrongPass123!",
        )
        FarmerDetails.objects.create(
            user=farmer_active_user,
            fullname="Farmer Active",
            is_active=True,
        )

        farmer_inactive_user = User.objects.create_user(
            username="farmer_inactive",
            email="farmer.inactive@example.com",
            password="StrongPass123!",
        )
        FarmerDetails.objects.create(
            user=farmer_inactive_user,
            fullname="Farmer Inactive",
            is_active=False,
        )

        buyer_user = User.objects.create_user(
            username="buyer_1",
            email="buyer1@example.com",
            password="StrongPass123!",
        )
        BuyerDetails.objects.create(
            user=buyer_user,
            fullname="Buyer One",
            is_active=True,
        )

        Crop.objects.create(crop_name="Tomato", category="Vegetable")
        Crop.objects.create(crop_name="Carrot", category="Vegetable")

    def _admin_access_token(self):
        response = self.client.post(
            "/api/auth/admin/login/",
            {"username": "admin_user", "password": "StrongPass123!"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response.data["access"]

    def test_dashboard_stats_requires_auth(self):
        response = self.client.get("/api/auth/admin/dashboard-stats/")
        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )

    def test_dashboard_stats_returns_expected_counts_for_admin(self):
        token = self._admin_access_token()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = self.client.get("/api/auth/admin/dashboard-stats/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["verified_farmers"], 1)
        self.assertEqual(response.data["pending_approvals"], 1)
        self.assertEqual(response.data["buyers"], 1)
        self.assertEqual(response.data["crops"], 2)
        self.assertEqual(response.data["total_farmers"], 2)


class AdminPendingVerificationFlowTests(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="admin_user_2",
            email="admin2@example.com",
            password="StrongPass123!",
            is_staff=True,
        )

        self.pending_farmer_user = User.objects.create_user(
            username="pending_farmer",
            email="pending.farmer@example.com",
            password="StrongPass123!",
            is_active=True,
        )
        self.pending_farmer_profile = FarmerDetails.objects.create(
            user=self.pending_farmer_user,
            fullname="Pending Farmer",
            is_active=False,
        )

        login = self.client.post(
            "/api/auth/admin/login/",
            {"username": "admin_user_2", "password": "StrongPass123!"},
            format="json",
        )
        self.assertEqual(login.status_code, status.HTTP_200_OK)
        token = login.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_rejected_farmer_disappears_from_pending_list(self):
        pending_before = self.client.get("/api/auth/admin/farmers/?status=pending")
        self.assertEqual(pending_before.status_code, status.HTTP_200_OK)
        self.assertEqual(len(pending_before.data), 1)

        reject = self.client.patch(
            "/api/auth/admin/verify/",
            {
                "role": "Farmer",
                "user_id": self.pending_farmer_user.id,
                "is_active": "false",
            },
            format="json",
        )
        self.assertEqual(reject.status_code, status.HTTP_200_OK)

        self.pending_farmer_profile.refresh_from_db()
        self.pending_farmer_user.refresh_from_db()
        self.assertFalse(self.pending_farmer_profile.is_active)
        self.assertFalse(self.pending_farmer_user.is_active)

        pending_after = self.client.get("/api/auth/admin/farmers/?status=pending")
        self.assertEqual(pending_after.status_code, status.HTTP_200_OK)
        self.assertEqual(len(pending_after.data), 0)

    def test_user_detail_works_with_list_item_id(self):
        pending = self.client.get("/api/auth/admin/farmers/?status=pending")
        self.assertEqual(pending.status_code, status.HTTP_200_OK)
        self.assertEqual(len(pending.data), 1)

        # Frontend uses list item `id` for the View button.
        list_item_id = pending.data[0]["id"]

        detail = self.client.get(f"/api/auth/admin/user/{list_item_id}/")
        self.assertEqual(detail.status_code, status.HTTP_200_OK)
        self.assertEqual(detail.data["id"], self.pending_farmer_user.id)
        self.assertEqual(detail.data["profile_id"], self.pending_farmer_profile.id)


class AdminDashboardChartsAPITests(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="charts_admin",
            email="charts.admin@example.com",
            password="StrongPass123!",
            is_staff=True,
        )

        self.upload = PriceUpload.objects.create(
            original_name="prices.csv",
            uploaded_by=self.admin_user,
            status="PROCESSED",
            processed_rows=2,
            file="price_uploads/test_prices.csv",
        )

        today = date.today()
        current_month_date = date(today.year, today.month, 1)

        previous_month = today.month - 1 if today.month > 1 else 12
        previous_year = today.year if today.month > 1 else today.year - 1
        previous_month_date = date(previous_year, previous_month, 1)

        CropPrice.objects.create(
            crop_name="Tomato",
            date=current_month_date,
            price=150.00,
            market="Dambulla",
            unit="kg",
            upload=self.upload,
        )

        CropPrice.objects.create(
            crop_name="Tomato",
            date=previous_month_date,
            price=120.00,
            market="Dambulla",
            unit="kg",
            upload=self.upload,
        )

    def _set_admin_token(self):
        login = self.client.post(
            "/api/auth/admin/login/",
            {"username": "charts_admin", "password": "StrongPass123!"},
            format="json",
        )
        self.assertEqual(login.status_code, status.HTTP_200_OK)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")

    def test_dashboard_charts_requires_auth(self):
        response = self.client.get("/api/auth/admin/dashboard-charts/")
        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )

    def test_dashboard_charts_returns_realtime_series_contract(self):
        self._set_admin_token()

        response = self.client.get("/api/auth/admin/dashboard-charts/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn("price_trend", response.data)
        self.assertIn("supply_by_crop", response.data)

        self.assertIn("labels", response.data["price_trend"])
        self.assertIn("values", response.data["price_trend"])
        self.assertEqual(len(response.data["price_trend"]["labels"]), 6)
        self.assertEqual(len(response.data["price_trend"]["values"]), 6)

        # Two inserted monthly values should appear in the rolling 6-month series.
        self.assertIn(150.0, response.data["price_trend"]["values"])
        self.assertIn(120.0, response.data["price_trend"]["values"])

        self.assertIn("labels", response.data["supply_by_crop"])
        self.assertIn("values", response.data["supply_by_crop"])


class AdminActivityLogAPITests(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="activity_admin",
            email="activity.admin@example.com",
            password="StrongPass123!",
            is_staff=True,
        )

        self.pending_farmer_user = User.objects.create_user(
            username="activity_farmer",
            email="activity.farmer@example.com",
            password="StrongPass123!",
            is_active=True,
        )
        self.pending_farmer_profile = FarmerDetails.objects.create(
            user=self.pending_farmer_user,
            fullname="Activity Farmer",
            is_active=False,
        )

    def _admin_login(self):
        return self.client.post(
            "/api/auth/admin/login/",
            {"username": "activity_admin", "password": "StrongPass123!"},
            format="json",
        )

    def _set_admin_token(self):
        response = self._admin_login()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")
        return response

    def test_activity_logs_requires_admin_auth(self):
        response = self.client.get("/api/auth/admin/activity-logs/")
        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )

    def test_activity_logs_return_latest_entries(self):
        self._set_admin_token()

        dashboard_response = self.client.get("/api/auth/admin/dashboard-stats/")
        self.assertEqual(dashboard_response.status_code, status.HTTP_200_OK)

        verify_response = self.client.patch(
            "/api/auth/admin/verify/",
            {
                "role": "Farmer",
                "user_id": self.pending_farmer_user.id,
                "is_active": True,
            },
            format="json",
        )
        self.assertEqual(verify_response.status_code, status.HTTP_200_OK)

        response = self.client.get("/api/auth/admin/activity-logs/?limit=10")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data["count"], 3)
        self.assertEqual(response.data["results"][0]["action_type"], ActivityLog.ActionType.USER_APPROVED)
        self.assertEqual(response.data["results"][0]["user"], "activity_admin")

        action_types = [item["action_type"] for item in response.data["results"]]
        self.assertIn(ActivityLog.ActionType.ADMIN_LOGIN_SUCCESS, action_types)
        self.assertIn(ActivityLog.ActionType.DASHBOARD_VIEWED, action_types)

    def test_activity_logs_limit_validation(self):
        self._set_admin_token()

        response = self.client.get("/api/auth/admin/activity-logs/?limit=500")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "limit must be between 1 and 100")


class AdminCropDetailsAPITests(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="crop_admin",
            email="crop.admin@example.com",
            password="StrongPass123!",
            is_staff=True,
        )
        self.non_admin_user = User.objects.create_user(
            username="crop_user",
            email="crop.user@example.com",
            password="StrongPass123!",
        )

        self.crop = Crop.objects.create(
            crop_name="Beans",
            description="Green beans",
            category="Vegetable",
            image="https://example.com/beans.jpg",
        )

        now = timezone.now()
        Marketplace.objects.create(
            farmer_id=201,
            crop_id=self.crop.crop_id,
            price="120.50",
            unit="kg",
            predicted_date=now.date() + timedelta(days=4),
            quantity=15,
            farming_method="Organic",
            farming_season="Yala",
            additional_details="Batch A",
            region="Western",
            district="Colombo",
            image="https://example.com/listing-a.jpg",
            status="Available",
            created_at=now - timedelta(days=2),
            updated_at=now - timedelta(days=2),
        )
        Marketplace.objects.create(
            farmer_id=202,
            crop_id=self.crop.crop_id,
            price="150.00",
            unit="kg",
            predicted_date=now.date() + timedelta(days=6),
            quantity=10,
            farming_method="Conventional",
            farming_season="Maha",
            additional_details=None,
            region="Southern",
            district="Galle",
            image=None,
            status="Available",
            created_at=now - timedelta(days=1),
            updated_at=now - timedelta(days=1),
        )
        Marketplace.objects.create(
            farmer_id=203,
            crop_id=self.crop.crop_id,
            price="300.00",
            unit="kg",
            predicted_date=now.date() + timedelta(days=8),
            quantity=7,
            farming_method="Organic",
            farming_season="Yala",
            additional_details="Sold batch",
            region="Uva",
            district="Badulla",
            image="https://example.com/listing-c.jpg",
            status="Sold",
            created_at=now,
            updated_at=now,
        )

    def test_crop_details_requires_auth(self):
        response = self.client.get(f"/api/auth/admin/crops/{self.crop.crop_id}/details/")
        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )

    def test_crop_details_forbids_non_admin(self):
        self.client.force_authenticate(user=self.non_admin_user)

        response = self.client.get(f"/api/auth/admin/crops/{self.crop.crop_id}/details/")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_crop_details_returns_available_listings_and_summary(self):
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.get(f"/api/auth/admin/crops/{self.crop.crop_id}/details/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("crop", response.data)
        self.assertIn("listings", response.data)
        self.assertIn("summary", response.data)

        self.assertEqual(response.data["crop"]["crop_id"], self.crop.crop_id)
        self.assertEqual(response.data["crop"]["crop_name"], "Beans")

        listings = response.data["listings"]
        self.assertEqual(len(listings), 2)

        required_listing_fields = {
            "market_id",
            "farmer_id",
            "crop_id",
            "quantity",
            "farming_season",
            "price",
            "unit",
            "predicted_date",
            "status",
            "created_at",
            "updated_at",
            "farming_method",
            "additional_details",
            "region",
            "district",
            "image",
        }
        self.assertTrue(required_listing_fields.issubset(set(listings[0].keys())))
        self.assertTrue(all(item["status"] == "Available" for item in listings))

        summary = response.data["summary"]
        self.assertEqual(summary["total_quantity"], 25)
        self.assertEqual(summary["active_count"], 2)
        self.assertEqual(float(summary["min_price"]), 120.5)
        self.assertEqual(float(summary["max_price"]), 150.0)

    def test_crop_details_not_found(self):
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.get("/api/auth/admin/crops/999999/details/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error"], "Crop not found")


class AdminReportsAPITests(APITransactionTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._ensure_market_table()

    @classmethod
    def _ensure_market_table(cls):
        table_name = Marketplace._meta.db_table
        required_columns = {
            "market_id",
            "farmer_id",
            "crop_id",
            "price",
            "quantity",
            "status",
            "created_at",
            "updated_at",
        }

        with connection.cursor() as cursor:
            table_names = connection.introspection.table_names(cursor)
            recreate_table = table_name not in table_names

            if not recreate_table:
                existing_columns = {
                    column.name
                    for column in connection.introspection.get_table_description(cursor, table_name)
                }
                recreate_table = not required_columns.issubset(existing_columns)

        if not recreate_table:
            return

        with connection.cursor() as cursor:
            if connection.vendor == "mysql":
                cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
                cursor.execute(f"DROP TABLE IF EXISTS `{table_name}`")
                cursor.execute(
                    f"""
                    CREATE TABLE `{table_name}` (
                        `market_id` integer AUTO_INCREMENT PRIMARY KEY,
                        `farmer_id` integer NOT NULL,
                        `crop_id` bigint NOT NULL,
                        `price` decimal(10, 2) NOT NULL,
                        `unit` varchar(20) NOT NULL,
                        `predicted_date` date NOT NULL,
                        `quantity` integer NOT NULL,
                        `additional_details` varchar(255) NULL,
                        `farming_method` varchar(100) NOT NULL,
                        `farming_season` varchar(100) NOT NULL,
                        `region` varchar(255) NOT NULL,
                        `district` varchar(255) NOT NULL,
                        `image` longtext NULL,
                        `status` varchar(20) NOT NULL,
                        `created_at` datetime(6) NOT NULL,
                        `updated_at` datetime(6) NOT NULL
                    )
                    """
                )
                cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
                return

            cursor.execute(f'DROP TABLE IF EXISTS "{table_name}"')
            cursor.execute(
                f'''
                CREATE TABLE "{table_name}" (
                    "market_id" integer PRIMARY KEY AUTOINCREMENT,
                    "farmer_id" integer NOT NULL,
                    "crop_id" bigint NOT NULL,
                    "price" decimal(10, 2) NOT NULL,
                    "unit" varchar(20) NOT NULL,
                    "predicted_date" date NOT NULL,
                    "quantity" integer NOT NULL,
                    "additional_details" varchar(255) NULL,
                    "farming_method" varchar(100) NOT NULL,
                    "farming_season" varchar(100) NOT NULL,
                    "region" varchar(255) NOT NULL,
                    "district" varchar(255) NOT NULL,
                    "image" text NULL,
                    "status" varchar(20) NOT NULL,
                    "created_at" datetime NOT NULL,
                    "updated_at" datetime NOT NULL
                )
                '''
            )

    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="reports_admin",
            email="reports.admin@example.com",
            password="StrongPass123!",
            is_staff=True,
        )
        self.standard_user = User.objects.create_user(
            username="regular_user",
            email="regular@example.com",
            password="StrongPass123!",
        )

        self.tomato = Crop.objects.create(crop_name="Tomato", category="Vegetable")
        self.carrot = Crop.objects.create(crop_name="Carrot", category="Vegetable")

        now = timezone.now()
        Marketplace.objects.create(
            farmer_id=101,
            crop_id=self.tomato.pk,
            price="250.00",
            unit="kg",
            predicted_date=now.date(),
            quantity=10,
            additional_details="First sold listing",
            farming_method="Organic",
            farming_season="Yala",
            region="Northern",
            district="Jaffna",
            status="Sold",
            created_at=now - timedelta(days=2),
            updated_at=now - timedelta(days=2),
        )
        Marketplace.objects.create(
            farmer_id=102,
            crop_id=self.carrot.pk,
            price="180.00",
            unit="kg",
            predicted_date=now.date(),
            quantity=4,
            additional_details="Unsold listing",
            farming_method="Conventional",
            farming_season="Maha",
            region="Central",
            district="Kandy",
            status="Available",
            created_at=now - timedelta(days=1),
            updated_at=now - timedelta(days=1),
        )

        PredictionHistory.objects.create(
            prediction_type="price",
            crop_name="Tomato",
            input_features={"source": "unit-test"},
            predicted_value=265.5,
            confidence=0.81,
        )
        PredictionHistory.objects.create(
            prediction_type="price",
            crop_name="Carrot",
            input_features={"source": "unit-test"},
            predicted_value=190.0,
            confidence=0.72,
        )

    def _admin_access_token(self):
        response = self.client.post(
            "/api/auth/admin/login/",
            {"username": "reports_admin", "password": "StrongPass123!"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response.data["access"]

    def _parse_csv(self, response):
        return list(csv.DictReader(StringIO(response.content.decode("utf-8"))))

    def test_transactions_report_requires_admin_auth(self):
        response = self.client.get("/api/auth/admin/reports/transactions/")
        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )

    def test_transactions_report_forbids_authenticated_non_admin_user(self):
        self.client.force_authenticate(user=self.standard_user)

        response = self.client.get("/api/auth/admin/reports/transactions/")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_transactions_report_returns_filtered_csv(self):
        token = self._admin_access_token()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        today = timezone.localdate().isoformat()
        start = (timezone.localdate() - timedelta(days=5)).isoformat()
        response = self.client.get(
            f"/api/auth/admin/reports/transactions/?startDate={start}&endDate={today}"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Content-Type"], "text/csv")
        self.assertIn("attachment; filename=", response["Content-Disposition"])

        body = response.content.decode("utf-8")
        self.assertIn("sold_at,market_id,crop,farmer_id,region,district", body)
        self.assertIn("estimated_total_value", body)

    def test_transactions_report_returns_pdf_when_requested(self):
        token = self._admin_access_token()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        today = timezone.localdate().isoformat()
        start = (timezone.localdate() - timedelta(days=5)).isoformat()
        response = self.client.get(
            f"/api/auth/admin/reports/transactions/?startDate={start}&endDate={today}&format=pdf"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertIn("attachment; filename=", response["Content-Disposition"])
        self.assertIn(".pdf", response["Content-Disposition"])
        self.assertTrue(response.content.startswith(b"%PDF-"))

    def test_transactions_report_rejects_invalid_date_range(self):
        token = self._admin_access_token()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = self.client.get(
            "/api/auth/admin/reports/transactions/?startDate=2026-03-15&endDate=2026-03-01"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["error"],
            "Start date must be earlier than or equal to the end date.",
        )

    def test_combined_market_report_returns_joined_csv(self):
        token = self._admin_access_token()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        today = timezone.localdate().isoformat()
        start = (timezone.localdate() - timedelta(days=5)).isoformat()
        response = self.client.get(
            f"/api/auth/admin/reports/combined-market/?startDate={start}&endDate={today}"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Content-Type"], "text/csv")

        body = response.content.decode("utf-8")
        self.assertIn("crop,report_start_date,report_end_date,sold_listing_count", body)
        self.assertIn("ml_avg_predicted_price", body)
        self.assertIn("latest_ml_prediction_at", body)

    def test_combined_market_report_rejects_unsupported_format(self):
        token = self._admin_access_token()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = self.client.get("/api/auth/admin/reports/combined-market/?format=xlsx")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "Unsupported format")


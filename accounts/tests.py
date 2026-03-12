from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import BuyerDetails, FarmerDetails
from crops.models import Crop


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

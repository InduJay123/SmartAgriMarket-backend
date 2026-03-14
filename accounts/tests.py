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

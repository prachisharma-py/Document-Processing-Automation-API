from rest_framework import status
from rest_framework.test import APITestCase

from .models import User

# Create your tests here.


class AuthenticationTests(APITestCase):
    def setUp(self):
        self.user_data = {
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "password": "TestPassword123",
        }

        self.user = User.objects.create_user(
            **self.user_data
        )


    def test_register_user(self):
        response = self.client.post(
            "/api/v1/auth/register/",
            {
                "email": "newuser@example.com",
                "first_name": "New",
                "last_name": "User",
                "password": "NewPassword123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data["email"],
            "newuser@example.com",
        )

        user = User.objects.get(email="newuser@example.com")

        self.assertTrue(
            user.check_password("NewPassword123")
        )


    def test_register_duplicate_email(self):
        response = self.client.post(
            "/api/v1/auth/register/",
            self.user_data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )


    def test_login(self):
        response = self.client.post(
            "/api/v1/auth/login/",
            {
                "email": "test@example.com",
                "password": "TestPassword123",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)


    def test_me_authenticated(self):
        response = self.client.post(
            "/api/v1/auth/login/",
            {
                "email": "test@example.com",
                "password": "TestPassword123",
            },
            format="json",
        )

        access_token = response.data["access"]

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {access_token}"
        )

        response = self.client.get("/api/v1/auth/me/")

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["email"],
            "test@example.com",
        )


    def test_me_unauthenticated(self):
        response = self.client.get("/api/v1/auth/me/")

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

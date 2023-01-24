from django.test import TestCase
from django.urls import reverse
from decimal import Decimal
from main import models
from unittest.mock import patch
from django.contrib import auth
from main import forms

# Create your tests here.
class TestPage(TestCase):
    def test_home_page_works(self) -> None:
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home.html")
        self.assertContains(response, 'BookTime')

    def test_about_us_page_works(self) -> None:
        response = self.client.get(reverse("about_us"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "about_us.html")
        self.assertContains(response, "BookTime")

    def test_products_page_returns_active(self) -> None:
        models.Product.object.create(
            name = "The cathedral",
            price = Decimal("10.00"),
            slug = "cathedral"
        )
        models.Product.object.create(
            name = "The Ring",
            price = Decimal("5.00"),
            slug = "the-ring",
            active = False
        )
        response = self.client.get(
            reverse("products", kwargs={"tag": "all"})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "BookTime")

        product_list = models.Product.object.active().order_by("name")
        
        self.assertEqual(
            list(response.context["object_list"]),
            list(product_list),
        )

    def test_products_page_filters_by_tags_and_active(self) -> None:
        cb = models.Product.object.create(
            name = "The cathedral",
            price = Decimal("10.00"),
            slug = "cathedral"
        )
        cb.tags.create(name = "Open source", slug = "opensource")
        models.Product.object.create(
            name = "Microsoft Windows guide",
            price = Decimal("12.00"),
            slug = "microsoft-windows-guide"
        )
        response = self.client.get(
            reverse("products", kwargs={"tag": "opensource"})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "BookTime")

        product_list = (
            models.Product.object.active()
            .filter(tags__slug="opensource")
            .order_by("name")
        )

        self.assertEqual(
            list(response.context["object_list"]),
            list(product_list),
        )

    def test_user_signup_page_loads_correctly(self):
        response = self.client.get(reverse("signup"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "signup.html")
        self.assertContains(response, "BookTime")
        self.assertIsInstance(
            response.context["form"], forms.UserCreationForm
        )

    def test_user_signup_page_submission_works(self):
        post_data = {
            "email": "user@domain.com",
            "password1": "compl3xP@ssw0rd",
            "password2": "compl3xP@ssw0rd",
        }
        with patch.object(
            forms.UserCreationForm, "send_mail") as mock_send:
            response = self.client.post(
                reverse("signup"), post_data
            )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            models.User.object.filter(
                email="user@domain.com").exists()
        )
        self.assertTrue(
            auth.get_user(self.client).is_authenticated
        )
        mock_send.assert_called_once()
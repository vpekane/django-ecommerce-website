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

    def test_address_list_page_returns_only_owned(self):
        user1 = models.User.object.create_user(
            "user1", "Compl3xp@ssw0rd"
        )
        user2 = models.User.object.create_user(
            "user2", "Compl3xP@ssw0rd"
        )

        models.Address.objects.create(
            user=user1,
            name="Bruce Wayne",
            address1="Wayne Manor",
            address2="Batcave",
            city="Gotham",
            country="us",
        )

        models.Address.objects.create(
            user=user2,
            name="Marc Kimball",
            address1="123 Deacon Road",
            city="London",
            country="uk",
        )

        self.client.force_login(user1)
        response = self.client.get(reverse("address_list"))
        self.assertEqual(response.status_code, 200)

        address_list = models.Address.objects.filter(user=user1)
        self.assertEqual(
            list(response.context["object_list"]),
            list(address_list)
        )

    def test_address_create_stores_user(self):
        user1 = models.User.object.create_user(
            "user1", "C0mpl3xP@ssw0rd"
        )
        post_data = {
            "name": "John Kercher",
            "address1": "1 av Street",
            "address2": "",
            "zip_code": "MA12GS",
            "city": "Manchester",
            "country": "uk",
        }
        self.client.force_login(user1)
        self.client.post(reverse("address_create"), post_data)

        self.assertTrue(models.Address.objects.filter(user=user1).exists())

    def test_add_to_basket_loggedin_works(self):
        user1 = models.User.object.create_user(
            "user1", "Compl3xP@ssw0rd"
        )
        cb = models.Product.object.create(
            name="The cathedral and the bazaar",
            slug="cathedral-bazaar",
            price=Decimal("10.00"),
        )
        w = models.Product.object.create(
            name="Microsoft Windows guide",
            slug="microsoft-windows-guide",
            price=Decimal("12.00")
        )
        self.client.force_login(user1)
        response = self.client.get(
            reverse("add_to_basket"), {"product_id": cb.id}
        )

        self.assertTrue(
            models.Basket.objects.filter(user=user1).exists()
        )

        self.assertEqual(
            models.BasketLine.objects.all().count(), 1
        )

        response = self.client.get(
            reverse("add_to_basket"), {"product_id": w.id}
        )
        self.assertEqual(
            models.BasketLine.objects.all().count(), 2
        )
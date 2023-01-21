from django.test import TestCase
from django.urls import reverse
from decimal import Decimal
from main import models

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


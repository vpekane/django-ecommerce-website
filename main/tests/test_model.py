from decimal import Decimal
from django.test import TestCase
from main import models

class TestModel(TestCase):
    def test_active_manager_works(self) -> None:
        models.Product.object.create(
            name="The cathedral",
            price=Decimal("10.00"),
        )
        models.Product.object.create(
            name="Pride and Prejudice",
            price=Decimal("2.00")
        )
        models.Product.object.create(
            name="A Tale of Two Cities",
            price=Decimal("2.00"),
            active=False
        )

        self.assertEqual(len(models.Product.object.active()), 2)

    def test_create_user_manager_works(self):
        models.User.object.create_user(
            "user1@domain.com", "C0mpl3xP@ssw0rd",
        )

        self.assertTrue(models.User.object.filter(email='user1@domain.com').exists())
    
    def test_create_superuser_manager_works(self):
        models.User.object.create_superuser(
            "user1@domain.com", "C0mpl3xP@ssw0rd",
        )

        self.assertTrue(models.User.object.filter(email='user1@domain.com').exists())
        self.assertEqual(models.User.object.filter(is_superuser='t').count(), 1)

    def test_product_tag_manager_works(self):
        models.ProductTag.object.create(
            name="The Book",
            slug="the-book",
        )

        self.assertEqual(models.ProductTag.object.filter(slug='the-book').count(), 1)
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

    def test_create_order_works(self):
        product1 = models.Product.object.create(
            name="The cathedral and bazaar",
            price=Decimal("10.00")
        )

        product2 = models.Product.object.create(
            name="The girl with the dragon tattoo",
            price=Decimal("20.00")
        )

        user1 = models.User.object.create_user(
            "user1@domain.com", "C0mpl3xP@ssw0rd"
        )

        billing_address = models.Address.objects.create(
            user=user1,
            name="John Doe",
            address1="127 Strudel Road",
            city="London",
            zip_code="1287",
            country="uk",
        )

        shipping_address = models.Address.objects.create(
            user=user1,
            name="John Doe",
            address1="123 Deacon Road",
            city="London",
            zip_code="3256",
            country="uk",
        )

        basket = models.Basket.objects.create(user=user1)
        models.BasketLine.objects.create(
            basket=basket, product=product1
        )
        models.BasketLine.objects.create(
            basket=basket, product=product2
        )
        with self.assertLogs("main.models", level="INFO") as cm:
            order = basket.create_order(billing_address, shipping_address)

        self.assertGreaterEqual(len(cm.output), 1)

        order.refresh_from_db()

        self.assertEqual(order.user, user1)
        self.assertEquals(
            order.billing_address1, "127 Strudel Road"
        )
        self.assertEquals(
            order.shipping_address1, "123 Deacon Road"
        )
        self.assertEquals(
            order.billing_city, "London"
        )
        self.assertEquals(
            order.billing_country, "uk"
        )
        self.assertEquals(
            order.billing_name, "John Doe"
        )
        self.assertEquals(
            order.shipping_name, "John Doe"
        )

        self.assertEquals(order.lines.all().count(), 2)
        lines = order.lines.all()
        self.assertEquals(lines[0].product, product1)
        self.assertEquals(lines[1].product, product2)
from decimal import Decimal
from django.test import TestCase
from main import models

class TestModel(TestCase):
    def test_active_manager_works(self) -> None:
        models.Product.object.create(
            name = "The cathedral",
            price = Decimal("10.00"),
        )
        models.Product.object.create(
            name = "Pride and Prejudice",
            price = Decimal("2.00")
        )
        models.Product.object.create(
            name = "A Tale of Two Cities",
            price = Decimal("2.00"),
            active = False
        )

        self.assertEqual(len(models.Product.object.active()), 2)

    # def test_product_tag_manager_works(self):
    #     prod = models.ProductTag.object.create(
    #         name = "The Book",
    #     )

    #     p = models.ProductTag.object.get_by_natural_key("the-book")

    #     print(p)

    #     # self.assertEqual(models.Product.object.get("the-book"), "")

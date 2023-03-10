from django.core.management.base import BaseCommand
from collections import Counter
from django.core.files.images import ImageFile
from django.template.defaultfilters import slugify
from main import models
import os.path
import csv

class Command(BaseCommand):
    help = "Import products from BookTime"

    def add_arguments(self, parser) -> None:
        parser.add_argument("csvfile", type=open)
        parser.add_argument("image_baserdir", type=str)

    def handle(self, *args, **options):
        self.stdout.write("Importing products")
        c = Counter()
        reader = csv.DictReader(options.pop("csvfile"))
        for row in reader:
            product, created = models.Product.object.get_or_create(
                name = row["name"],
                price = row["price"]
            )
            product.description = row["description"]
            product.slug = slugify(row["name"])
            for import_tag in row["tags"].split("|"):
                tag, tag_created = models.ProductTag.object.get_or_create(
                    name = import_tag
                )
                product.tags.add(tag)
                c["tags"] += 1
                if tag_created:
                    c["tags_created"] += 1
            with open(os.path.join(
                    options["image_baserdir"],
                    row["image_filename"],
                ), "rb",) as file:
                image = models.ProductImage(
                    product = product,
                    image = ImageFile(file, name = row["image_filename"])
                )
                image.save()
                c["images"] += 1
            product.save()
            c["products"] += 1
            if created:
                c["products_created"] += 1

        self.stdout.write(
            "Products processed = %d (created = %d)"
            % (c["products"], c["products_created"])
        )
        self.stdout.write(
            "Tags processed = %d (created = %d)"
            % (c["tags"], c["tags_created"])
        )
        self.stdout.write("Images processed = %d" % c["images"])
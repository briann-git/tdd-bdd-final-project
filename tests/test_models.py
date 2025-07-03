# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, db, DataValidationError
from service import app
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHS)
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    def test_read_a_product(self):
        "It should read a product from the database"
        product = ProductFactory()
        product.create()
        self.assertEqual(product, Product.find(product.id))

    def test_update_a_product(self):
        "It should Update a product"
        product = ProductFactory()
        product.create()
        fetched = Product.find(product.id)
        self.assertEqual(product, fetched)

        # Modify the fetched item
        fetched.name = "New Name"
        fetched.description = "New Description"
        fetched.price = 5.65
        fetched.available = False
        fetched.category = Category.HOUSEWARES
        fetched.update()

        updated = Product.find(product.id)
        self.assertEqual(updated.name, "New Name")
        self.assertEqual(updated.description, "New Description")
        self.assertAlmostEqual(updated.price, Decimal(5.65))
        self.assertEqual(updated.available, False)
        self.assertEqual(updated.category, Category.HOUSEWARES)

    def test_fail_update_a_product(self):
        """It should fail if id is not provided for update"""
        product = ProductFactory()
        product.create()
        product.id = None
        with self.assertRaises(DataValidationError):
            product.update()

    def test_delete_a_product(self):
        """It should Delete a Product"""
        product = ProductFactory()
        # Create
        product.create()
        self.assertEqual(len(Product.all()), 1)
        # Delete
        product.delete()
        self.assertEqual(len(Product.all()), 0)

    def test_list_all_products(self):
        """It should list all products."""
        products = Product.all()
        self.assertEqual(len(products), 0)
        for _ in range(5):
            product = ProductFactory()
            product.create()
        self.assertEqual(len(Product.all()), 5)

    def test_find_by_name(self):
        """It should return a product given a name"""
        products = []
        for _ in range(5):
            product = ProductFactory()
            product.create()
            products.append(product)

        first_product = products[0]
        product_count = len(list(
            filter(lambda x: x.name == first_product.name, products)
        ))
        fetched = Product.find_by_name(first_product.name)
        self.assertEqual(len(fetched), product_count)

    def test_find_by_availability(self):
        """It should return products filtered by availability"""
        products = []
        for _ in range(5):
            product = ProductFactory()
            product.create()
            products.append(product)

        first_product_availability = products[0].available
        products_count = len(list(filter(lambda x: x.available == first_product_availability, products)))
        fetched = Product.find_by_availability(first_product_availability)
        self.assertEqual(len(fetched), products_count)

    def test_find_by_category(self):
        """It should return products filtered by category"""
        products = []
        for _ in range(5):
            product = ProductFactory()
            product.create()
            products.append(product)

        first_product_category = products[0].category
        product_count = len(list(
            filter(lambda x: x.category == first_product_category, products)
        ))
        fetched = Product.find_by_category(first_product_category)
        self.assertEqual(len(fetched), product_count)

    def test_find_by_price(self):
        """It should return products filtered by price"""
        products = []
        for _ in range(5):
            product = ProductFactory()
            product.create()
            products.append(product)

        first_product_price = products[0].price
        product_count = len(list(
            filter(lambda x: x.price == first_product_price, products)
        ))
        fetched = Product.find_by_price(first_product_price)
        self.assertEqual(len(fetched), product_count)

    def test_deserialize(self):
        """It should raise validation error if invalide available value is passed"""
        product = ProductFactory()
        serialized = product.serialize()

        serialized['available'] = "Yes"
        with self.assertRaises(DataValidationError):
            product.deserialize(data=serialized)

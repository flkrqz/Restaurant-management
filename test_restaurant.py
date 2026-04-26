# test_restaurant.py

import unittest
from restaurant import Food, Drink, Order, Table, Restaurant


class TestFood(unittest.TestCase):
    """Testuoja Food klasę"""

    def setUp(self):
        """setUp vykdomas PRIEŠ kiekvieną testą - sukuria objektus"""
        self.food = Food("F01", "Cepelinai", 8.50, "Pagrindinis")

    def test_food_creation(self):
        """Tikrina ar Food sukuriamas teisingai"""
        self.assertEqual(self.food.name, "Cepelinai")
        self.assertEqual(self.food.price, 8.50)
        self.assertEqual(self.food.category, "Pagrindinis")
        self.assertEqual(self.food.item_id, "F01")

    def test_food_display_contains_maistas(self):
        """Tikrina ar display() rodo [MAISTAS]"""
        result = self.food.display()
        self.assertIn("MAISTAS", result)
        self.assertIn("Cepelinai", result)

    def test_price_setter_valid(self):
        """Tikrina ar galima pakeisti kainą"""
        self.food.price = 9.00
        self.assertEqual(self.food.price, 9.00)

    def test_price_setter_negative_raises_error(self):
        """Tikrina ar neigiama kaina meta klaidą"""
        with self.assertRaises(ValueError):
            self.food.price = -1.00

    def test_str_representation(self):
        """Tikrina __str__ metodą"""
        result = str(self.food)
        self.assertIn("Cepelinai", result)
        self.assertIn("8.50", result)


class TestDrink(unittest.TestCase):
    """Testuoja Drink klasę"""

    def setUp(self):
        self.alcoholic_drink = Drink("D01", "Alus", 3.00, True)
        self.non_alcoholic = Drink("D02", "Vanduo", 1.50, False)

    def test_drink_creation(self):
        """Tikrina ar Drink sukuriamas teisingai"""
        self.assertEqual(self.alcoholic_drink.name, "Alus")
        self.assertTrue(self.alcoholic_drink.is_alcoholic)
        self.assertFalse(self.non_alcoholic.is_alcoholic)

    def test_drink_display_alcoholic(self):
        """Tikrina alkoholinio gėrimo display()"""
        result = self.alcoholic_drink.display()
        self.assertIn("GERIMAS", result)
        self.assertIn("Alkoholinis", result)

    def test_drink_display_non_alcoholic(self):
        """Tikrina nealkoholinio gėrimo display()"""
        result = self.non_alcoholic.display()
        self.assertIn("Nealkoholinis", result)

    def test_default_is_not_alcoholic(self):
        """Tikrina kad numatytasis gėrimas yra nealkoholinis"""
        drink = Drink("D03", "Sultys", 2.00)
        self.assertFalse(drink.is_alcoholic)


class TestOrder(unittest.TestCase):
    """Testuoja Order klasę"""

    def setUp(self):
        self.order = Order(1, 3)
        self.food = Food("F01", "Cepelinai", 8.50, "Pagrindinis")
        self.drink = Drink("D01", "Vanduo", 1.50, False)

    def test_order_creation(self):
        """Tikrina ar Order sukuriamas teisingai"""
        self.assertEqual(self.order.order_id, 1)
        self.assertEqual(self.order.table_number, 3)
        self.assertFalse(self.order.is_paid)

    def test_add_item(self):
        """Tikrina ar item pridedamas"""
        self.order.add_item(self.food, 2)
        self.assertEqual(len(self.order.get_items()), 1)

    def test_add_same_item_twice_merges(self):
        """Tikrina ar du kartus pridėtas tas pats item susujungia"""
        self.order.add_item(self.food, 1)
        self.order.add_item(self.food, 2)
        items = self.order.get_items()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0][1], 3)  

    def test_total_calculation(self):
        """Tikrina bendra sumos skaičiavimą"""
        self.order.add_item(self.food, 2)   
        self.order.add_item(self.drink, 1)  
        self.assertAlmostEqual(self.order.get_total(), 18.50, places=2)

    def test_total_empty_order(self):
        """Tuščio užsakymo suma = 0"""
        self.assertEqual(self.order.get_total(), 0.0)

    def test_remove_item(self):
        """Tikrina item šalinimą"""
        self.order.add_item(self.food)
        self.order.add_item(self.drink)
        self.order.remove_item("Cepelinai")
        items = self.order.get_items()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0][0].name, "Vanduo")

    def test_mark_as_paid(self):
        """Tikrina apmokėjimo pažymėjimą"""
        self.assertFalse(self.order.is_paid)
        self.order.mark_as_paid()
        self.assertTrue(self.order.is_paid)

    def test_add_item_invalid_quantity(self):
        """Tikrina ar neigiamas kiekis meta klaidą"""
        with self.assertRaises(ValueError):
            self.order.add_item(self.food, 0)

    def test_display_receipt_contains_total(self):
        """Tikrina ar sąskaita rodo sumą"""
        self.order.add_item(self.food, 1)
        receipt = self.order.display_receipt()
        self.assertIn("VISO", receipt)
        self.assertIn("8.50", receipt)


class TestTable(unittest.TestCase):
    """Testuoja Table klasę"""

    def setUp(self):
        self.table = Table(1, 4)

    def test_table_initially_free(self):
        """Naujas staliukas yra laisvas"""
        self.assertFalse(self.table.is_occupied)
        self.assertIsNone(self.table.current_order)

    def test_assign_order_marks_occupied(self):
        """Priskyrus užsakymą - staliukas užimtas"""
        order = Order(1, 1)
        self.table.assign_order(order)
        self.assertTrue(self.table.is_occupied)
        self.assertIsNotNone(self.table.current_order)

    def test_clear_table_makes_free(self):
        """Po atlaisvinimo - staliukas vėl laisvas"""
        order = Order(1, 1)
        self.table.assign_order(order)
        self.table.clear_table()
        self.assertFalse(self.table.is_occupied)
        self.assertIsNone(self.table.current_order)

    def test_table_properties(self):
        """Tikrina table numerį ir talpą"""
        self.assertEqual(self.table.table_number, 1)
        self.assertEqual(self.table.capacity, 4)


class TestRestaurantSingleton(unittest.TestCase):
    """Testuoja Singleton dizaino šabloną"""

    def setUp(self):
        
        Restaurant._instance = None

    def test_singleton_same_instance(self):
        """Du kartus sukurtas Restaurant duoda TĄ PATĮ objektą"""
        r1 = Restaurant("Restoranas A")
        r2 = Restaurant("Restoranas B")
        self.assertIs(r1, r2)  

    def test_restaurant_menu_management(self):
        """Tikrina meniu pridėjimą ir paiešką"""
        r = Restaurant()
        food = Food("F01", "Testinis Patiekalas", 5.00, "Test")
        r.add_to_menu(food)
        found = r.find_menu_item("Testinis Patiekalas")
        self.assertIsNotNone(found)
        self.assertEqual(found.name, "Testinis Patiekalas")

    def test_restaurant_remove_from_menu(self):
        """Tikrina šalinimą iš meniu"""
        r = Restaurant()
        food = Food("F02", "Salinamasis", 5.00, "Test")
        r.add_to_menu(food)
        removed = r.remove_from_menu("Salinamasis")
        self.assertTrue(removed)
        self.assertIsNone(r.find_menu_item("Salinamasis"))

    def test_create_order_invalid_table(self):
        """Tikrina klaidą kuriant užsakymą neegzistuojančiam staliukui"""
        r = Restaurant()
        with self.assertRaises(ValueError):
            r.create_order(999)

    def test_daily_revenue_only_paid(self):
        """Tikrina kad pajamos skaičiuoja tik apmokėtus"""
        r = Restaurant()
        r.add_table(Table(10, 4))
        food = Food("F99", "Testas", 10.00, "Test")
        r.add_to_menu(food)

        order = r.create_order(10)
        order.add_item(food, 1)
        
        self.assertEqual(r.get_daily_revenue(), 0.0)

        r.close_order(10)
        
        self.assertEqual(r.get_daily_revenue(), 10.0)


if __name__ == "__main__":
    
    unittest.main(verbosity=2)

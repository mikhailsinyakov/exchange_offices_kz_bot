import unittest

from exchange_offices import get_purchase_amount

class TestExchangeOffices(unittest.TestCase):
    def test_get_purchase_amount(self):
        office_info = {
            "USD": (468, 475),
            "EUR": (459, 464),
            "RUB": (7.1, 7.39)
        }

        self.assertEqual(get_purchase_amount(office_info, "USD", "KZT", 100), 100*468)
        self.assertEqual(get_purchase_amount(office_info, "KZT", "USD", 10000), 10000/475)
        self.assertEqual(get_purchase_amount(office_info, "RUB", "USD", 20000), 20000*7.1/475)



if __name__ == "__main__":
    unittest.main()
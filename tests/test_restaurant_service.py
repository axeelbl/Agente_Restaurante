import unittest

from app.backend.services.restaurant_service import handle_restaurant_request


class RestaurantServiceTests(unittest.TestCase):
    def test_menu_query_returns_menu(self):
        response = handle_restaurant_request("Ensename la carta")

        self.assertIsNotNone(response)
        self.assertIn("Carta actual", response["bot_message"])
        self.assertIn("Croquetas de jamon iberico", response["bot_message"])

    def test_menu_of_day_query_returns_daily_menu(self):
        response = handle_restaurant_request("Que lleva el menu del dia")

        self.assertIsNotNone(response)
        self.assertIn("Menu del dia", response["bot_message"])
        self.assertIn("Primeros", response["bot_message"])
        self.assertIn("Segundos", response["bot_message"])

    def test_vegetarian_recommendation_is_based_on_menu(self):
        response = handle_restaurant_request("Quiero algo vegetariano")

        self.assertIsNotNone(response)
        self.assertIn("te recomiendo", response["bot_message"].lower())
        self.assertIn("Arroz meloso de setas", response["bot_message"])
        self.assertIn("Curry suave de garbanzos", response["bot_message"])

    def test_basic_faq_hours(self):
        response = handle_restaurant_request("Cual es vuestro horario?")

        self.assertIsNotNone(response)
        self.assertIn("martes a domingo", response["bot_message"].lower())
        self.assertIn("lunes", response["bot_message"].lower())


if __name__ == "__main__":
    unittest.main()

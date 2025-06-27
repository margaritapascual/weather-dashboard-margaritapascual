# tests/test_config.py

import os
from dotenv import load_dotenv
import unittest

class TestConfig(unittest.TestCase):
    def test_api_key_loaded(self):
        load_dotenv()
        api_key = os.getenv("OPENWEATHER_API_KEY")
        self.assertIsNotNone(api_key, "API key should not be None")
        self.assertNotEqual(api_key, "", "API key should not be empty")


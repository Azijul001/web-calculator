"""
Comprehensive Unit and Integration Tests for the Python Web Calculator.
Tests mathematical engine logic, security constraints, and Flask API endpoints.
"""

import math
import unittest
import sys
import os

# Add parent directory to path so imports work cleanly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from calculator_engine import CalculatorEngine, CalculationError
from app import app


class TestCalculatorEngine(unittest.TestCase):
    """Unit tests for the AST-based calculator engine."""

    def setUp(self):
        self.deg_engine = CalculatorEngine(angle_mode="deg")
        self.rad_engine = CalculatorEngine(angle_mode="rad")

    def test_basic_arithmetic(self):
        self.assertEqual(self.deg_engine.evaluate("2 + 3")[0], 5)
        self.assertEqual(self.deg_engine.evaluate("10 - 4")[0], 6)
        self.assertEqual(self.deg_engine.evaluate("6 * 7")[0], 42)
        self.assertEqual(self.deg_engine.evaluate("20 / 4")[0], 5)
        self.assertEqual(self.deg_engine.evaluate("17 // 5")[0], 3)
        self.assertEqual(self.deg_engine.evaluate("17 % 5")[0], 2)
        self.assertEqual(self.deg_engine.evaluate("2 ** 4")[0], 16)
        self.assertEqual(self.deg_engine.evaluate("2 ^ 4")[0], 16)

    def test_operator_precedence_and_parentheses(self):
        self.assertEqual(self.deg_engine.evaluate("2 + 3 * 4")[0], 14)
        self.assertEqual(self.deg_engine.evaluate("(2 + 3) * 4")[0], 20)
        self.assertEqual(self.deg_engine.evaluate("10 - 2 * 3 + 4 / 2")[0], 6)
        self.assertEqual(self.deg_engine.evaluate("((2 + 3) * (4 - 1))")[0], 15)

    def test_implicit_multiplication_and_visual_symbols(self):
        self.assertEqual(self.deg_engine.evaluate("2(3 + 4)")[0], 14)
        self.assertEqual(self.deg_engine.evaluate("(2 + 1)(3 + 1)")[0], 12)
        self.assertAlmostEqual(self.deg_engine.evaluate("2pi")[0], 2 * math.pi)
        self.assertEqual(self.deg_engine.evaluate("6 × 7")[0], 42)
        self.assertEqual(self.deg_engine.evaluate("10 ÷ 2")[0], 5)
        self.assertEqual(self.deg_engine.evaluate("10 − 3")[0], 7)

    def test_percentages(self):
        self.assertEqual(self.deg_engine.evaluate("50%")[0], 0.5)
        self.assertEqual(self.deg_engine.evaluate("200 * 15%")[0], 30)

    def test_scientific_functions(self):
        # Square root & cube root
        self.assertEqual(self.deg_engine.evaluate("sqrt(144)")[0], 12)
        self.assertEqual(self.deg_engine.evaluate("cbrt(27)")[0], 3)

        # Trigonometry in Degrees
        self.assertAlmostEqual(self.deg_engine.evaluate("sin(30)")[0], 0.5, places=5)
        self.assertAlmostEqual(self.deg_engine.evaluate("cos(60)")[0], 0.5, places=5)
        self.assertAlmostEqual(self.deg_engine.evaluate("tan(45)")[0], 1.0, places=5)
        self.assertAlmostEqual(self.deg_engine.evaluate("sin(90)")[0], 1.0, places=5)

        # Trigonometry in Radians
        self.assertAlmostEqual(self.rad_engine.evaluate("sin(pi / 2)")[0], 1.0, places=5)
        self.assertAlmostEqual(self.rad_engine.evaluate("cos(pi)")[0], -1.0, places=5)

        # Logarithms & Exponentials
        self.assertEqual(self.deg_engine.evaluate("log(1000)")[0], 3)
        self.assertEqual(self.deg_engine.evaluate("log10(100)")[0], 2)
        self.assertAlmostEqual(self.deg_engine.evaluate("ln(e)")[0], 1.0, places=5)
        self.assertEqual(self.deg_engine.evaluate("log2(8)")[0], 3)
        self.assertAlmostEqual(self.deg_engine.evaluate("exp(2)")[0], math.exp(2), places=5)

        # Factorials & Absolute Values
        self.assertEqual(self.deg_engine.evaluate("fact(5)")[0], 120)
        self.assertEqual(self.deg_engine.evaluate("factorial(6)")[0], 720)
        self.assertEqual(self.deg_engine.evaluate("abs(-42)")[0], 42)

    def test_formatting_cleanliness(self):
        self.assertEqual(self.deg_engine.evaluate("0.1 + 0.2")[1], "0.3")
        self.assertEqual(self.deg_engine.evaluate("4.0 + 1.0")[1], "5")
        self.assertEqual(self.deg_engine.evaluate("10 / 2")[1], "5")

    def test_error_handling(self):
        with self.assertRaises(CalculationError):
            self.deg_engine.evaluate("10 / 0")

        with self.assertRaises(CalculationError):
            self.deg_engine.evaluate("sqrt(-1)")

        with self.assertRaises(CalculationError):
            self.deg_engine.evaluate("log(-5)")

        with self.assertRaises(CalculationError):
            self.deg_engine.evaluate("fact(-3)")

        with self.assertRaises(CalculationError):
            self.deg_engine.evaluate("2 + * 3")

    def test_security_constraints(self):
        # Code execution attempts must fail safely
        malicious_inputs = [
            "__import__('os').system('dir')",
            "open('test.txt', 'w')",
            "exec('x = 1')",
            "eval('2+2')",
            "[x for x in (1, 2)]",
            "lambda x: x + 1",
            "import math",
        ]
        for malicious in malicious_inputs:
            with self.assertRaises(CalculationError):
                self.deg_engine.evaluate(malicious)


class TestFlaskAPI(unittest.TestCase):
    """Integration tests for the Flask web application."""

    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_index_page(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Python", response.data)
        self.assertIn(b"expressionInput", response.data)

    def test_api_calculate_success(self):
        response = self.client.post(
            "/api/calculate",
            json={"expression": "15 * 4 + 10", "angle_mode": "deg"}
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["result"], "70")

    def test_api_calculate_error(self):
        response = self.client.post(
            "/api/calculate",
            json={"expression": "10 / 0", "angle_mode": "deg"}
        )
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertFalse(data["success"])
        self.assertIn("Cannot divide by zero", data["error"])

    def test_api_history_flow(self):
        # Perform calculations
        self.client.post("/api/calculate", json={"expression": "1 + 1"})
        self.client.post("/api/calculate", json={"expression": "2 * 3"})

        # Retrieve history
        res_hist = self.client.get("/api/history")
        self.assertEqual(res_hist.status_code, 200)
        history = res_hist.get_json()["history"]
        self.assertGreaterEqual(len(history), 2)
        self.assertEqual(history[0]["result"], "6")

        # Clear history
        res_clear = self.client.post("/api/clear-history")
        self.assertEqual(res_clear.status_code, 200)

        # Confirm empty
        res_hist_after = self.client.get("/api/history")
        self.assertEqual(len(res_hist_after.get_json()["history"]), 0)


if __name__ == "__main__":
    unittest.main()

"""
Safe Mathematical Expression Evaluator using Python's AST (Abstract Syntax Tree).
Provides secure evaluation of standard and scientific expressions with angle mode support.
"""

import ast
import math
import re
from typing import Any, Dict, Optional, Tuple, Union


class CalculationError(Exception):
    """Custom exception raised for calculator evaluation errors."""
    pass


class CalculatorEngine:
    """Evaluates mathematical expressions securely using AST parsing."""

    # Allowed unary operators
    UNARY_OPERATORS = {
        ast.UAdd: lambda a: +a,
        ast.USub: lambda a: -a,
    }

    # Allowed binary operators
    BINARY_OPERATORS = {
        ast.Add: lambda a, b: a + b,
        ast.Sub: lambda a, b: a - b,
        ast.Mult: lambda a, b: a * b,
        ast.Div: lambda a, b: CalculatorEngine._safe_div(a, b),
        ast.FloorDiv: lambda a, b: CalculatorEngine._safe_floordiv(a, b),
        ast.Mod: lambda a, b: CalculatorEngine._safe_mod(a, b),
        ast.Pow: lambda a, b: CalculatorEngine._safe_pow(a, b),
    }

    # Constants supported
    CONSTANTS: Dict[str, float] = {
        "pi": math.pi,
        "e": math.e,
        "tau": math.tau,
    }

    def __init__(self, angle_mode: str = "deg"):
        """
        Initialize calculator engine.
        :param angle_mode: 'deg' for degrees or 'rad' for radians.
        """
        self.angle_mode = angle_mode.lower() if angle_mode in ("deg", "rad") else "deg"

    @staticmethod
    def _safe_div(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        if b == 0:
            raise CalculationError("Cannot divide by zero")
        return a / b

    @staticmethod
    def _safe_floordiv(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        if b == 0:
            raise CalculationError("Cannot divide by zero")
        return a // b

    @staticmethod
    def _safe_mod(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        if b == 0:
            raise CalculationError("Cannot divide by zero in modulo")
        return a % b

    @staticmethod
    def _safe_pow(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        # Guard against absurdly large exponents that can cause denial of service
        if isinstance(b, (int, float)) and abs(b) > 10000:
            raise CalculationError("Exponent is too large (maximum allowed is 10,000)")
        try:
            res = a ** b
            if isinstance(res, complex):
                raise CalculationError("Result is a complex number")
            return res
        except OverflowError:
            raise CalculationError("Result overflowed numerical limit")

    def _get_functions(self) -> Dict[str, Any]:
        """Returns allowed mathematical functions, respecting the current angle mode."""
        is_deg = self.angle_mode == "deg"

        def _sin(x):
            val = math.radians(x) if is_deg else x
            # Handle near-zero floats like sin(180 deg)
            res = math.sin(val)
            return 0.0 if abs(res) < 1e-15 else res

        def _cos(x):
            val = math.radians(x) if is_deg else x
            res = math.cos(val)
            return 0.0 if abs(res) < 1e-15 else res

        def _tan(x):
            val = math.radians(x) if is_deg else x
            # Test for undefined tan(90 deg + k*180 deg)
            if is_deg and (abs(x % 180 - 90) < 1e-9 or abs(x % 180 + 90) < 1e-9):
                raise CalculationError("Tangent is undefined for this angle")
            return math.tan(val)

        def _asin(x):
            if x < -1 or x > 1:
                raise CalculationError("Domain error for asin (input must be between -1 and 1)")
            rad = math.asin(x)
            return math.degrees(rad) if is_deg else rad

        def _acos(x):
            if x < -1 or x > 1:
                raise CalculationError("Domain error for acos (input must be between -1 and 1)")
            rad = math.acos(x)
            return math.degrees(rad) if is_deg else rad

        def _atan(x):
            rad = math.atan(x)
            return math.degrees(rad) if is_deg else rad

        def _sqrt(x):
            if x < 0:
                raise CalculationError("Cannot calculate square root of a negative number")
            return math.sqrt(x)

        def _cbrt(x):
            return math.cbrt(x) if hasattr(math, "cbrt") else (abs(x) ** (1 / 3) * (-1 if x < 0 else 1))

        def _log(x, base=10):
            if x <= 0:
                raise CalculationError("Logarithm input must be strictly greater than zero")
            return math.log10(x)

        def _ln(x):
            if x <= 0:
                raise CalculationError("Natural logarithm input must be strictly greater than zero")
            return math.log(x)

        def _log2(x):
            if x <= 0:
                raise CalculationError("Logarithm base 2 input must be strictly greater than zero")
            return math.log2(x)

        def _exp(x):
            if x > 709:
                raise CalculationError("Result overflowed numerical limit in exp()")
            return math.exp(x)

        def _factorial(x):
            if not float(x).is_integer() or x < 0:
                raise CalculationError("Factorial requires a non-negative integer")
            if x > 1000:
                raise CalculationError("Factorial input is too large (maximum allowed is 1,000)")
            return math.factorial(int(x))

        return {
            "sin": _sin,
            "cos": _cos,
            "tan": _tan,
            "asin": _asin,
            "acos": _acos,
            "atan": _atan,
            "sqrt": _sqrt,
            "cbrt": _cbrt,
            "log": _log,
            "log10": _log,
            "ln": _ln,
            "log2": _log2,
            "exp": _exp,
            "abs": abs,
            "fact": _factorial,
            "factorial": _factorial,
            "round": round,
            "floor": math.floor,
            "ceil": math.ceil,
        }

    def preprocess_expression(self, expr: str) -> str:
        """
        Cleans and sanitizes user input expression into valid Python AST syntax.
        Handles visual symbols, implicit multiplication, and percentages.
        """
        if not expr or not expr.strip():
            raise CalculationError("Empty expression")

        s = expr.strip()

        # Replace visual math symbols
        s = s.replace("×", "*").replace("·", "*")
        s = s.replace("÷", "/")
        s = s.replace("−", "-")
        s = s.replace("π", "pi")
        s = s.replace("^", "**")

        # Convert percentage notation (e.g. 50% -> (50*0.01) or x% -> (x/100))
        s = re.sub(r"(\d+(\.\d+)?)%", r"(\1*0.01)", s)

        # Handle implicit multiplication:
        # e.g., 2pi -> 2*pi, 2(3+4) -> 2*(3+4), (2+3)(4+5) -> (2+3)*(4+5)
        # 1) standalone number before '(' -> number * (
        s = re.sub(r"\b(\d+(\.\d+)?)\s*\(", r"\1*(", s)
        # 2) ')' before digit -> ) * digit
        s = re.sub(r"\)\s*(\d)", r")*\1", s)
        # 3) ')' before '(' -> ) * (
        s = re.sub(r"\)\s*\(", r")*(", s)
        # 4) standalone number before identifier (like 2pi, 5sin) -> 2*pi, 5*sin
        s = re.sub(r"\b(\d+(\.\d+)?)\s*([a-zA-Z_])", r"\1*\3", s)
        # 5) ')' before identifier -> ) * identifier
        s = re.sub(r"\)\s*([a-zA-Z_])", r")*\1", s)

        return s

    def _eval_node(self, node: ast.AST, functions: Dict[str, Any]) -> Union[int, float]:
        """Recursively evaluates allowed AST nodes."""
        if isinstance(node, ast.Expression):
            return self._eval_node(node.body, functions)

        elif isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise CalculationError(f"Invalid constant type: {type(node.value).__name__}")

        elif isinstance(node, ast.UnaryOp):
            op_type = type(node.op)
            if op_type in self.UNARY_OPERATORS:
                operand = self._eval_node(node.operand, functions)
                return self.UNARY_OPERATORS[op_type](operand)
            raise CalculationError(f"Unsupported unary operator: {op_type.__name__}")

        elif isinstance(node, ast.BinOp):
            op_type = type(node.op)
            if op_type in self.BINARY_OPERATORS:
                left = self._eval_node(node.left, functions)
                right = self._eval_node(node.right, functions)
                return self.BINARY_OPERATORS[op_type](left, right)
            raise CalculationError(f"Unsupported binary operator: {op_type.__name__}")

        elif isinstance(node, ast.Name):
            name = node.id
            if name in self.CONSTANTS:
                return self.CONSTANTS[name]
            raise CalculationError(f"Unknown variable or constant '{name}'")

        elif isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                raise CalculationError("Complex function calls are not permitted")
            func_name = node.func.id
            if func_name not in functions:
                raise CalculationError(f"Unknown function '{func_name}'")

            args = [self._eval_node(arg, functions) for arg in node.args]
            try:
                return functions[func_name](*args)
            except TypeError:
                raise CalculationError(f"Invalid number of arguments for '{func_name}'")
            except Exception as e:
                if isinstance(e, CalculationError):
                    raise
                raise CalculationError(str(e))

        raise CalculationError(f"Unsupported expression syntax: {type(node).__name__}")

    def evaluate(self, expression: str) -> Tuple[Union[int, float], str]:
        """
        Evaluates the expression string.
        Returns a tuple of (numeric_result, formatted_result_string).
        """
        cleaned_expr = self.preprocess_expression(expression)

        try:
            parsed_ast = ast.parse(cleaned_expr, mode="eval")
        except SyntaxError as e:
            raise CalculationError(f"Syntax error in expression: {e.msg}")

        functions = self._get_functions()
        raw_result = self._eval_node(parsed_ast, functions)

        # Clean numerical display
        formatted = self.format_result(raw_result)
        return raw_result, formatted

    @staticmethod
    def format_result(val: Union[int, float]) -> str:
        """Formats the calculated value cleanly."""
        if isinstance(val, float):
            # If it's effectively an integer (e.g. 5.0)
            if val.is_integer() and abs(val) < 1e15:
                return str(int(val))
            # Round off floating point inaccuracies like 0.30000000000000004
            rounded = round(val, 10)
            if rounded.is_integer() and abs(rounded) < 1e15:
                return str(int(rounded))
            # Scientific notation for huge / tiny numbers
            if abs(val) >= 1e15 or (0 < abs(val) < 1e-6):
                return f"{val:.8e}".replace("+", "")
            # Normal float with trailing zeroes removed
            formatted = f"{rounded:.10f}".rstrip("0").rstrip(".")
            return formatted
        return str(val)

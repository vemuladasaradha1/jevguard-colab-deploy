#import app
from app.tools import calculator_tool, extract_expression


def test_calculator_multiplication():
    result = calculator_tool("25 * 48")
    assert result == "1200"


def test_calculator_addition():
    result = calculator_tool("100 + 25")
    assert result == "125"


def test_calculator_subtraction():
    result = calculator_tool("100 - 25")
    assert result == "75"


def test_calculator_division():
    result = calculator_tool("100 / 4")
    assert result == "25"


def test_calculator_power():
    result = calculator_tool("2 ** 5")
    assert result == "32"


def test_natural_language_expression():
    result = extract_expression(
        "What is 25 multiplied by 48?"
    )

    assert result == "25 * 48"



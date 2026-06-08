import pytest

from functions import divide, validate_password

# Вариант A: validate_password
class TestValidatePassword:
    def test_tc01(self):
        assert validate_password("Password1") is True

    def test_tc02(self):
        assert validate_password("MySecure2Pass") is True

    def test_tc03(self):
        assert validate_password("Short1") is False

    def test_tc04(self):
        assert validate_password("abcdefgh") is False

    def test_tc05(self):
        assert validate_password("12345678") is False

    def test_tc06(self):
        assert validate_password("Pass word1") is False

    def test_tc07(self):
        assert validate_password("Pass1234") is True

    def test_tc08(self):
        assert validate_password("Pass123") is False

    def test_tc09(self):
        assert validate_password("") is False

    def test_tc10(self):
        assert validate_password("        ") is False

    @pytest.mark.parametrize(
        "password,expected",
        [
            ("Abcdefg1", True),
            ("abcdefg1", True),
            ("ABCDEFG1", True),
            ("Abcdef12", True),
            ("Abcdefg", False),
            ("1234567a", True),
        ],
        ids=[
            "mixed_case_valid",
            "lowercase_valid",
            "uppercase_valid",
            "two_digits_valid",
            "no_digit_invalid",
            "seven_digits_plus_letter",
        ],
    )
    def test_tc11(self, password, expected):
        assert validate_password(password) is expected

# Вариант B: divide
class TestDivide:
    def test_tc12(self):
        assert divide(10, 2) == 5.0

    def test_tc13(self):
        assert divide(7, 3) == pytest.approx(2.3333333333333335)

    def test_tc14(self):
        assert divide(5.5, 2) == 2.75

    def test_tc15(self):
        assert divide(-10, 2) == -5.0

    def test_tc16(self):
        with pytest.raises(ZeroDivisionError, match="Деление на ноль"):
            divide(10, 0)

    def test_tc17(self):
        with pytest.raises(TypeError, match="Аргументы должны быть числами"):
            divide("10", 2)

    def test_tc18(self):
        assert divide(0, 5) == 0.0
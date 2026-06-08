"""Функции для практической работы 3: unit-тестирование."""


def validate_password(password: str) -> bool:
    if not isinstance(password, str):
        return False

    if len(password) < 8:
        return False

    # if " " in password:
    #     return False

    has_letter = any(char.isalpha() for char in password)
    has_digit = any(char.isdigit() for char in password)

    return has_letter and has_digit


def divide(a, b):
    """
    Делит число a на число b.
    Поддерживает int и float.
    При делении на 0 выбрасывает ZeroDivisionError.
    """
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        raise TypeError("Аргументы должны быть числами (int или float)")

    if b == 0:
        raise ZeroDivisionError("Деление на ноль невозможно")

    return a / b

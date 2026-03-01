from decimal import Decimal, InvalidOperation

from django import template

register = template.Library()


@register.filter
def money(value):
    try:
        amount = Decimal(str(value or 0))
    except (InvalidOperation, TypeError, ValueError):
        return "0$"

    sign = "-" if amount < 0 else ""
    amount = abs(amount).quantize(Decimal("0.01"))

    integer_part = int(amount)
    decimal_part = int((amount - integer_part) * 100)
    integer_text = f"{integer_part:,}".replace(",", ".")

    if decimal_part:
        return f"{sign}{integer_text},{decimal_part:02d}$"
    return f"{sign}{integer_text}$"
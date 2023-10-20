from django import template

register = template.Library()


@register.filter
def neg(value):
    return - value


# (pas de chiffre après la virgule)
@register.filter
def round0(value):
    return '{0:.0f}'.format(value)


# utilisé pour afficher des sommes d'argents (2 chiffres après la virgule)
@register.filter
def round2(value):
    return '{0:.2f}'.format(value)


@register.filter
def round_stock(value):
    """
    Dans beaucoup de cas, floatformat pourrait-être préférable

    https://docs.djangoproject.com/en/4.2/ref/templates/builtins/#floatformat
    """
    v = abs(value)
    if v >= 100:
        return '{0:.0f}'.format(value)
    if v >= 10:
        return '{0:.1f}'.format(value).rstrip('0').rstrip('.')
    if v >= 1:
        return '{0:.2f}'.format(value).rstrip('0').rstrip('.')
    if v == 0:
        return '0'
    else:
        return '{0:.3f}'.format(value)


@register.filter
def comma_to_dot(value):
    return str(value).replace(',', '.')


def bool_to_utf8(b):
    if b:
        return "✔"
    else:
        return "✘"

@register.filter
def print_quantity(quantity, unit=None):
    q = round_stock(quantity)
    if unit is not None:
        if q == '1' or q == '-1' or q == '0':
            return q + ' ' + unit.name
        else:
            return q + ' ' + unit.plural_name()
    else:
        return q

@register.filter
def print_quantity_op(op):
    if op.product is not None:
        return print_quantity(op.quantity, op.product.unit)
    else:
        return print_quantity(op.quantity)

@register.filter
def print_neg_quantity_op(op):
    if op.product is not None:
        return print_quantity(-op.quantity, op.product.unit)
    else:
        return print_quantity(-op.quantity)

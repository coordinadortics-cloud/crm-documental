from django import template

register = template.Library()


@register.filter
def pesos(valor):
    try:
        valor = float(valor)
        return "$ {:,.0f}".format(valor).replace(",", ".")
    except:
        return "$ 0"
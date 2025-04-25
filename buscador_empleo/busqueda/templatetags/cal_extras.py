from django import template

register = template.Library()

@register.filter
def notas_del_dia(notas_por_dia, dia):
    return notas_por_dia.get(dia, [])

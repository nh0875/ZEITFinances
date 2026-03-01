from django import template

register = template.Library()


@register.filter
def es_admin(user):
    """Retorna True si el usuario es administradora (staff/superuser/grupo administrador)."""
    if not user or not user.is_authenticated:
        return False
    return user.is_staff or user.is_superuser or user.groups.filter(name__iexact="administrador").exists()


@register.filter
def es_recepcionista(user):
    """Retorna True si el usuario pertenece al grupo recepcionista y no es admin."""
    if not user or not user.is_authenticated:
        return False
    return user.groups.filter(name__iexact="recepcionista").exists() and not es_admin(user)

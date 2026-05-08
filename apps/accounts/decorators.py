from functools import wraps
from django.shortcuts import redirect
from django.http import HttpResponseForbidden


def login_required(view_func):
    """
    Verifica se o usuário está autenticado.
    Se não estiver, redireciona para o login.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f"/auth/login/?next={request.path}")
        return view_func(request, *args, **kwargs)
    return wrapper


def role_required(*roles):
    """
    Verifica se o usuário tem o role necessário.
    Recebe um ou mais roles permitidos.

    Uso:
      @role_required("kitchen")
      @role_required("owner", "manager")
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect(f"/auth/login/?next={request.path}")
            if request.user.role not in roles:
                return HttpResponseForbidden(
                    "Você não tem permissão para acessar esta página."
                )
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def kitchen_required(view_func):
    """
    Atalho para views da cozinha.
    Permite kitchen, manager e owner — todos podem ver a cozinha.
    """
    return role_required("kitchen", "manager", "owner", "superadmin")(view_func)


def panel_required(view_func):
    """
    Atalho para views do painel administrativo.
    Apenas owner, manager e superadmin.
    """
    return role_required("owner", "manager", "superadmin")(view_func)
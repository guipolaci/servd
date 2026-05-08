from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.http import require_POST


def login_view(request):
    """
    Página de login.
    GET  → exibe o formulário
    POST → processa as credenciais
    """
    # Se já estiver logado, redireciona para onde deve ir
    if request.user.is_authenticated:
        return _redirect_by_role(request.user)

    error = None

    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")

        # authenticate() verifica email e senha no banco
        # retorna o User se correto, None se errado
        user = authenticate(request, username=email, password=password)

        if user is not None:
            # login() cria a sessão — salva no banco e envia cookie
            login(request, user)

            # Redireciona para onde o usuário tentou acessar
            # ou para a página padrão do seu role
            next_url = request.GET.get("next")
            if next_url:
                return redirect(next_url)
            return _redirect_by_role(user)
        else:
            error = "Email ou senha incorretos."

    return render(request, "auth/login.html", {"error": error})


@require_POST
def logout_view(request):
    """
    Encerra a sessão do usuário.
    Só aceita POST — GET não deve deslogar por segurança.
    """
    logout(request)
    return redirect("/auth/login/")


def _redirect_by_role(user):
    """
    Redireciona o usuário para a página certa
    baseado no seu role e restaurante.
    """
    if user.role == "superadmin":
        return redirect("/django-admin/")

    if user.restaurant:
        slug = user.restaurant.slug
        if user.role == "kitchen":
            return redirect(f"/kitchen/{slug}/")
        return redirect(f"/panel/{slug}/")

    # Usuário sem restaurante associado
    return redirect("/auth/login/")
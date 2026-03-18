from django.http import Http404
from apps.accounts.models import Restaurant

class TenantMiddleware:
    """
    Intercepta toda requisição e resolve o tenant (restaurante)
    a partir do slug presente na URL.

    URLs com slug:
      /tropical-lanches/table/5/     → request.restaurant = Tropical Lanches
      /kitchen/tropical-lanches/     → request.restaurant = Tropical Lanches
      /panel/tropical-lanches/menu/  → request.restaurant = Tropical Lanches

    URLs sem slug (admin, auth, static):
      /django-admin/   → request.restaurant = None
      /auth/login/     → request.restaurant = None
    """

    # URLs que não pertencem a nenhum tenant
    # O middleware ignora essas e não tenta resolver slug
    EXEMPT_PREFIXES = (
        "/django-admin/",
        "/auth/",
        "/static/",
        "/media/",
    )

    def __init__(self, get_response):
        # get_response é a próxima camada da pilha
        # pode ser outro middleware ou a view final
        self.get_response = get_response

    def __call__(self, request):
        # Define o valor padrão — None significa "sem tenant"
        request.restaurant = None

        # Verifica se a URL atual deve ser ignorada
        is_exempt = any(
            request.path.startswith(prefix)
            for prefix in self.EXEMPT_PREFIXES
        )

        if not is_exempt:
            slug = self._extract_slug(request.path)

            if slug:
                try:
                    request.restaurant = Restaurant.objects.select_related(
                        "plan",
                        "subscription",
                    ).get(slug=slug, is_active=True)
                except Restaurant.DoesNotExist:
                    raise Http404(f"Restaurante '{slug}' não encontrado.")

        # Passa a requisição para o próximo middleware ou view
        return self.get_response(request)

    def _extract_slug(self, path):
        """
        Extrai o slug do caminho da URL.

        /tropical-lanches/table/5/    → tropical-lanches
        /kitchen/tropical-lanches/    → tropical-lanches
        /panel/tropical-lanches/menu/ → tropical-lanches

        Prefixos conhecidos como kitchen e panel são ignorados
        porque não são slugs — são partes fixas da URL.
        """
        # Remove barras e separa as partes da URL
        parts = [part for part in path.split("/") if part]

        if not parts:
            return None

        # Partes fixas da URL que não são slugs
        skip = {"kitchen", "panel", "auth"}

        for part in parts:
            if part not in skip:
                return part

        return None
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify


class Plan(models.Model):
    """
    Planos do SaaS. Define os limites de cada restaurante.
    """
    class Name(models.TextChoices):
        FREE = "free", "Free"
        STARTER = "starter", "Starter"
        PRO = "pro", "Pro"

    name = models.CharField(max_length=50, choices=Name.choices, unique=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    max_tables = models.PositiveIntegerField(default=5)
    max_products = models.PositiveIntegerField(default=20)
    has_analytics = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Restaurant(models.Model):
    """
    Tenant central do sistema.
    Todo dado pertence a um Restaurant.
    O slug é o identificador nas URLs: servd.app/tropical-lanches/
    """
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=100, unique=True)
    plan = models.ForeignKey(
        Plan,
        on_delete=models.PROTECT,
        related_name="restaurants"
    )
    logo = models.ImageField(upload_to="restaurants/logos/", blank=True, null=True)
    address = models.CharField(max_length=500, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Gera o slug automaticamente a partir do nome
        # se ainda não tiver um
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Subscription(models.Model):
    """
    Assinatura ativa de um restaurante.
    Controla qual plano está ativo e quando expira.
    """
    class Status(models.TextChoices):
        TRIALING = "trialing", "Trialing"
        ACTIVE = "active", "Active"
        PAST_DUE = "past_due", "Past Due"
        CANCELLED = "cancelled", "Cancelled"

    restaurant = models.OneToOneField(
        Restaurant,
        on_delete=models.CASCADE,
        related_name="subscription"
    )
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.TRIALING
    )
    started_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.restaurant} — {self.plan}"


class User(AbstractUser):
    """
    Usuário customizado. Substitui o User padrão do Django.
    Todo usuário de staff pertence a um restaurante e tem um role.
    Clientes finais não são usuários — acessam via QR Code sem login.
    """
    class Role(models.TextChoices):
        SUPERADMIN = "superadmin", "Super Admin"
        OWNER = "owner", "Owner"
        MANAGER = "manager", "Manager"
        KITCHEN = "kitchen", "Kitchen"

    email = models.EmailField(unique=True)
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
    )
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.KITCHEN
    )

    # Login por email em vez de username
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    @property
    def is_superadmin(self):
        return self.role == self.Role.SUPERADMIN

    @property
    def is_owner(self):
        return self.role == self.Role.OWNER

    @property
    def is_kitchen(self):
        return self.role == self.Role.KITCHEN

    def __str__(self):
        return f"{self.email} ({self.role})"
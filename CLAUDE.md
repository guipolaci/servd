# Projeto Servd

## Stack
- Django 5
- PostgreSQL
- Redis + Django Channels (WebSockets)
- HTMX + Alpine.js (frontend)
- Python 3.12

## Arquitetura (HackSoft style)
- models/ — apenas definições de dados
- selectors/ — queries (leituras)
- services/ — regras de negócio (escritas)
- views/ — entrada HTTP

## Convenções
- Multi-tenancy via Foreign Key + slug-based TenantMiddleware
- Type hints obrigatórios em services e selectors
- Nomes de funções em snake_case
- Comentários em português

## Comandos
- Iniciar: python manage.py runserver
- Migrations: python manage.py migrate
- Testes: pytest
- Worker: python manage.py runworker
- Shell: python manage.py shell_plus

## Contexto do negócio
- SaaS multi-tenant pra restaurantes
- Cliente real: Tropical Lanches (São Carlos, SP)
- Real-time ordering via WebSockets
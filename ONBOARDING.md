# Servd — Contexto do Projeto

## O que é
SaaS multi-tenant para restaurantes com pedidos em tempo real via WebSockets. Cliente real: **Tropical Lanches** (São Carlos, SP).

## Stack
- Django 5 + Python 3.12
- PostgreSQL (banco principal)
- Redis + Django Channels (WebSockets)
- HTMX + Alpine.js (frontend reativo sem SPA)
- Tailwind CSS (via django-tailwind)
- Docker (dev e prod)

## Arquitetura (HackSoft style)
```
apps/<app>/
  models/      — definições de dados
  selectors/   — queries (leituras)
  services/    — regras de negócio (escritas)
  views/       — entrada HTTP
  consumers/   — WebSocket handlers
```

## Apps
- `accounts` — autenticação, roles (admin, cozinha), TenantMiddleware por slug
- `menu` — categorias e itens do cardápio por restaurante
- `orders` — pedidos, status (pending → preparing → ready → delivered), sinal post_save para WebSocket
- `dashboard` — painel administrativo (em construção)

## Fluxo principal
1. Cliente acessa `/menu/<slug>/` → vê cardápio → faz pedido
2. Pedido salvo → `post_save` signal dispara evento WebSocket
3. Cozinha recebe notificação em tempo real no painel `/kitchen/<slug>/`
4. Cozinha atualiza status via HTMX (POST → 204) → WebSocket atualiza o card na UI sem reload

## Convenções
- Type hints obrigatórios em services e selectors
- Nomes de funções em snake_case
- Comentários em português
- Multi-tenancy: todo acesso filtrado por `restaurant` via middleware

## Comandos úteis
```bash
python manage.py runserver   # servidor
python manage.py migrate     # migrações
python manage.py runworker   # worker Channels
pytest                       # testes
python manage.py shell_plus  # shell com imports automáticos
```

## Histórico de commits
1. Setup inicial com arquitetura em camadas e multi-tenancy
2. WebSocket com Django Channels
3. Docker + PostgreSQL + Redis
4. Autenticação com controle de roles
5. Tailwind CSS + estilização do menu público
6. Fix: notificações via post_save signal
7. Redesign de templates e refatoração da view de status de pedido
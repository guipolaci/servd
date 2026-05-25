# Servd 🍽️

SaaS de cardápio digital com pedidos em tempo real para restaurantes e lanchonetes.

O cliente escaneia o QR Code da mesa, monta o pedido no celular e confirma.
O pedido vai direto para o painel da cozinha via WebSocket — sem atendente intermediário.

## Stack

- **Backend:** Django 5 + Python 3.12
- **Real-time:** Django Channels + WebSocket + Redis
- **Frontend:** HTMX + Alpine.js + Tailwind CSS
- **Banco:** PostgreSQL
- **Deploy:** Railway.app
- **Infra local:** Docker Compose (PostgreSQL + Redis)

## Como rodar localmente

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/servd.git
cd servd

# Suba o banco e o Redis
docker compose up -d

# Crie e ative o ambiente virtual
python3 -m venv .venv
source .venv/bin/activate

# Instale as dependências
pip install -r requirements/development.txt

# Configure o ambiente
cp .env.example .env

# Rode as migrations
python manage.py migrate

# Inicie o servidor
python manage.py runserver
```

## Arquitetura

Projeto seguindo o [HackSoft Django Style Guide](https://github.com/HackSoftware/Django-Styleguide) com arquitetura em camadas:

```
apps/<app>/
  models/      → estrutura dos dados
  selectors/   → queries de leitura
  services/    → regras de negócio (escritas, validações)
  views/       → recebe request, retorna response
```

Multi-tenancy via Foreign Key: todo registro pertence a um `Restaurant`. O `TenantMiddleware` resolve o tenant pelo slug na URL e injeta `request.restaurant` em todas as views.

## Apps

### `accounts`
- Model `Restaurant` — tenant central do sistema, identificado por slug
- Model `User` — usuário customizado com login por email e roles: `superadmin`, `owner`, `manager`, `kitchen`
- Model `Plan` — planos do SaaS (Free, Starter, Pro) com limites de mesas e produtos
- Model `Subscription` — controla o plano ativo e status de cada restaurante
- Autenticação com redirecionamento por role pós-login
- Decorators de autorização: `login_required`, `role_required`, `kitchen_required`, `panel_required`

### `menu`
- Model `Category` — categorias do cardápio (Lanches, Bebidas, etc.), ordenáveis
- Model `Product` — itens do cardápio com preço, imagem, tags (Mais Pedido, Novidade, Vegetariano) e disponibilidade
- Model `ProductExtra` — adicionais configuráveis por produto (ex: bacon +R$3)

### `orders`
- Model `Table` — mesas físicas com geração automática de QR Code (aponta para o cardápio da mesa)
- Model `Order` — pedido com status progressivo: `pending → preparing → ready → delivered / cancelled`
- Model `OrderItem` — linha do pedido com snapshot de preço (preserva o valor cobrado mesmo se o produto for editado)
- Model `OrderItemExtra` — adicional selecionado com snapshot de preço
- Service `create_order` — criação atômica de pedido com cálculo de total e notificação da cozinha
- Service `update_order_status` — avança o status e notifica cozinha + cliente via WebSocket

### `dashboard`
- Estrutura criada (views, selectors, services) — em desenvolvimento

## Fluxo do pedido

```
Cliente escaneia QR Code
        ↓
  Cardápio da mesa (menu_view)
        ↓
  Monta pedido e confirma (place_order_view)
        ↓
  Página de acompanhamento (order_tracking_view)
  [WebSocket: escuta status do pedido]
        ↓
  Painel da cozinha (kitchen_view)
  [WebSocket: recebe novos pedidos em tempo real]
        ↓
  Cozinha atualiza status → notifica cliente via WebSocket
```

## WebSocket consumers

| Consumer | URL | Descrição |
|---|---|---|
| `KitchenConsumer` | `ws/kitchen/<slug>/` | Painel da cozinha — recebe todos os pedidos do tenant |
| `OrderStatusConsumer` | `ws/order/<order_id>/` | Cliente acompanha o status do seu pedido |

## Autenticação

- Login por email e senha
- Sessão padrão do Django
- Redirecionamento pós-login por role: `kitchen` → painel da cozinha, `owner/manager` → painel admin, `superadmin` → Django Admin
- Views protegidas por decorators customizados

## Comandos úteis

```bash
python manage.py runserver      # servidor de desenvolvimento
python manage.py migrate        # executa migrations pendentes
python manage.py runworker      # worker do Django Channels
python manage.py shell_plus     # shell com todos os models importados
pytest                          # testes
docker compose up -d            # sobe PostgreSQL + Redis
docker compose down             # derruba os containers
```

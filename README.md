# Servd 🍽️

SaaS de cardápio digital com pedidos em tempo real para restaurantes e lanchonetes.

O cliente escaneia o QR Code da mesa, monta o pedido no celular e confirma.
O pedido vai direto para o painel da cozinha via WebSocket — sem atendente intermediário.

## Stack

- **Backend:** Django 5
- **Real-time:** Django Channels + WebSocket + Redis
- **Frontend:** HTMX + Alpine.js + Tailwind CSS
- **Banco:** PostgreSQL
- **Deploy:** Railway.app

## Como rodar localmente
```bash
# Clone o repositório
git clone https://github.com/seu-usuario/servd.git
cd servd

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

Projeto seguindo o HackSoft Django Style Guide com arquitetura em camadas:
```
apps/<app>/
  models/      → estrutura dos dados
  selectors/   → queries de leitura
  services/    → regras de negócio
  views/       → recebe request, retorna response
```
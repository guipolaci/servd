import json
from channels.generic.websocket import AsyncWebsocketConsumer


class KitchenConsumer(AsyncWebsocketConsumer):
    """
    Consumer do painel da cozinha.
    Fica conectado e recebe novos pedidos em tempo real.
    """

    async def connect(self):
        # Pega o slug da URL WebSocket: ws/kitchen/tropical-lanches/
        self.slug = self.scope["url_route"]["kwargs"]["slug"]

        # Nome do grupo — todos os consumers da mesma cozinha
        # ficam no mesmo grupo e recebem as mesmas mensagens
        self.group_name = f"kitchen_{self.slug}"

        # Entra no grupo
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        # Aceita a conexão WebSocket
        await self.accept()

    async def disconnect(self, close_code):
        # Sai do grupo quando o browser fechar a conexão
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def order_update(self, event):
        """
        Chamado quando o channel_layer.group_send envia
        um evento do tipo "order.update" para esse grupo.
        Repassa o evento para o browser via WebSocket.
        """
        await self.send(text_data=json.dumps({
            "type": "order.update",
            "order_id": event["order_id"],
            "status": event["status"],
        }))


class OrderStatusConsumer(AsyncWebsocketConsumer):
    """
    Consumer do cliente na mesa.
    Recebe atualizações de status do seu pedido específico.
    """

    async def connect(self):
        self.order_id = self.scope["url_route"]["kwargs"]["order_id"]
        self.group_name = f"order_{self.order_id}"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def order_status(self, event):
        """
        Chamado quando o status do pedido muda.
        Notifica o cliente em tempo real.
        """
        await self.send(text_data=json.dumps({
            "type": "order.status",
            "status": event["status"],
        }))
from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer

from ontrack.utils.datetime import DateTimeHelper as dt


class TaskProgressConsumer(JsonWebsocketConsumer):
    def connect(self):
        print("WebSoket Connected ...")
        self.task_id = self.scope["url_route"]["kwargs"]["task_id"]
        self.task_name = "task_%s" % self.task_id

        # Join task group
        async_to_sync(self.channel_layer.group_add)(self.task_name, self.channel_name)
        super().connect()
        message = {
            "type": "info",
            "title": "Connected",
            "message": f"Starting monitoring task id: {self.task_id}",
            "date": dt.current_dt_display_str(),
        }

        super().send_json(message)

    def disconnect(self, close_code):
        # Leave task group
        print("WebSoket Disconnected ...", close_code)
        async_to_sync(self.channel_layer.group_discard)(
            self.task_name, self.channel_name
        )

    def receive_json(self, content, **kwargs):
        print("Message received from client:", content)
        return super().receive_json(content, **kwargs)

    def send_json(self, content, close=False):
        return super().send_json(content, close)

    # Receive message from task group
    def celery_task_update(self, event):
        # Send task_id to WebSocket
        message = event["message"]
        self.send_json(message)

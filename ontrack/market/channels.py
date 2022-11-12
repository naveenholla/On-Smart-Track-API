# from asgiref.sync import async_to_sync
# from channels.generic.websocket import JsonWebsocketConsumer


# class TaskProgressConsumer(JsonWebsocketConsumer):
#     def celery_task_update(self, event):
#         message = event["message"]
#         self.send_json(message)

#     def connect(self):
#         print("WebSoket Connected ...")
#         super().connect()
#         # taskID = self.scope.get("url_route").get("kwargs").get("taskID")
#         # async_to_sync(self.channel_layer.group_add)(taskID, self.channel_name)

#     def receive_json(self, content, **kwargs):
#         print("Message received from client:", content)
#         return super().receive_json(content, **kwargs)

#     def send_json(self, content, close=False):
#         return super().send_json(content, close)

#     def receive(self, text_data=None, bytes_data=None, **kwargs):
#         self.send(text_data="Hello world!")

#     def disconnect(self, close_code):
#         print("WebSoket Connected ...", close_code)
#         self.close()

import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


class CallConsumer(WebsocketConsumer):
    # срабатывает при подключении к каналу
    def connect(self):
        self.accept()  # принимаем пользователя
        self.send(  # отсылаем ему JSON
            text_data=json.dumps(  # python dict -> JSON
                {"type": "connection", "data": {"message": "Connected"}}
            )
        )

    # срабатывает при отключении от канала
    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(self.my_name, self.channel_name)

    # получает сообщения от клиентского WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)  # JSON -> python dict
        event_type = text_data_json["type"]

        if event_type == "login":
            name = text_data_json["data"]["name"]
            self.my_name = name
            async_to_sync(self.channel_layer.group_add)(self.my_name, self.channel_name)

        if event_type == "call":
            name = text_data_json["data"]["name"]
            print(self.my_name, "is calling", name)
            async_to_sync(self.channel_layer.group_send)(
                name,
                {
                    "type": "call_received",
                    "data": {
                        "caller": self.my_name,
                        "rtcMessage": text_data_json["data"]["rtcMessage"],
                    },
                },
            )

        if event_type == "answer_call":
            caller = text_data_json["data"]["caller"]
            async_to_sync(self.channel_layer.group_send)(
                caller,
                {
                    "type": "call_answered",
                    "data": {"rtcMessage": text_data_json["data"]["rtcMessage"]},
                },
            )

        if event_type == "ICEcandidate":
            user = text_data_json["data"]["user"]
            async_to_sync(self.channel_layer.group_send)(
                user,
                {
                    "type": "ICEcandidate",
                    "data": {"rtcMessage": text_data_json["data"]["rtcMessage"]},
                },
            )

    # событие когда нам звонят и мы принимаем звонок
    def call_received(self, event):
        print("Call received by ", self.my_name)
        self.send(
            text_data=json.dumps({"type": "call_received", "data": event["data"]})
        )

    # событие когда мы звоним и наш звонок принят
    def call_answered(self, event):
        print(self.my_name, "'s call answered")
        self.send(
            text_data=json.dumps({"type": "call_answered", "data": event["data"]})
        )

    def ICEcandidate(self, event):
        self.send(text_data=json.dumps({"type": "ICEcandidate", "data": event["data"]}))

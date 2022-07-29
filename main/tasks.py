from typing import NamedTuple

from django.utils import timezone

from celery import shared_task

from main.models import Client, Mailing, Message


class MessageTuple(NamedTuple):
    id: int
    phone: str
    text: str


@shared_task
def start_sending(mailing: Mailing):
    """Запускает отправку сообщений или ставит её запуск на будущее время"""
    clients = Client.objects.filter(operator_code=mailing.attribute)

    if not clients.exists():
        clients = Client.objects.filter(tag=mailing.attribute)

        if not clients:
            return None

    messages = []
    for client in clients:
        messages.append(
            Message(
                datetime=timezone.now(),
                status="Waiting",
                mailing=mailing,
                client=client,
            )
        )
    messages = Message.objects.bulk_create(messages)

    send_list = [
        MessageTuple(id=obj.id, phone=obj.client.phone_number, text=mailing.text)
        for obj in messages
    ]

    if mailing.start_time <= timezone.now() <= mailing.end_time:
        send.delay(send_list)
    else:
        send.apply_async(args=(send_list,), eta=mailing.start_time)


@shared_task
def send(messages: list[Message]):
    """Отправляет сообщения клиентам"""
    print(messages) 

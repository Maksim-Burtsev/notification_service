import datetime
import json
from typing import NamedTuple

import requests
from requests.structures import CaseInsensitiveDict

from django.utils import timezone

from celery import shared_task

from main.models import Client, Mailing, Message
from notification_service.settings import TOKEN


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
        # send.apply_async(eta=timezone.now()+timedelta(seconds=5))


@shared_task
def send(messages: list[MessageTuple]):
    """
    Отправляет сообщения клиентам. 
    
    Если по какой-то причине письмо не было доставлено и время рассылки ещё не истекло, то следующая попытка будет предпринята в конце рассылки."
    
    Еcли время рассылки истекло, то всем неотправленным сообщениям присваивается соответствующий статус
    """

    URL, headers = _get_headers_and_url()
    success_id, failed_id = [], []

    for message in messages:
        data = {"id": message[0], "phone": message[1], "text": message[2]}
        response = requests.post(
            URL.format(msgId=message[0]), headers=headers, data=json.dumps(data)
        )

        if response.status_code == 200:
            success_id.append(message[0])
        else:
            failed_id.append(message[0])

    _update_message_status(success_id, status="Success")

    if failed_id:
        if timezone.now() < messages[0].mailing.end_time:
            _update_message_status(failed_id, status="Trying")

            failed_messages = [i for i in messages if i[0] in failed_id]
            send.apply_async(args=(failed_messages,), eta=messages[0].mailing.end_time)

        else:
            _update_message_status(failed_id, status="Wrong")


def _get_headers_and_url():
    """Возвращает ссылку и заголовки для запроса"""

    URL = "https://probe.fbrq.cloud/v1/send/{msgId}"
    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["Authorization"] = f"Bearer {TOKEN}"

    return URL, headers


def _update_message_status(id_list: list[int], status: str) -> None:
    """Обновляет статус сообщений"""

    if id_list:
        Message.objects.filter(id__in=id_list).update(
            status=status, datetime=timezone.now()
        )

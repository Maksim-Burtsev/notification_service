from datetime import timedelta

from django.shortcuts import get_object_or_404
from django.db.models import Count
from django.utils import timezone

from ninja import NinjaAPI
from ninja.errors import HttpError

from main.schemas import ClientSchema, MailingSchema, MessageSchema, MailingWithStatic
from main.models import Client, Mailing, Message
from main.tasks import start_sending
from main.logic import count_messages_by_status


api = NinjaAPI()


@api.post("/add_client")
def add_cliend(request, client: ClientSchema):
    """Добавление клиента"""
    if not client.phone_number.isdigit() or not client.operator_code.isdigit():
        raise HttpError(
            status_code=400, message="Номер телефона и код должны быть цифрами"
        )

    client = Client.objects.create(**client.dict())

    return {"id": client.id}


@api.put("/update_client/{client_id}")
def update_client(request, client_id: int, client: ClientSchema):
    """Обновление атрибутов клиента"""
    db_client = get_object_or_404(Client, id=client_id)

    for attr, value in client.dict().items():
        setattr(db_client, attr, value)

    try:
        db_client.save()
    except:
        raise HttpError(
            status_code=400,
            message="Клиент с указанным номером телефона уже существует",
        )

    return {"Success": True}


@api.delete("/delete_client/{client_id}")
def delete_client(request, client_id: int):
    """Удаление клиента"""
    client = get_object_or_404(Client, id=client_id)
    client.delete()

    return {"Success": True}


@api.post("/create_mailing")
def create_mailing(request, mailing: MailingSchema):
    """Создание рассылки"""
    mailing = Mailing.objects.create(**mailing.dict())

    start_sending(mailing)
    return {"id": mailing.id}


@api.delete("/delete_mailing/{mailing_id}")
def delete_mailing(request, mailing_id: int):
    """Удаление рассылки"""
    mailing = get_object_or_404(Mailing, id=mailing_id)
    mailing.delete()

    return {"Success": True}


@api.put("/update_mailing/{mailing_id}")
def update_mailing(requestm, mailing_id: int, mailing: MailingSchema):
    """Обновление рассыки"""
    db_mailing = get_object_or_404(Mailing, id=mailing_id)

    for attr, value in mailing.dict().items():
        setattr(db_mailing, attr, value)

    db_mailing.save()

    return {"Success": True}


@api.get("/detail_statics/{mailing_id}", response=list[MessageSchema | None])
def detail_mailing(request, mailing_id: int):
    """Детальная статистика отправленных сообщений по конкретной рассылке"""

    messages = Message.objects.filter(mailing_id=mailing_id).select_related("client")

    return messages


@api.get("/general_statics", response = list[MailingWithStatic|None])
def general_statics(request):
    """Общая статистика отправленных сообщений по рассылкам"""

    mailings = Mailing.objects.prefetch_related('messages').annotate(total=Count('messages')).all()

    res = [count_messages_by_status(mailing) for mailing in mailings]

    return res
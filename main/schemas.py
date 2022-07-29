from datetime import datetime

from ninja import Schema, Field


class ClientSchema(Schema):
    """Схема клиента"""
    phone_number: str = Field(..., max_length=11, description="Номер клиента")
    operator_code: str = Field(..., max_length=11, description="Код оператора")
    tag: str | None = Field(None, description="Произвольный тег")
    time_zone: str = Field(..., description="Временной пояс")


class MailingSchema(Schema):
    """Схема рассылки"""
    start_time: datetime = Field(..., description="Начало рассылки")
    text: str = Field(..., description="Сообщение рассылки")
    attribute: str = Field(..., description="Свойство")
    end_time: datetime = Field(..., description="Время окончания рассылки")

class MessageSchema(Schema):
    """Схема сообщения"""
    dtime: datetime = Field(..., description="Время создания (или отправки)", alias='datetime')
    status: str = Field(..., description='Статус отправки')
    mailing_id: int = Field(..., description='Id рассылки', alias='mailing.id')
    cliend_id: int = Field(..., description='Id клиента', alias='client.id')

class CountMessageSchema(Schema):
    """Схема количества отправленных сообщений"""
    success: int 
    wrong: int 
    waiting: int 
    trying: int 
    total: int 

class MailingWithStatic(MailingSchema):
    """Схема рассылки с количеством отправленных сообщений"""
    messages_count: CountMessageSchema



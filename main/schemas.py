from ninja import Schema, Field


class ClientSchema(Schema):
    """Схема клиента"""
    phone_number: str = Field(..., max_length=11, description="Номер клиента")
    operator_code: str = Field(..., max_length=11, description="Код оператора")
    tag: str | None = Field(None, description="Произвольный тег")
    time_zone: str = Field(..., description="Временной пояс")

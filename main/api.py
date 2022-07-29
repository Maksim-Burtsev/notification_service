from ninja import NinjaAPI
from ninja.errors import HttpError

from main.schemas import ClientSchema
from main.models import Client


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

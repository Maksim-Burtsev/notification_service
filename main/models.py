from django.db import models


class Mailing(models.Model):

    start_time = models.DateTimeField(help_text="Дата и время запуска рассылки")
    text = models.TextField(help_text="Текст сообщения для доставки клиенту")
    attribute = models.CharField(max_length=255, help_text="Свойство клиетов")
    end_time = models.DateTimeField(help_text="Время окончания рассылки")

    def __str__(self) -> str:
        return self.attribute


class Client(models.Model):

    phone_number = models.CharField(max_length=11, unique=True, help_text="Телефон клиента")
    operator_code = models.CharField(max_length=10, help_text="Код оператора")
    tag = models.CharField(
        max_length=200, blank=True, null=True, help_text="Произвольный тег"
    )
    time_zone = models.CharField(max_length=200, help_text="Часовой пояс")

    def __str__(self) -> str:
        return self.phone_number


class Message(models.Model):

    STATUS_CHOICES = (
        ("Sent", "Отправлено"),
        ("Waiting", "Ожидает отправки"),
        ("Wrong", "Не доставлено"),
    )

    datetime = models.DateTimeField(help_text="Дата и время создания/отправки")
    status = models.CharField(
        max_length=255, choices=STATUS_CHOICES, help_text="Статус отправки"
    )
    mailing = models.ForeignKey(
        Mailing, on_delete=models.CASCADE, related_name="messages", help_text="Рассылка"
    )
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name="messages", help_text="Клиент"
    )

    def __str__(self) -> str:
        return f'{self.client.phone_number}/{self.mailing}'

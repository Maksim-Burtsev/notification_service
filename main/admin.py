from django.contrib import admin

from main.models import Mailing, Message, Client


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ("attribute", "text", "start_time", "end_time")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("client", "status")


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("phone_number", "operator_code", "tag", "time_zone")

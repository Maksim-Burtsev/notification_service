def count_messages_by_status(obj):
    """Считает количество сообщений для объекта согласно статусу"""

    success, trying, wrong, waiting = 0, 0, 0, 0
    for message in obj.messages.all():
        if message.status == 'Success':
            success += 1
        elif message.status == 'Waiting':
            waiting += 1
        elif message.status == 'Trying':
            trying += 1
        elif message.status == 'Wrong':
            wrong += 1

    obj.messages_count = {
        'total':obj.total,
        'success':success,
        'wrong':wrong,
        'trying':trying,
        'waiting':waiting
    }

    return obj
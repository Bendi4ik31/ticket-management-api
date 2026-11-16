import time
from celery import shared_task
from .models import Ticket


@shared_task
def notify_ticket_status_change(ticket_id, new_status):
    """
    Фонова задача для сповіщення автора про зміну статусу тикета.
    """
    try:
        ticket = Ticket.objects.get(pk=ticket_id)
    except Ticket.DoesNotExist:
        print(f"[NOTIFICATION ERROR] Тикет #{ticket_id} не знайдено у базі даних.")
        return f"Ticket #{ticket_id} does not exist"

    time.sleep(3)  # Імітація важкої відправки листа
    
    author_email = ticket.author.email if ticket.author.email else f"{ticket.author.username}@example.com"
    
    print(
        f'[NOTIFICATION] Тикет #{ticket.id} ("{ticket.title}") змінив статус на {new_status}. '
        f'Надіслано автору: {author_email}'
    )
    return f"Notification sent to {author_email} for ticket #{ticket.id}"


@shared_task
def process_critical_alert(ticket_id):
    """
    Фонова задача для екстреного алерта при створенні CRITICAL тикета.
    """
    try:
        ticket = Ticket.objects.get(pk=ticket_id)
    except Ticket.DoesNotExist:
        print(f"[CRITICAL ALERT ERROR] Тикет #{ticket_id} не знайдено у базі даних.")
        return f"Ticket #{ticket_id} does not exist"

    if ticket.priority == Ticket.Priority.CRITICAL:
        time.sleep(2)  # Імітація відправки алерта у Telegram/Slack
        print(f'[CRITICAL ALERT] Зверніть увагу на тикет #{ticket.id} ("{ticket.title}")!')
        return f"Critical alert sent for ticket #{ticket.id}"

    return f"Ticket #{ticket.id} is not critical"
import telegram
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Order, Consultation
from FlowerShop.settings import TG_BOT_TOKEN, TG_CHAT_ID


bot = telegram.Bot(token=TG_BOT_TOKEN)



@receiver(post_save, sender=Order)
def notify_telegram_order(sender, instance, created, **kwargs):
    if created:
        message = (f"Новый заказ!\n"
            f"Клиент: {instance.customer_name} - {instance.customer_phone}\n"
            f"Дата и время: {instance.delivery_time}\n"
            f"Адрес: {instance.delivery_address}\n"
            f"Букет: {instance.bouquet }"
        )
        bot.send_message(chat_id=TG_CHAT_ID, text=message)

@receiver(post_save, sender=Consultation)
def notify_telegram_consultation(sender, instance, created, **kwargs):
    if created:
        message = (f"Требуется консультация!\n"
            f"Клиент: {instance.name}\n "
            f"Телефон: {instance.phone}\n"
        )
        bot.send_message(chat_id=TG_CHAT_ID, text=message)
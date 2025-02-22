from django.conf import settings
from telebot import TeleBot, types


class TelegramIntegration:
    def __init__(self):
        self.telegram = TeleBot(settings.TELEGRAM_SECRET_KEY)

    def send_video_to_telegram_channel(self, instance):
        event = instance.member.event
        category = instance.category_nomination.event_category.category.name
        nomination = instance.category_nomination.nomination.name

        arr_file_ids = instance.url_video.split(',')
        media_files = [types.InputMediaPhoto(file_id) for file_id in arr_file_ids]

        media_files[0].caption=f" Мероприятие - {event} \n{nomination} - {category}  \nНомер работы - {instance.id}"

        message_group = self.telegram.send_media_group(
            settings.TELEGRAM_CHAT_ID,
            media_files,
        )
        instance.url_message_video = f"https://t.me/BeautyRankVideo/{message_group[0].message_id}"
        instance.save()

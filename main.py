from telethon import TelegramClient, events
from telethon.tl.custom import Button
import re
import requests

# Вставляем api_id и api_hash
api_id = 12071866
api_hash = 'ce2652028d8f77d7ffa1a8566815e283'

client = TelegramClient('session_name', api_id, api_hash)
client.start()

# Настройки
target_user_id = 656670978  # ID пользователя для отслеживания
group_id = 2493357778  # ID группы
topic_id = 513  # ID нужного топика


@client.on(events.NewMessage(chats=group_id))
async def normal_handler(event):
    last_message = event.message.message  # Получаем текст сообщения
    from_id = event.from_id

    # Проверка reply_to и извлечение ID сообщения
    reply_to_msg_id = event.message.reply_to_msg_id if event.message.reply_to else None

    if reply_to_msg_id == topic_id and hasattr(from_id, 'user_id') and from_id.user_id == target_user_id:
        match_number = re.search(r'\+375[^\d]*(\d{2})[^\d]*(\d{3})[^\d]*(\d{2})[^\d]*(\d{2})', last_message)
        match_address_delivery = re.search(r'delivery_address:\s*(.+)', last_message)

        if match_number:
            kod_operatora = match_number.group(1)
            nomer_klienta = f'+375{kod_operatora}{match_number.group(2)}{match_number.group(3)}{match_number.group(4)}'

            # Извлечение адреса
            delivery_address = (match_address_delivery.group(1).strip() if match_address_delivery
                                else last_message[match_number.end():].strip())

            if delivery_address:
                formatted_address = delivery_address.replace(" ", "+")
                key = "09645daa-cc6f-4af8-9cf9-6a65d20bb98b"
                geocode_url = f"https://geocode-maps.yandex.ru/1.x/?apikey={key}&geocode={formatted_address}&format=json"

                response = requests.get(geocode_url)
                data = response.json()

                if data['response']['GeoObjectCollection']['featureMember']:
                    point = data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos']
                    b, a = map(float, point.split())

                    # Формирование URL для Яндекс.Карт
                    sokol_latitude, sokol_longitude = 53.872725, 27.904440
                    url = f"https://yandex.ru/maps/?rtext={sokol_latitude},{sokol_longitude}~{a},{b}&rtt=auto"
                    buttons = [[Button.url('Маршрут', url)]]

                    # Отправка сообщения с кнопками
                    await client.send_message(event.chat_id, f'Номер клиента: {nomer_klienta}',
                                              reply_to=reply_to_msg_id, buttons=buttons)


client.run_until_disconnected()
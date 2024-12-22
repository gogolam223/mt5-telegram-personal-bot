from telethon import TelegramClient

async def handle_noti(client: TelegramClient, chat_id: int, message = ''):
    if chat_id == 0:
        print('No noti chat id')
        return
    if client.is_connected():
        await client.send_message(entity=chat_id, message=message)
        return
    return True
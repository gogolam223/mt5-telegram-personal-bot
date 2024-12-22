import os
from dotenv import load_dotenv
from telethon import TelegramClient, events
from message_parser import message_parser_xauusd, message_parser_xauusd_combo
from mt5 import MetaTrader
from notification import handle_noti
from utils import parse_int

# Load environment variables from .env file
load_dotenv()

# Access the environment variables
telegram_api_id = os.getenv('TELEGRAM_API_ID')
telegram_api_hash = os.getenv('TELEGRAM_API_HASH')
telegram_source_chat_id = os.getenv('TELEGRAM_SOURCE_CHAT_ID')
telegram_noti_chat_id = os.getenv('TELEGRAM_NOTI_CHAT_ID')
mt5_server = os.getenv('MT5_SERVER')
mt5_login = os.getenv('MT5_LOGIN')
mt5_password = os.getenv('MT5_PASSWORD')

# config
ticker = 'XAUUSD'
acceptable_price_diff = 0.3
lot: float = 1.0 # make sure this is float
sl_point: int = 1000
tp_point: int = 100

# start
client = TelegramClient('telegram_session', telegram_api_id, telegram_api_hash)
mt = MetaTrader(ticker, int(mt5_login), mt5_password, mt5_server)

@client.on(events.NewMessage(chats=[parse_int(telegram_source_chat_id)]))
async def handler(event):
    # This function will be called when a new message is received
    result = message_parser_xauusd_combo(event)
    if result['valid']:
        # check position - not placing second order
        positions = mt.get_positions()
        if len(positions) > 0:
            await handle_noti(client, parse_int(telegram_noti_chat_id), 'Received telegram message but there is an order already')
            return
        
        # check time - within 30s of signal receive message time vs VM time
        tick_data = mt.get_tick_data()
        if abs(tick_data['timestamp'] - result['message_timestamp']) > 30:
            await handle_noti(client, parse_int(telegram_noti_chat_id), f'Tick timestamp [{tick_data['timestamp']}] & message timestamp [{result['message_timestamp']}] diff > 30')
            return
        
        # check TG price vs market price
        if result['trend'] == 'Up':
            if abs(tick_data['ask'] - result['current_price']) > acceptable_price_diff:
                await handle_noti(client, parse_int(telegram_noti_chat_id), f'Tick price [{tick_data['ask']}] & message price [{result['current_price']}] diff > {acceptable_price_diff}')
                return
            
            new_order = mt.place_order(
                lot,
                'BUY',
                sl_point,
                tp_point,
            )
            await handle_noti(client, parse_int(telegram_noti_chat_id), f'Buy Order Placed: {new_order.order}')
            return
        if result['trend'] == 'Down':
            if abs(tick_data['bid'] - result['current_price']) > acceptable_price_diff:
                await handle_noti(client, parse_int(telegram_noti_chat_id), f'Tick price [{tick_data['ask']}] & message price [{result['current_price']}] diff > {acceptable_price_diff}')
                return
            
            new_order = mt.place_order(
                lot,
                'SELL',
                sl_point,
                tp_point,
            )
            await handle_noti(client, parse_int(telegram_noti_chat_id), f'Sell Order Placed: {new_order.order}')
            return
        
        await handle_noti(client, parse_int(telegram_noti_chat_id), 'No Trend in the message')
        return
    else:
        await handle_noti(client, parse_int(telegram_noti_chat_id), result['msg'])
        return


async def main():
    await client.start()

    # get all dialogs and try to find the source chat
    dialogs = await client.get_dialogs()
    dialog = next((item for item in dialogs if str(item.id) == telegram_source_chat_id), None)

    # the source chat is not found in dialogs
    if (dialog == None):
        print("Invalid Source Chat ID... Please select a chat and update the .env")
        for item in dialogs:
            print(f"Chat ID: {item.id}, Title: {item.title}")
        await client.disconnect()
        return
    
    # start the listener & handle the msg
    print(f"Listening for new messages on chat [{dialog.title}]...")
    await client.run_until_disconnected()

try:
    client.loop.run_until_complete(main())
except KeyboardInterrupt:
    print("\nScript stopped.")

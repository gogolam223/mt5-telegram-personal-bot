from datetime import datetime
from telethon import events
from typing import TypedDict, Union, Literal

from utils import parse_float

class ValidMessage(TypedDict):
    valid: True
    fx: Literal['XAUUSD']
    trend: Literal['Up', 'Down']
    current_price: int
    message_timestamp: datetime

class InvalidMessage(TypedDict):
    valid: False
    msg: str

FormattedMessage = Union[ValidMessage, InvalidMessage]

def message_parser_xauusd(msg: events.NewMessage) -> FormattedMessage:
    try:
        text = msg.raw_text.splitlines()
        timestamp = msg.message.date.timestamp()

        # fx
        if text[0].strip() not in ['🔴XAUUSD🔴', '🟢XAUUSD🟢']:
            raise TypeError
        
        # price
        price_texts = text[1].strip().split(' ')
        if len(price_texts) != 2 or price_texts[0] != '現價:':
            raise TypeError
        price = parse_float(price_texts[1])
        if price == 0:
            raise TypeError

        # trend
        trend_text = text[3].strip()
        if trend_text not in ['Potential Uptrend Started', 'Potential Downtrend Started']:
            raise TypeError
        trend = 'Up' if trend_text == 'Potential Uptrend Started' else 'Down' if trend_text == 'Potential Uptrend Started' else None
        if trend == None:
            raise TypeError

        return {
            'valid': True,
            'fx': 'XAUUSD',
            'trend': trend,
            'current_price': price,
            'message_timestamp': timestamp,
        }
    except:
        return {
            'valid': False,
            "msg": f'Bot failed to read the telegram message: \n{msg.raw_text}'
        }
    

def message_parser_xauusd_combo(msg: events.NewMessage) -> FormattedMessage:
    try:
        text = msg.raw_text.splitlines()
        timestamp = msg.message.date.timestamp()
        # fx
        if text[0].strip() not in ['XAUUSD 1/3 Combo']:
            raise TypeError
        
        # price
        price_texts = text[2].strip().split(' ')
        if len(price_texts) != 2 or price_texts[0] != '現價:':
            raise TypeError
        price = parse_float(price_texts[1])
        if price == 0:
            raise TypeError

        # trend
        trend_text = text[1].strip()
        if trend_text not in ['入場方向: Short🔴', '入場方向: Long🟢']:
            raise TypeError
        trend = 'Up' if trend_text == '入場方向: Long🟢' else 'Down' if trend_text == '入場方向: Short🔴' else None
        if trend == None:
            raise TypeError
        
        # extra checking for the combo info
        fifteen_min_check = text[6].strip().split(' ')
        hour_check = text[7].strip().split(' ')
        if fifteen_min_check[0] != '15mins:' or hour_check[0] != '1hr:':
            raise TypeError
        
        if (trend == 'Up' and fifteen_min_check[1] == 'Uptrend' and hour_check[1] == 'Uptrend') or (trend == 'Down' and fifteen_min_check[1] == 'Downtrend' and hour_check[1] == 'Downtrend'):
            return {
                'valid': True,
                'fx': 'XAUUSD',
                'trend': trend,
                'current_price': price,
                'message_timestamp': timestamp,
            }
        else:
            return {
                'valid': False,
                "msg": f'Combo info does not match: \n{msg.raw_text}'
            }
    except:
        return {
            'valid': False,
            "msg": f'Bot failed to read the telegram message: \n{msg.raw_text}'
        }
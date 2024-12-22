import os
from dotenv import load_dotenv
import MetaTrader5 as mt5
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Literal

timezone_adjust = -1 * 60 * 60 * 2 # the mt5 is giving data in GMT+2 timezone, adding this adjustment to the time obtained from mt5

class MetaTrader:
    def __init__(self, ticker: str, login: int, password: str, server: str):
        self.login = login
        self.password = password
        self.server = server
        self.ticker = ticker

        if not mt5.initialize(login=login, password=password, server=server):
            raise RuntimeError("Failed to initialize MetaTrader5")

    def shutdown(self):
        mt5.shutdown()

    def is_market_avail(self) -> bool:
        # TODO: this method should check whether the market is open or close
        # but at this moment we use a try block to catch error while adding positions
        return True
    
    def place_order(
            self,
            lot: float,
            order_type: Literal['BUY', 'SELL'],
            sl_point: float,
            tp_point: float,
            devation = 20,
        ):
        tick_data = self.get_tick_data()
        if order_type == 'BUY':
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": self.ticker,
                "volume": lot,
                "type": mt5.ORDER_TYPE_BUY,
                "price": tick_data['ask'],
                "sl": tick_data['ask'] - sl_point * tick_data['point'],
                "tp": tick_data['ask'] + tp_point * tick_data['point'],
                "deviation": devation,
                "magic": 123456,
                "comment": "Opened by MT5-TELEGRAM-BOT",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
        elif order_type == 'SELL':
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": self.ticker,
                "volume": lot,
                "type": mt5.ORDER_TYPE_SELL,
                "price": tick_data['bid'],
                "sl": tick_data['bid'] + sl_point * tick_data['point'],
                "tp": tick_data['bid'] - tp_point * tick_data['point'],
                "deviation": 20,
                "magic": 0,
                "comment": "Opened by MT5-TELEGRAM-BOT",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
        else:
            raise TypeError("order_type Type Error")
        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            raise RuntimeError(f"Failed to add position: {result.comment}")
        return result

    def get_tick_data(self) -> Dict[str, Any]:
        info = mt5.symbol_info(self.ticker)
        tick = mt5.symbol_info_tick(self.ticker)
        if not tick:
            raise RuntimeError("Failed to get tick data")

        return {
            "timestamp": tick.time + timezone_adjust,
            "bid": tick.bid,
            "ask": tick.ask,
            "point": info.point,
        }

    def get_positions(self) -> List[Dict[str, Any]]:
        positions = mt5.positions_get(symbol=self.ticker)
        # print(positions)
        return [
            {
                "symbol": pos.symbol,
                "type": pos.type,
                "time": datetime.fromtimestamp(pos.time + timezone_adjust),
                "volume": pos.volume,
                "price_open": pos.price_open,
                "price_current": pos.price_current,
                "sl": pos.sl,
                "tp": pos.tp,
            } for pos in positions]
    

# Example usage
if __name__ == "__main__":
    # Load environment variables from .env file
    load_dotenv()

    ticker = 'XAUUSD'
    server = os.getenv('MT5_SERVER')
    login = os.getenv('MT5_LOGIN')
    password = os.getenv('MT5_PASSWORD')


    mt = MetaTrader(ticker ,login, password, server)
    try:
        # Getting tick data example
        tick_data = mt.get_tick_data()
        print(f"Tick data: {tick_data}")

        # Getting positions example
        positions = mt.get_positions()
        print(f"Positions: {positions}")

        # place order example
        result = mt.place_order(
            0.02,
            'SELL',
            3000,
            300,
        )
        print(f"Result: {result}")
    finally:
        mt.shutdown()




import copy
import datetime
import json
import os
import sys
import time

import pandas as pd
import xlwings as xw
from kiteconnect import KiteConnect
from py_vollib.black_scholes.greeks.analytical import delta, gamma, rho, theta, vega
from py_vollib.black_scholes.implied_volatility import implied_volatility


def get_login_credentials():
    global credential

    def login_credentials():
        print("Enter your Zerodha Login Credentials:")
        api_key = str(input("Enter API Key :"))
        api_secret = str(input("Enter API Secret :"))
        save_credential = (
            str(input("Press Y to save the login credential else N:")).upper() == "Y"
        )

        credential = {"api_key": api_key, "api_secret": api_secret}

        if save_credential:
            with open("Login_Credentials.txt", "w") as f:
                json.dump(credential, f)
            print("Data Saved ...")
        else:
            print("Data Save Cancelled!!")

    while True:
        try:
            with open("Login_Credentials.txt") as f:
                credential = json.load(f)
            break
        except Exception:
            login_credentials()
    return credential


def get_access_token():
    global access_token, token_file_path
    token_file_path = f"AccessToken/{datetime.datetime.now().date()}.json"

    def login():
        global credential
        print("Trying Log In:")
        api_key = credential["api_key"]
        api_secret = credential["api_secret"]

        kite = KiteConnect(api_key=api_key)
        print("Login url:", kite.login_url())
        request_token = input("Login and enter your request token here:")
        try:
            access_token = kite.generate_session(
                request_token=request_token, api_secret=api_secret
            )["access_token"]
            os.makedirs("AccessToken", exist_ok=True)
            with open(token_file_path, "w") as f:
                json.dump(access_token, f)
            print("Login sucessful ...")
        except Exception as e:
            print(f"Login Failed {e}")

    print("Loading access Token ...")
    while True:
        if os.path.exists(token_file_path):
            with open(token_file_path) as f:
                access_token = json.load(f)
            break
        else:
            login()
    return access_token


def get_kite():
    global kite, credential, access_token, token_file_path
    try:
        kite = KiteConnect(api_key=credential["api_key"])
        kite.set_access_token(access_token)
    except Exception as e:
        print(f"Error: {e}")
        os.remove(token_file_path) if os.path.exists(token_file_path) else None
        sys.exit()


def get_live_data(instruments):
    global kite, live_data

    try:
        live_data
    except Exception:
        live_data = {}

    try:
        live_data = kite.quote(instruments)
    except Exception as e:
        print(f"Get Live data Failed {e}")

    return live_data


def place_trade(symbol, quantity, direction):
    try:
        order = kite.place_order(
            variety=kite.VARIETY_REGULAR,
            exchange=symbol[0:3],
            tradingsymbol=symbol[4:],
            quantity=int(quantity),
            product=kite.PRODUCT_CNC,
            order_type=kite.ORDER_TYPE_MARKET,
            price=0.0,
            validity=kite.VALIDITY_DAY,
            tag="OnSmartTrack",
        )
        print(
            f"Order: Symbol {symbol},"
            f" Qty {quantity}, Direction {direction},"
            f" Time {datetime.datetime.now().time()} \n => {order}"
        )
        return order
    except Exception as e:
        return f"{e}"


def get_orderbook():
    global orders
    try:
        orders
    except Exception:
        orders = {}

    try:
        data = pd.DataFrame(kite.orders())
        data = data[data["tag"] == "OnSmartTrack"]
        data = data.filter(
            [
                "order_timestamp",
                "exchange",
                "tradingsymbol",
                "transaction_type",
                ["quantity", "average_price", "status", "status_message_raw"],
            ]
        )
        data.columns = data.columns.str.replace("_", " ")
        data.columns = data.columns.str.title()
        data = data.set_index(["Order Timestamp"], drop=True)
        data = data.sort_index(ascending=True)
        orders = data
    except Exception as e:
        print(e)

    return orders


def greeks(
    premium,
    expiry,
    asset_price,
    strike_price,
    interest_rate,
    instrument_type,
):
    try:
        t = (
            (
                datetime(
                    expiry.year,
                    expiry.month,
                    expiry.day,
                    15,
                    30,
                )
                - datetime.now()
            )
            / datetime.timedelta(days=1)
        ) / 365
        S = asset_price
        K = strike_price
        r = interest_rate
        if premium == 0 or t <= 0 or S <= 0 or K <= 0 or r <= 0:
            raise Exception
        flag = instrument_type[0].lower()
        imp_v = implied_volatility(premium, S, K, t, r, flag)
        return {
            "IV": imp_v,
            "Delta": delta(flag, S, K, t, r, imp_v),
            "Gamma": gamma(flag, S, K, t, r, imp_v),
            "Rho": rho(flag, S, K, t, r, imp_v),
            "Theta": theta(flag, S, K, t, r, imp_v),
            "Vega": vega(flag, S, K, t, r, imp_v),
        }
    except Exception:
        return {
            "IV": 0,
            "Delta": 0,
            "Gamma": 0,
            "Rho": 0,
            "Theta": 0,
            "Vega": 0,
        }


def start_excel():
    global kite, live_data
    excel_file_name = "TA_python.xlsx"
    print("Excel Starting ...")
    if not os.path.exists(excel_file_name):
        try:
            wb = xw.Book()
            wb.save(excel_file_name)
            wb.close()
        except Exception as e:
            print(e)
            sys.exit()
    wb = xw.Book(excel_file_name)
    for i in ["Data", "Exchange", "OrderBook"]:
        try:
            wb.sheets(i)
        except Exception:
            wb.sheets.add(i)
    dt = wb.sheets("Data")
    ex = wb.sheets("Exchange")
    ob = wb.sheets("OrderBook")

    ex.range("a:j").value = ob.range("a:l").value = dt.range("w:x").value = None
    dt.range("a1:x1").value = [
        "Sr.No",
        "Symbol",
        "Open",
        "High",
        "Low",
        "LTP",
        "Volume",
        "Vwap",
        "Best Bid Price",
        "Best Ask Price",
        "CLose",
        "OI",
        "IV",
        "Delta",
        "Gamma",
        "Rho",
        "Theta",
        "Vega",
        "Qty",
        "Direction",
        "Entry Signal",
        "Exit Signal",
        "Entry",
        "Exit",
    ]

    subs_lst = []
    while True:
        try:
            master_contract = pd.DataFrame(kite.instruments())
            master_contract = master_contract.drop(
                ["instrument_token", "exchange_token", "last_price", "tick_size"],
                axis=1,
            )
            master_contract["watchlist_symbol"] = (
                master_contract["exchange"] + ":" + master_contract["tradingsymbol"]
            )
            master_contract.columns = master_contract.columns.str.replace("_", " ")
            master_contract.columns = master_contract.columns.str.title()
            ex.range("a1").value = master_contract

            df = copy.deepcopy(master_contract)
            df = df[df["Segment"] == "NFO-OPT"]
            nfo_dict = {}
            for i in df.index:
                nfo_dict[f'NFO:{df["Tradingsymbol"][i]}'] = [
                    df["Expiry"][i],
                    df["Strike"][i],
                    df["Name"][i],
                ]
            break
        except Exception as e:
            print(e)
            time.sleep(1)

    while True:
        try:
            time.sleep(0.5)
            get_live_data(subs_lst)
            symbols = dt.range("b2:b500").value
            trading_info = dt.range("l2:q500").value

            for i in subs_lst:
                if i not in symbols:
                    subs_lst.remove(i)
                    try:
                        del live_data[i]
                    except Exception as e:
                        print(e)
            main_list = []
            idx = 0
            for i in symbols:
                lst = [
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                ]
                if i:
                    if i not in subs_lst:
                        subs_lst.append(i)
                    if i in subs_lst:
                        try:
                            ld = live_data[i]
                            ohlc = ld["ohlc"]
                            depth = ld["depth"]
                            lst = [
                                ohlc["open"],
                                ohlc["high"],
                                ohlc["low"],
                                ld["last_price"],
                            ]
                            try:
                                lst += [
                                    ld["volume"],
                                    ld["average_price"],
                                    depth["buy"][0]["price"],
                                    depth["sell"][0]["price"],
                                    ohlc["close"],
                                    ld["oi"],
                                ]

                                try:
                                    an = nfo_dict[i][2]
                                    if an == "NIFTY":
                                        asset_name = "NSE:NIFTY 50"
                                    elif an == "BANKNIFTY":
                                        asset_name = "NSE:NIFTY BANK"
                                    else:
                                        asset_name = f"NSE:{an}"
                                    lst += greeks(
                                        premium=ld["last_price"],
                                        expiry=nfo_dict[i][0],
                                        asset_price=live_data[asset_name]["last_price"],
                                        strike_price=nfo_dict[i][1],
                                        interest_rate=0.1,
                                        instrument_type=i[-2:],
                                    )
                                except Exception:
                                    lst += ["-", "-", "-", "-", "-", "-"]
                            except Exception:
                                lst += [
                                    0,
                                    0,
                                    0,
                                    0,
                                    ohlc["close"],
                                    0,
                                    "-",
                                    "-",
                                    "-",
                                    "-",
                                    "-",
                                    "-",
                                ]
                            trade_info = trading_info[idx]

                            if trade_info[0] is not None and trade_info[1] is not None:
                                direction = trade_info[1].upper()
                                trade_entry = "Buy" if direction == "BUY" else "Sell"
                                trade_exit = "Sell" if direction != "BUY" else "Buy"

                                if (
                                    type(trade_info[0]) is float
                                    and type(trade_info[1]) is str
                                    and trade_info[2] is True
                                ):
                                    if (
                                        trade_info[3] is not True
                                        and trade_info[4] is None
                                        and trade_info[5] is None
                                    ):
                                        dt.range(f"w{idx + 2}").value = place_trade(
                                            i, int(trade_info[0]), trade_entry
                                        )
                                    elif (
                                        trade_info[3] is True
                                        and trade_info[4] is not None
                                        and trade_info[5] is None
                                    ):
                                        dt.range(f"x{idx + 2}").value = place_trade(
                                            i, int(trade_info[0]), trade_exit
                                        )
                        except Exception as e:
                            print(e)
                main_list.append(lst)
                idx += 1
            dt.range("c2").value = main_list
            if wb.sheets.active.name == "OrderBook":
                ob.range("a1").value = get_orderbook()
        except Exception as e:
            print(e)


if __name__ == "__main__":
    get_login_credentials()
    get_access_token()
    get_kite()
    get_orderbook()
    start_excel()

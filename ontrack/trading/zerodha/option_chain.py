import copy
import os
import sys
import threading
import time
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import xlwings as xw
from kiteconnect import KiteConnect
from py_vollib.black_scholes.greeks.analytical import delta, gamma, rho, theta, vega
from py_vollib.black_scholes.implied_volatility import implied_volatility

print("--- Option Chain ---")
api_key = input("Enter Kite API Key: ").strip()
access_token = input("Enter Kite Access Token: ").strip()
sheet_name = input("Enter Sheet Name:").strip()
file_name = "TradeViaPython.xlsm"
sheet_name = f"OC_{sheet_name}"

kite = KiteConnect(api_key=api_key)
kite.set_access_token(access_token=access_token)

try:
    kite.margins()
except Exception:
    print("Login Failed !!!")
    sys.exit()

if not os.path.exists(file_name):
    try:
        wb = xw.Book()
        wb.save(file_name)
        wb.close()
    except Exception as e:
        print(f"Error creating excel file: {e}")
        sys.exit()

w = xw.Book(file_name)

try:
    wb.sheets(sheet_name)
except Exception:
    wb.sheets.add(sheet_name)

oc = wb.sheets(sheet_name)

oc.range("a:b").value = oc.range("d7:e33").value = oc.range("g:bd").value = None

exchange = None
while True:
    if exchange is None:
        try:
            exchange = pd.DataFrame(kite.instruments("NFO"))
            break
        except Exception:
            print("Exchange Download Error ....")
            time.sleep(10)
df = pd.DataFrame({"FNO Symbol": list(exchange["name"].unique())})
df = df.set_index("FNO Symbol", drop=True)
oc.range("a1").value = df

(
    oc.range("d2").value,
    oc.range("d3").value,
    oc.range("d4").value,
    oc.range("d5").value,
) = ("Symbol==>>", "Option Expiry==>>", "Fut Expiry==>>", "Calc Base Fut==>>")

try:
    oc.range("d2:e5").api.Borders.Weight = 3
    oc.range("d7:e33").api.Borders.Weight = 2
    oc.range("g:bd").api.Borders.Weight = 1
except Exception:
    pass

pre_symbol = pre_oc_exipry = pre_fut_expiry = ""
oc_expiries_list = []
fut_expiries_list = []
instrument_dict = {}
pre_day_oi = {}
stop_thread = False


def get_oi(data):
    global prev_day_oi, kite, stop_thread
    for symbol, v in data.items():
        if stop_thread:
            break
        while True:
            try:
                pre_day_oi[symbol]
                break
            except Exception:
                try:
                    pre_day_data = kite.historical_data(
                        v["token"],
                        (datetime.now() - timedelta(days=30)).date(),
                        (datetime.now() - timedelta(days=1)).date(),
                        "day",
                        oi=True,
                    )
                    try:
                        pre_day_oi[symbol] = pre_day_data[-1]["oi"]
                    except Exception:
                        pre_day_oi[symbol] = 0
                    break
                except Exception:
                    time.sleep(0.5)


print("Excel: Started")
while True:
    inp_symbol, inp_oc_expiry, inp_fut_expiry, inp_cal_base_fut = (
        oc.range("e2").value,
        oc.range("e3").value,
        oc.range("e4").value,
        oc.range("e5").value,
    )
    if (
        pre_symbol != inp_symbol
        or pre_oc_exipry != inp_oc_expiry
        or pre_fut_expiry != inp_fut_expiry
    ):
        oc.range("g:bd").value = oc.range("d7:e33").value = None
        instrument_dict = {}
        stop_thread = True
        time.sleep(2)
        if pre_symbol != inp_symbol:
            oc.range("b:b").value = None
            oc_expiries_list = []
            fut_expiries_list = []
        pre_symbol = inp_symbol
        pre_oc_exipry = inp_oc_expiry
        pre_fut_expiry = inp_fut_expiry
    if inp_symbol is not None:
        try:
            if not oc_expiries_list:
                df = copy.deepcopy(exchange)
                df = df[df["name"] == inp_symbol]
                df = df[df["segment"] == "NFO-OPT"]
                oc_expiries_list = sorted(list(df["expiry"].unique()))
                df = pd.DataFrame({"Option Expiry Date", oc_expiries_list})
                df = df.set_index("Option Expiry Date", drop=True)
                oc.range("b6").value = df
            if not fut_expiries_list:
                df = copy.deepcopy(exchange)
                df = df[df["name"] == inp_symbol]
                df = df[df["segment"] == "NFO-FUT"]
                fut_expiries_list = sorted(list(df["expiry"].unique()))
                df = pd.DataFrame({"FUT Expiry Date", fut_expiries_list})
                df = df.set_index("FUT Expiry Date", drop=True)
                oc.range("b1").value = df
            if (
                not instrument_dict
                and inp_oc_expiry is not None
                and inp_fut_expiry is not None
            ):
                df = copy.deepcopy(exchange)
                df = df[df["name"] == inp_symbol]
                df = df[df["segment"] == "NFO-OPT"]
                df = df[df["expiry"] == inp_oc_expiry.date()]
                lot_size = list(df["lot_size"])[0]
                for i in df.index:
                    instrument_dict[f'NFO:{df["tradingsymbol"][i]}'] = {
                        "strikePrice": float(df["strike"][i]),
                        "instrumentType": df["instrument_type"][i],
                        "token": df["instrument_token"][i],
                    }

                df = copy.deepcopy(exchange)
                df = df[df["name"] == inp_symbol]
                df = df[df["segment"] == "NFO-FUT"]
                df = df[df["expiry"] == inp_fut_expiry.date()]
                lot_size = list(df["lot_size"])[0]
                for i in df.index:
                    fut_instrument = f'NFO:{df["tradingsymbol"][i]}'
                    instrument_dict[f'NFO:{df["tradingsymbol"][i]}'] = {
                        "strikePrice": float(df["strike"][i]),
                        "instrumentType": df["instrument_type"][i],
                        "token": df["instrument_token"][i],
                    }

                stop_thread = False
                thread = threading.Thread(target=get_oi, args=(instrument_dict,))
                thread.start()

            option_data = {}
            fut_data = {}
            spot_data = {}
            vix_data = {}

            spot_instrument = (
                "NSE:NIFTY 50"
                if inp_symbol == "NIFTY"
                else (
                    "NSE:NIFTY BANK"
                    if inp_symbol == "BANKNIFTY"
                    else f"NSE:{inp_symbol}"
                )
            )
            list_of_symbols = list(instrument_dict.keys())
            list_of_symbols.append(spot_instrument)
            list_of_symbols.append("NSE:INDIA VIX")
            tick_data = kite.quote(list_of_symbols).items()

            for symbol, values in tick_data:
                if symbol == spot_instrument:
                    spot_data = values
                elif symbol == "NSE:INDIA VIX":
                    vix_data = values
                elif symbol == fut_instrument:
                    fut_data = values
                else:
                    try:
                        try:
                            option_data[symbol]
                        except Exception:
                            option_data[symbol] = {}
                        option_data[symbol]["Strike_Price"] = instrument_dict[symbol][
                            "strikePrice"
                        ]
                        option_data[symbol]["instrument_Type"] = instrument_dict[
                            symbol
                        ]["instrumentType"]
                        option_data[symbol]["LTP"] = values["last_price"]
                        option_data[symbol]["LTP_Change"] = (
                            values["last_price"] - values["ohlc"]["close"]
                            if values["last_price"] != 0
                            else 0
                        )
                        option_data[symbol]["LTT"] = values["last_trade_time"]
                        option_data[symbol]["Total_Buy_Qunatity"] = values[
                            "buy_quantity"
                        ]
                        option_data[symbol]["Total_Sell_Qunatity"] = values[
                            "sell_quantity"
                        ]
                        option_data[symbol]["Average_Price"] = values["average_price"]
                        option_data[symbol]["Open"] = values["open"]
                        option_data[symbol]["High"] = values["high"]
                        option_data[symbol]["Low"] = values["low"]
                        option_data[symbol]["Best_Bid_Price"] = values["depth"]["buy"][
                            0
                        ]["price"]
                        option_data[symbol]["Best_Ask_Price"] = values["depth"]["sell"][
                            0
                        ]["price"]
                        option_data[symbol]["Prev_Close"] = values["ohlc"]["close"]
                        option_data[symbol]["Total_Traded_Volume"] = values["volume"]
                        option_data[symbol]["OI"] = int(values["oi"] / lot_size)
                        try:
                            option_data[symbol]["OI_Change"] = int(
                                (values["oi"] - pre_day_oi[symbol]) / lot_size
                            )
                        except Exception:
                            option_data[symbol]["OI_Change"] = None

                        name_surfix = "(Fut)" if inp_cal_base_fut else "(Spot)"
                        last_price = (
                            fut_data["last_price"]
                            if inp_cal_base_fut
                            else spot_data["last_price"]
                        )
                        strike_price = instrument_dict[symbol]["strikePrice"]
                        if instrument_dict[symbol]["instrumentType"] == "CE":
                            option_data[symbol][f"Intrinsic_Value {name_surfix}"] = (
                                last_price - strike_price
                            )
                            option_data[symbol][f"Time_Value {name_surfix}"] = (
                                values["last_price"] - last_price - strike_price
                            )
                        else:
                            option_data[symbol][f"Intrinsic_Value {name_surfix}"] = (
                                strike_price - last_price
                            )
                            option_data[symbol][f"Time_Value {name_surfix}"] = values[
                                "last_price"
                            ] - (strike_price - last_price)

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
                                    / timedelta(days=1)
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

                        greek = greeks(
                            values["last_price"],
                            inp_oc_expiry.date(),
                            last_price,
                            strike_price,
                            0.1,
                            instrument_dict[symbol]["instrumentType"],
                        )
                        for k, v in greek.items():
                            option_data[symbol][f"{k} {name_surfix}"] = v
                    except Exception as e:
                        print(e)
                        pass

            df = pd.DataFrame(option_data).transpose()
            ce_df = df[df["Instrument_Type"] == "CE"]
            ce_df = ce_df.rename(columns={i: f"CE_{i}" for i in list(ce_df.keys())})
            ce_df.index = ce_df["CE_Strike_Price"]
            ce_df = ce_df.drop(["CE_Strike_Price"], axis=1)
            ce_df["Strike"] = ce_df.index

            pe_df = df[df["Instrument_Type"] == "PE"]
            pe_df = pe_df.rename(columns={i: f"PE_{i}" for i in list(pe_df.keys())})
            pe_df.index = pe_df["PE_Strike_Price"]
            pe_df = pe_df.drop(["PE_Strike_Price"], axis=1)

            df = pd.concat([ce_df, pe_df], axis=1).sort_index()
            df = df.replace(np.nan, 0)
            df["Strike"] = df.index

            total_profit_loss = {}
            for i in df.index:
                itm_call = df[df.index < i]
                itm_call_loss = (i - itm_call.index) * itm_call["CE_OI"]

                itm_put = df[df.index > i]
                itm_put_loss = (itm_put.index - i) * itm_put["PE_OI"]

                total_profit_loss[sum(itm_call_loss) + sum(itm_put_loss)] = i
            df.index = [np.nan] * len(df)

            try:
                fut_change_oi = fut_data["oi"] - pre_day_oi[fut_instrument]
            except Exception:
                fut_change_oi = 0

            oc.range("d7").value = [
                ["Spot LTP", spot_data["last_price"]],
                ["FUT LTP", fut_data["last_price"]],
                ["VIX LTP", vix_data["last_price"]],
                [
                    "Spot LTP Change",
                    spot_data["last_price"] - spot_data["ohlc"]["close"],
                ],
                ["FUT LTP Change", fut_data["last_price"] - fut_data["ohlc"]["close"]],
                ["VIX LTP Change", vix_data["last_price"] - vix_data["ohlc"]["close"]],
                ["", ""],
                ["FUT OI", fut_data["oi"]],
                ["FUT Change in OI", fut_change_oi],
                ["", ""],
                ["Total Call OI", sum(list(df["CE_OI"]))],
                ["Total Put OI", sum(list(df["PE_OI"]))],
                ["Total Call Change in OI", sum(list(df["CE_OI_Change"]))],
                ["Total Put Change in OI", sum(list(df["PE_OI_Change"]))],
                ["", ""],
                ["Max Call OI", max(list(df["CE_OI"]))],
                ["Max Put OI", max(list(df["PE_OI"]))],
                [
                    "Max Call OI Strike",
                    list(df[df["CE_OI"] == max(list(df["CE_OI"]))]["Strike"])[0],
                ],
                [
                    "Max Put OI Strike",
                    list(df[df["PE_OI"] == max(list(df["PE_OI"]))]["Strike"])[0],
                ],
                ["", ""],
                ["Max Call Change in OI", max(list(df["CE_OI_Change"]))],
                ["Max Put Change in OI", max(list(df["PE_OI_Change"]))],
                [
                    "Max Call Change in OI Strike",
                    list(
                        df[df["CE_OI_Change"] == max(list(df["CE_OI_Change"]))][
                            "Strike"
                        ]
                    )[0],
                ],
                [
                    "Max Put Change in OI Strike",
                    list(
                        df[df["PE_OI_Change"] == max(list(df["PE_OI_Change"]))][
                            "Strike"
                        ]
                    )[0],
                ],
                ["", ""],
                [
                    "PCR",
                    round(
                        (
                            sum(list(df["PE_OI"])) / sum(list(df["CE_OI"]))
                            if sum(list(df["CE_OI"])) != 0
                            else 0
                        ),
                        2,
                    ),
                ],
                [
                    "Max Pain Strike",
                    total_profit_loss[min(list(total_profit_loss.keys()))],
                ],
            ]
            oc.range("g1").value = df
        except Exception as e:
            print(e)
            pass

from kite_trade import KiteApp, get_enctoken

user_id = ""
password = ""
twofa = ""

enctoken = get_enctoken(userid=user_id, password=password, twofa=twofa)
kite = KiteApp(enctoken=enctoken)

print(kite.margins())
print(kite.orders())
print(kite.positions())

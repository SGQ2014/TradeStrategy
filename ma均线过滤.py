from tqsdk import TqApi, TqAuth, TargetPosTask,tafunc,TqReplay
import talib as tb
import pandas as pd
from datetime import date
'''

'''
account=[["13362207470", "20091841"],["13738127551", "20091841"],["18397966326","20091841"],
["15381198206","20091841"],["15268575012","20091841"],["15868144962","20091841"],["17764561979","20091841"]]
lables="SHFE.rb2201"
api = TqApi(auth=TqAuth(account[5][0],account[5][1]))
BigKline = api.get_kline_serial(lables, 60*15)
TradeKline = api.get_kline_serial(lables, 60*3)
position = api.get_position(lables)
# 创建 rb2201 的目标持仓 task，该 task 负责调整 rb2201 的仓位到指定的目标仓位
target_pos_near = TargetPosTask(api, lables)
def crossup(tradeKline,amaKline):
    if tradeKline.iloc[-2]<amaKline.iloc[-2] and tradeKline.iloc[-1]>amaKline.iloc[-1]:
        return True
    else:
        return False

def crossdown(tradeKline,amaKline):
    if tradeKline.iloc[-2]>amaKline.iloc[-2] and tradeKline.iloc[-1]<amaKline.iloc[-1]:
        return True
    else:
        return False

lossprice = 0
entryprice = 0
    
while True:
    """ if api.is_changing(TradeKline.iloc[-1], "datetime") or api.is_changing(BigKline.iloc[-1], "datetime"): """
    api.wait_update()
    
    if api.is_changing(TradeKline.iloc[-1], "close"):
        BmaValue= tafunc.ma(BigKline.close, 20)
        tmaValue= tafunc.ma(TradeKline.close,40)
      
        if BigKline.iloc[-1].close > BmaValue.iloc[-1] and crossup(TradeKline.close,tmaValue) and position.pos==0:
            print("目标持仓: 多仓建立")
            # 设置目标持仓为正数表示多头，负数表示空头，0表示空仓
            target_pos_near.set_target_volume(1)
            entryprice = TradeKline.iloc[-1].close
            lossprice = min(TradeKline.iloc[-1].low,TradeKline.iloc[-2].low,TradeKline.iloc[-3].low,TradeKline.iloc[-4].low,TradeKline.iloc[-5].low)
            print(lossprice,entryprice)
        elif BigKline.iloc[-1].close < BmaValue.iloc[-1] and crossdown(TradeKline.close,tmaValue) and position.pos==0:
            print("目标持仓: 空仓建立")
            target_pos_near.set_target_volume(-1)
            lossprice = max(TradeKline.iloc[-1].high,BigKline.iloc[-2].high,BigKline.iloc[-3].high,BigKline.iloc[-4].high,BigKline.iloc[-5].high)
            entryprice = TradeKline.iloc[-1].close
            print(lossprice,entryprice)
        #多头平仓
        elif ((lossprice > TradeKline.iloc[-1].close) and (position.pos>0)):
            print(lossprice,TradeKline.iloc[-1].close)
            target_pos_near.set_target_volume(0)
        elif (((entryprice-lossprice) <(TradeKline.iloc[-1].close-entryprice) and crossdown(TradeKline.close,tmaValue)) and (position.pos>0)):
            print((entryprice-lossprice),(TradeKline.iloc[-1].close-entryprice))
            target_pos_near.set_target_volume(0)
        #空头平仓
        elif (lossprice <TradeKline.iloc[-1].close and (position.pos<0)) or (((lossprice-entryprice) < (entryprice - TradeKline.iloc[-1].close) and crossdown(TradeKline.close,tmaValue)) and (position.pos<0)):
            print(lossprice,TradeKline.iloc[-1].close)
            target_pos_near.set_target_volume(0)



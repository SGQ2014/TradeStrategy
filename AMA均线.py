from tqsdk import TqApi, TqAuth, TargetPosTask,tafunc,TqReplay
import talib as tb
import pandas as pd
from datetime import date
'''

'''
account=[["13362207470", "20091841"],["13738127551", "20091841"],["18397966326","20091841"],
["15381198206","20091841"],["15268575012","20091841"],["15868144962","20091841"],["17764561979","20091841"]]
lables="SHFE.rb2201"
api = TqApi(auth=TqAuth(account[1][0],account[1][1]))
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
        BAmaValue= tb.KAMA(BigKline.close,timeperiod=30)
        tAmaValue= tb.KAMA(TradeKline.close,timeperiod=30)
        print(BigKline.iloc[-1].close,BAmaValue.iloc[-1],TradeKline.iloc[-1].close,tAmaValue.iloc[-1],TradeKline.iloc[-2].close,tAmaValue.iloc[-2],TradeKline.datetime)
        if BigKline.iloc[-1].close > BAmaValue.iloc[-1] and crossup(TradeKline.close,tAmaValue) and position.pos_long_his==0 and position.pos_long_today==0:
            print("目标持仓: 多仓建立",TradeKline.datetime)
            # 设置目标持仓为正数表示多头，负数表示空头，0表示空仓
            target_pos_near.set_target_volume(2)
            lossprice = min(BigKline.iloc[-1].low,BigKline.iloc[-2].low,BigKline.iloc[-3].low,BigKline.iloc[-4].low,BigKline.iloc[-5].low)
        elif BigKline.iloc[-1].close < BAmaValue.iloc[-1] and crossdown(TradeKline.close,tAmaValue) and position.pos_short_his==0 and position.pos_short_today==0:
            print("目标持仓: 空仓建立",TradeKline.datetime)
            target_pos_near.set_target_volume(-2)
            lossprice = min(BigKline.iloc[-1].low,BigKline.iloc[-2].low,BigKline.iloc[-3].low,BigKline.iloc[-4].low,BigKline.iloc[-5].low)
        elif lossprice <TradeKline.iloc[-1].close or crossdown(TradeKline.close,tAmaValue) and (position.pos_long_his>0 or position.pos_long_today>0):
            print("目标持仓: 多头平仓",TradeKline.datetime)
            target_pos_near.set_target_volume(0)
        elif crossup(TradeKline.close,tAmaValue) and (position.pos_short_his>0 or position.pos_short_today>0):
            print("目标持仓: 空头平仓",TradeKline.datetime)
            target_pos_near.set_target_volume(0)



from numpy.lib.function_base import select
from tqsdk import (TargetPosTask,
                   TqSim, TqApi,
                   TqBacktest, ta,
                   tafunc,TqAuth)
from datetime import date, timedelta
import numpy as np
import pandas as pd

account=[["13362207470", "20091841"],["13738127551", "20091841"],["18397966326","20091841"],
["15381198206","20091841"],["15268575012","20091841"],["15868144962","20091841"],["17764561979","20091841"]]
lables="SHFE.rb2201"
class Deviation_Macd(object):
    def __init__(self, symbol):
        self.api = TqApi(auth=TqAuth(account[5][0],account[5][1]))
        self.kline = self.api.get_kline_serial(symbol, 60*15)
        self.target_pos = TargetPosTask(self.api, symbol)
        self.position = self.api.get_position(symbol)
        self.quote = self.api.get_quote(symbol)
        self.macd = 0
        self._1owest_md = []
        self._highest_md = []
        self.lowest = []
        self.highest = []
        self.var = {
            'crosS_upID': np.nan,
            'cross_downID': np.nan,
            'dt': np.nan,
            'cross_flag_L': 0,
            'cross_flag_H': 0,
            '_lowest_md': 0,
            '_highest_md': 0}

    def on_kline(self):
        self.macd = ta.MACD(self.kline, 12, 26, 9)
        self.kline['MACDValue'] = self.macd["diff"]
        self. kline['AvgMACD'] = self.macd["dea"]
        self. kline['MACDDiff '] = self.macd["bar"]
        self. kline['零轴'] = 0
        self.kline['cross_up'] = tafunc.crossup(
            self.kline['MACDValue'], self.kline['AvgMACD'])
        self.kline['cross_down'] = tafunc.crossdown(
            self.kline['MACDValue'], self.kline['AvgMACD'])
        self.kline['trend_long'] = tafunc.crossup(
            self.kline['AvgMACD'], self.kline['零轴'])
        self. kline[' trend_short'] = tafunc.crossdown(
            self.kline['AvgMACD'], self.kline['零轴'])

    def on_dev_down(self):
        if self.api.is_changing(self.kline.iloc[-1], 'datetime'):
            self.var['dt'] = pd.to_datetime(
                self.kline.datetime.iloc[-2]) + timedelta(hours=8)
            if self.var['cross_flag_L'] == 0:
                if self.kline['trend_short'].iloc[-2] == 1:
                    self.var["crosS_downID"] = self.kline. id.iloc[-2]
                    self.var['cross_flag_L'] = -1
            elif self.var['cross_flag_L'] == -1:
                if self.kline['cross_up'] .iloc[-2] == 1 and self.kline['AvgMACD'] .iloc[-2] < 0:
                    self.var["cross_upID"] = self.kline. id.iloc[-2]
                    print("金叉", self.var["cross_upID"])
                    self._lowest_md.append(self.kline['MACDValue'][int(
                        self.var["cross_downID"])-int(self.kline.id.iloc[-2]):].min())
                    self.lowest.append(self.kline['low'][int(
                        self.var["cross_downID"])-int(self.kline. id.iloc[-2]):].min())
                    print(self.var['dt'])
                if self.kline['cross_down'].iloc[-2] == 1 and self.kline['AvgMACD'].iloc[-2] < 0:
                    self .var["cross_downID"] = self.kline. id.iloc[-2]
                else:
                    if self.kline['trend_long'].iloc[-2] == 1:
                        self.var["cross_downID"] = np.nan
                        self.var['cross_flag_L'] = 0
                        self._1owest_md = []
                        self.lowest = []

    def on_deV_up(self):
        if self .api.is_changing(self.kline.iloc[-1], 'datetime'):
            self .var['dt'] = pd.to_datetime(
                self.kline.datetime .iloc[-2]) + timedelta(hours=8)
            print("时间: ", self. var['dt'])
            if self.var['cross_flag_H'] == 0:
                if self.kline['trend_long'].iloc[-2] == 1:
                    self.var["cross_upID"] = self.kline. id.iloc[-2]
                    self.var['cross_flag_H'] = 1
                    print("多头趋势", self.var["cross_upID"])
                    print("时间: ", self.var['dt'])
            elif self.var['cross_flag_H'] == 1:
                if self.kline['cross_down'] .iloc[-2] == 1 and self.kline['AvgMACD'] .iloc[-2] > 0:
                    self.var["cross_downID"] = self.kline. id.iloc[-2]
                    print("上涨死叉", self.var["cross_downID"])
                    self._highest_md.append(
                        self.kline['MACDValue'][int(self.var["cross_upID"]) - int(self.kline.id.iloc[-2]):] .max())
                    self.highest.append(self.kline['high'][int(
                        self .var["cross_upID"])-int(self.kline. id.iloc[-2]):] .max())
                    print(self.var['dt'])
                    print(self._highest_md)
                    print(self. highest)
                if self.kline['cross_up'].iloc[-2] == 1 and self.kline['AvgMACD'].iloc[-2] > 0:
                    self.var["cross_upID"] = self.kline.id.iloc[-2]
                else:
                    if self.kline['trend_short'].iloc[-2] == 1:
                        self.var["cross_upID"] = np.nan
                        self.var['cross_flag_H'] = 0
                        self._highest_md = []
                        self.highest = []

    def on_bar(self):
        if self.position.pos_long == 0 and self.position.pos_short == 0:
            if self.api.is_changing(self.kline.iloc[-1], 'datetime'):
                if len(self._lowest_md) >= 2:
                    if self._lowest_md[-1] > self._lowest_md[-2] and self.lowest[-1] < self.lowest[-2]:
                        self.target_pos.set_target_volume(1)
                if len(self._highest_md) >= 2:
                    if self._highest_md[-1] < self._highest_md[-2] and self.highest[-1] > self.highest[-2]:
                        self.target_pos.set_target_volume(-1)
                else:
                    if len(self._lowest_md) < 1:
                        pass
                    if len(self._highest_md) < 1:
                        pass
                    else:
                        print(self._lowest_md)
                        print(self. lowest)
                        print(self._highest_md)
                        print(self. highest)
        else:
            if self.position.pos_long > 0:
                self . target_pos.set_target_volume(0)
                del self._lowest_md[-2]
                del self . lowest[-2]
            elif self.position.pos_short > 0:
                self. target_pos.set_target_volume(0)
                del self._highest_md[-2]
                del self . highest[-2]

    def main(self):
        print("程序启动......")
        while True:
            self.api.wait_update()
            self.on_kline()
            self.on_dev_down()
            self.on_deV_up()
            self.on_bar()

if __name__ == '__main__':
    D_Macd = Deviation_Macd(symbol="KQ.i@SHFE.rb")
    D_Macd.main()

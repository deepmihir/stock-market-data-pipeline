import urllib.parse
import pandas as pd
import pytz,os
import requests
import json
from datetime import datetime, timedelta, time

TIMEZONE = pytz.timezone('Asia/Kolkata')


file_url = 'https://assets.upstox.com/market-quote/instruments/exchange/complete.csv.gz'
symboldf = pd.read_csv(file_url)
symboldf['expiry'] = pd.to_datetime(symboldf['expiry']).apply(lambda x: x.date())
symboldf = symboldf[symboldf.exchange=='NSE_EQ']

df = pd.read_csv("EQUITY_L.csv")

inList = 'NSE_EQ|' + df[' ISIN NUMBER']

symboldf = symboldf[symboldf.instrument_key.isin(inList)]

def getHistoricalData(symInfo):
  res = None
  try :
    parseInstrument = urllib.parse.quote(symInfo.instrument_key)
    fromDate = (datetime.now(TIMEZONE) - timedelta(days=10000)).strftime("%Y-%m-%d")
    todate = datetime.now(TIMEZONE).strftime("%Y-%m-%d")
    url = f"https://api.upstox.com/v2/historical-candle/{parseInstrument}/day/{todate}/{fromDate}"
    print(url)
    res = requests.get(url, headers={'accept':'application/json'},params={},timeout=5.0)

    candlesRes = res.json()
    if 'data' in candlesRes and 'candles' in candlesRes['data'] and candlesRes['data']['candles']:
      candleData = pd.DataFrame(candlesRes['data']['candles'])
      candleData.columns = ['date','open','high','low','close','vol','oi']
      candleData['date'] = pd.to_datetime(candleData['date']).dt.tz_convert('Asia/Kolkata')
      candleData['symbol'] = symInfo.tradingsymbol
      print(symInfo.tradingsymbol,len(candleData))
      return candleData
    # return candlesRes
    else:
      print('No data')
  except Exception as e:
    raise(e)
  

candlesList = []
for i in symboldf.index:
  res = getHistoricalData(symboldf.loc[i])
  if res is not None:
    candlesList.append(res)
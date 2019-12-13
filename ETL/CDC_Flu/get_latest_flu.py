db_string= 'postgresql+psycopg2://postgres:<MY RDS_PASSWORD>@<MY_RDS_HOST_NAME>/sdohdb'

import traceback
import urllib3
import xmltodict
import json

def getxml():
    url = "https://www.cdc.gov/flu/weekly/flureport.xml"
    http = urllib3.PoolManager()
    response = http.request('GET', url)
    try:
        data = xmltodict.parse(response.data)
    except:
        print("Failed to parse xml from response (%s)" % traceback.format_exc())
    return data

fludict = getxml()

import string
flu_list=[]
for item in fludict['flureport']['timeperiod']:
  row_dict = {}
  for subitem in item['state']:
    label = subitem['label']
    if label == 'No Activity':
        spread = 1
    elif label == 'Sporadic':
        spread = 2
    elif label == 'Local Activity':
        spread = 3
    elif label == 'Regional':
        spread = 4
    elif label == 'Widespread':
        spread = 5
    else:
        spread = 0
    row_dict={'week':item['@number'], 'year':item['@year'],'state':subitem['abbrev'],'spread':spread}
    #print(row_dict)
    flu_list.append(row_dict)
    
import pandas as pd
df = pd.DataFrame(flu_list)
df['yearweek'] = df['year'].astype(str) +"-"+ df['week'].astype(str)
df.drop(['year', 'week'], axis=1,inplace=True)
df.set_index('yearweek',inplace=True)

from sqlalchemy import create_engine
from sqlalchemy.types import Integer
engine = create_engine(db_string)
df.to_sql('cdc_flu', con=engine, if_exists='replace',schema='public',dtype={'week': Integer(),})

with engine.connect() as con:
    rs = con.execute("alter table cdc_flu add column weekending DATE")
    rs = con.execute("update cdc_flu set weekending = to_date(yearweek,'yyyy-ww')+4")
import pandas as pd
import numpy as np
import twstock
from datetime import datetime, timedelta
import streamlit as st

from dash import Dash, html, dash_table, dcc, callback, Output, Input
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import webbrowser
from threading import Timer

now = datetime.strftime(datetime.now(),'%Y%m%d')
before = datetime.now() - timedelta(days=90)
stockyear,stockmonth = int(before.year) ,int(before.month)

st.set_page_config(layout="wide")
st.title('Stock Visualiztion Dashboard :sunglasses:')

# Using "with" notation
st.sidebar.write("""#### Choose your Stock""")
with st.form(key ='Form1'):
    with st.sidebar:
        input_stock = st.sidebar.text_input('Please enter the stock name',
                                            label_visibility= 'hidden',
                                            placeholder='輸入股票代碼')
        stock_number = st.sidebar.number_input('Please enter the stock name',
                                        value=1.382,
                                        placeholder='倍率',
                                        label_visibility= 'hidden')
        submitted = st.form_submit_button(label = 'Search 🔎')





def get_history_stock_price(input_stock,stock_number,syear =stockyear,smonth=stockmonth,before=before):
    stock = twstock.Stock(input_stock)
    target_price = stock.fetch_from(syear, month=smonth)
    stock_df = pd.DataFrame(target_price)
    stock_df = stock_df[['date','open','high','low','close'	]]

    
    
    stock_df['高關價']  =  np.around(stock_df['low']+(stock_df['high'] - stock_df['low'])*stock_number,2)
    stock_df['中關價']  =  np.around((stock_df['high'] + stock_df['low'])/2,2)
    stock_df['低關價']  = np.around(stock_df['high']-(stock_df['high'] - stock_df['low'])*stock_number,2)
    stock_df['高關價'] = stock_df['高關價'].shift(periods=1)
    stock_df['中關價'] = stock_df['中關價'].shift(periods=1)
    stock_df['低關價'] = stock_df['低關價'].shift(periods=1)
    
    stock_df = stock_df[stock_df['date']>before]
    stock_df['date'] =stock_df['date'].apply(lambda x :datetime.strftime(x,'%Y-%m-%d'))
    

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        specs=[[{"type": "table"}],
            [{"type": "scatter"}]]
    )

    fig.add_trace(
        go.Scatter(
            x=stock_df["date"],
            y=stock_df["close"],
            text=stock_df["close"],
            mode ='lines+markers+text'
        ),
        row=2, col=1
    )
    
    
    
    fig.update_layout(xaxis = {'type' : 'category','tickangle':-90})
    
    if datetime.now().weekday()<5 and datetime.now().hour<14:
        temp = twstock.realtime.get(input_stock)
        real_time = pd.DataFrame({'date':datetime.strftime(datetime.now(),'%Y-%m-%d'),
                    'open':float(temp.get('realtime').get('open')),
                    'high':float(temp.get('realtime').get('high')),
                    'low':float(temp.get('realtime').get('low')),
                    'close':0},index = [0])
        stock_df = pd.concat([stock_df, real_time], ignore_index = True)
        # stock_df = stock_df.sort_values(by= ['date'],ascending=True)
        stock_df['高關價'].iloc[-1]  =  np.around(stock_df['low'].iloc[-2] +(stock_df['high'].iloc[-2] - stock_df['low'].iloc[-2])*stock_number,2)
        stock_df['中關價'].iloc[-1]   =  np.around((stock_df['high'].iloc[-2] + stock_df['low'].iloc[-2])/2,2)
        stock_df['低關價'].iloc[-1]   = np.around(stock_df['high'].iloc[-2]-(stock_df['high'].iloc[-2] - stock_df['low'].iloc[-2])*stock_number,2)
    
    elif datetime.now().hour>14 or datetime.now().weekday()>=5:
        temp = twstock.realtime.get(input_stock)
        real_time = pd.DataFrame({'date':datetime.strftime(datetime.now()+timedelta(days=1, hours=3),'%Y-%m-%d'),
                    'open':0,
                    'high':0,
                    'low':0,
                    'close':0}, index=[0])
        stock_df = pd.concat([stock_df, real_time], ignore_index = True)        
        stock_df['高關價'].iloc[-1]  =  np.around(stock_df['low'].iloc[-2] +(stock_df['high'].iloc[-2] - stock_df['low'].iloc[-2])*stock_number,2)
        stock_df['中關價'].iloc[-1]   =  np.around((stock_df['high'].iloc[-2] + stock_df['low'].iloc[-2])/2,2)
        stock_df['低關價'].iloc[-1]   = np.around(stock_df['high'].iloc[-2]-(stock_df['high'].iloc[-2] - stock_df['low'].iloc[-2])*stock_number,2)
    
    stock_df = stock_df.sort_values(by= ['date'],ascending=False)
    fig.add_trace(
        go.Table(
            header=dict(
            values=["日期", "開盤價", "最高價",
                    "最低價", "收盤價",'高關價','中關價','低關價'],
            font=dict(size=20),
            align="left"
        ),
            cells=dict(
                values=[stock_df[k].tolist() for k in stock_df.columns],
                align = "left")
        ),
        row=1, col=1
    )
    fig.update_layout(
        height=700,
        title_text=f'{twstock.codes[input_stock].name}/{input_stock}',
        title_font_size=45,
        showlegend=False,
        width = 1100,
        margin=dict(
        l=00,
        r=10,
        b=10,
        t=80
        ))
    
    st.plotly_chart(fig)
    return None

def main(input_stock,stock_number,stockyear,stockmonth,before):
    
    if submitted:
        get_history_stock_price(input_stock,stock_number,syear =stockyear,smonth=stockmonth,before=before)
        
    return None




if __name__ == '__main__':
    main(input_stock,stock_number,stockyear,stockmonth,before)

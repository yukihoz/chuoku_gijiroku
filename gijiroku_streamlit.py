#from tracemalloc import start
#from turtle import window_width
import numpy as np
from st_aggrid import AgGrid
import pandas as pd
import streamlit as st
import pydeck as pdk #3Dマッピング
#import plotly.express as px 
import MeCab
mecab = MeCab.Tagger()
import matplotlib.pyplot as plt
from wordcloud import WordCloud
font_path = 'Corporate-Logo-Bold-ver2.otf'

#pd.set_option('display.max_colwidth', 0)

#st.set_page_config(layout="wide")
st.title('中央区の区議会')

logs = pd.read_csv('./議事録2015-2019u.csv', encoding='UTF-8')#df_jp_indとしてDFで読み込み
giin_list = logs['人分類'].unique()

st.header('■ワードクラウド')
option_selected_g = st.selectbox(
    'どれか選択してね',
    giin_list
)

start_year, end_year = st.select_slider(
     '対象年度を選んでね',
     options=['2015', '2016', '2017', '2018', '2019', '2020', '2021'],
     value=('2015', '2019'))

start_year = int(start_year)
end_year = int(end_year)

#pd.to_numeric(start_year)

#pd.to_numeric(end_year)
#logs['年度'] = logs['年度'].astype(int)


pd.set_option('display.max_rows', 10000)

logs_contents_temp = logs[(logs['人分類'].str.contains(option_selected_g)) & (logs['内容分類']== "質問" ) & (logs['年度'] >= start_year) & (logs['年度'] <= end_year)]

logs_contents_temp_show = logs_contents_temp[["年月日","会議","内容"]]

logs_contents_temp_moji = logs_contents_temp.groupby('年度').sum()# 年度ごとの文字数

#文字カウント
logs_contents_temp_moji = logs_contents_temp_moji['文字数']

#logs_contents_temp_moji = logs_contents_temp.sum(level=2)
#logs_contents_temp_moji = pd.DataFrame({'value': df.loc[logs_contents_temp['年度'] == "2015"],logs_contents_temp['文字数'].sum(),
#                                        'value': logs_contents_temp['文字数'][logs_contents_temp['年度'] == "2016"].sum(),
#                                        'value': logs_contents_temp['文字数'][logs_contents_temp['年度'] == "2017"].sum(),
#                                        'value': logs_contents_temp['文字数'][logs_contents_temp['年度'] == "2018"].sum(),
#                                        'value': logs_contents_temp['文字数'][logs_contents_temp['年度'] == "2019"].sum(),
#                                        'value': logs_contents_temp['文字数'][logs_contents_temp['年度'] == "2020"].sum()},
#                                        index = ['2015','2016','2017','2018','2019','2020'])

#チャート作成
st.bar_chart(logs_contents_temp_moji
            )
            
# ワードクラウド作成
logs_contents = logs_contents_temp['内容']

#logs_contents = logs['内容'][logs['人分類'].str.contains('|'.join(option_selected_g))]

f = open('temp.txt', 'w')#textに書き込み
f.writelines(logs_contents)
f.close()

#logs_contents_s = str(logs_contents)
text = open("temp.txt", encoding="utf8").read()
#text['列文字数'] = list(map(len, text['内容']))
#results = mecab.parse(logs_contents_s)
results = mecab.parse(text)
result = results.split('\n')[:-2][0]

nouns = []
for result in results.split('\n')[:-2]:
        if '名詞' in result.split('\t')[4]:
            nouns.append(result.split('\t')[0])
words = ' '.join(nouns)

#集計文字数表示
st.metric(label="発言文字数", value=len(text))

stpwds = ["議会","文","場所","現在","ら","方々","こちら","性","化","場合","対象","一方","皆様","考え","それぞれ","意味","とも","内容","とおり","目","事業","つ","見解","検討","本当","議論","民","地域","万","確認","実際","先ほど","前","後","利用","説明","次","あたり","部分","状況","わけ","話","答弁","資料","半ば","とき","支援","形","今回","中","対応","必要","今後","質問","取り組み","終了","暫時","午前","たち","九十","八十","七十","六十","五十","四十","三十","問題","提出","進行","付託","議案","動議","以上","程度","異議","開会","午後","者","賛成","投票","再開","休憩","質疑","ただいま","議事","号","二十","平成","等","会","日","月","年","年度","委員","中央","点","区","委員会","賛成者","今","中央区","もの","こと","ふう","ところ","ほう","これ","私","わたし","僕","あなた","みんな","ただ","ほか","それ", "もの", "これ", "ところ","ため","うち","ここ","そう","どこ", "つもり", "いつ","あと","もん","はず","こと","そこ","あれ","なに","傍点","まま","事","人","方","何","時","一","二","三","四","五","六","七","八","九","十"]

wc = WordCloud(stopwords=stpwds, width=1280, height=720, background_color='white', font_path = font_path)
wc.generate(words)
wc.to_file('wc.png')
st.image('wc.png')
#plt.imshow(wc)
#logs_contents
#st.text(logs_contents_s)
#results

#logs_moji = pd.read_csv('./議事録2015-2019suma.csv', encoding='UTF-8')#df_jp_indとしてDFで読み込み

#selected_g = logs2 [(logs2['人分類'].str.contains(option_selected_g))]



#table作成
grid_options = {
    "columnDefs":[
    {
        "headerName":"年月日",
        "field":"年月日",
        "suppressSizeToFit":True,
        "autoHeight":True,

    },
    {
        "headerName":"会議名",
        "field":"会議",
        "suppressSizeToFit":True,
        "wrapText":True,
        "autoHeight":True,
        "maxWidth":200,
    },
    {
        "headerName":"発言内容",
        "field":"内容",
        "wrapText":True,
        "autoHeight":True,
        "suppressSizeToFit":True,
        "maxWidth":800,
    },
],
}

AgGrid(logs_contents_temp_show, grid_options)


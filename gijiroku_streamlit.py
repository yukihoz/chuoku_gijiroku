from st_aggrid import AgGrid
import pandas as pd
import streamlit as st

import MeCab
mecab = MeCab.Tagger()
import matplotlib.pyplot as plt
from wordcloud import WordCloud
font_path = 'Corporate-Logo-Bold-ver2.otf'
import altair as alt
#import datetime
from datetime import datetime, timedelta, timezone


st.set_page_config(layout="wide")
st.title(':face_with_monocle:  議会の議事録ビジュアライズ(β)@中央区')
st.subheader('「この政治家、どういう考えの人なんだろ？？」と思っても、議会の議事録とか眺めるのしんどいよね…:dizzy_face:')
st.markdown('　SNSとかで発信している政治家も最近は増えてきてますが、何やってるかよく分からない人の方が多いというのが実際のところではないでしょうか。一応議会とかに出席してあれこれやってるんだろうけど、その議事録とか見るのはだらだら長くてしんどい。')
st.markdown('　そういう人向けに、政治家の方々が議会でどういう発言をされているのかについて「文字解析の技術で1枚の画像としてざっくりと可視化してみよう！」というサービスを作ってみました（いわゆるワードクラウドというやつ）。')
st.markdown('　対象はわたしの住んでる東京都中央区議会、期間は2022年3月時点で入手できた2015年5月から2021年10月まで。')
st.markdown('　python + streamlitで作ってます。超初心者の習作なもので色々ツッコミどころはあるかと思います。こうすればもっと良いよ！とか教えてもらえると嬉しいです。一緒にやろうよ！という人がいてくれるともっと嬉しいです。コメント、ツッコミはお気軽に。')
st.markdown('**作った人：[ほづみゆうき](https://twitter.com/ninofku)**')

logs = pd.read_csv('./gijiroku2015-2021.csv', encoding='UTF-8')#dataframeとしてcsvを読み込み
giin_list_temp = pd.read_csv('./giin2015-2021.csv', encoding='UTF-8')
giin_list = giin_list_temp['氏名']

iinkai_list_temp = pd.read_csv('./iinkai2015-2021.csv', encoding='UTF-8')
iinkai_list = iinkai_list_temp['委員会']

st.header(':clipboard: 使い方')
st.markdown('　「:fork_and_knife: 検索条件」で条件を設定すると、その下の「:cake: 結果表示」に結果が表示されますよ。')
st.markdown('　基本的には政治家の名前を選択すればオッケー、もっと細かく見たければ「会議体」とか「年度」とかで絞ってみてください。')

st.header(':fork_and_knife: 検索条件')
# 議員選択
option_selected_g = st.selectbox(
    '政治家の名前をどれか選択してください。選んだ政治家の結果が表示されます。',
    giin_list
)

#委員会選択
with st.expander("■「会議体」での絞り込み", False):
#st.markdown(' ##### :books:「会議体」での絞り込み')
        option_selected_i = st.multiselect(
        '「XXXX委員会」とかの会議体で結果を絞りたい場合は使ってみてください。初期値では全部が選択されてます。',
        iinkai_list,
        ['臨時会','環境建設委員会','企画総務委員会','区民文教委員会','少子高齢化対策特別委員会','築地等まちづくり及び地域活性化対策特別委員会','東京オリンピック・パラリンピック対策特別委員会','福祉保健委員会','防災等安全対策特別委員会','定例会','決算特別委員会','予算特別委員会','子ども子育て・高齢者対策特別委員会','築地等地域活性化対策特別委員会','全員協議会','コロナウイルス・防災等対策特別委員会','懲罰特別委員会','東京2020大会・晴海地区公共施設整備対策特別委員会'])
option_selected_i = '|'.join(option_selected_i)

#委員会選択のテキスト化（後の条件付けのため
f = open('temp_iinkai.txt', 'w')#textに書き込み
f.writelines(option_selected_i)
f.close()
option_selected_i_txt = open("temp_iinkai.txt", encoding="utf8").read()

#st.markdown(' ##### :date:「年度」での絞り込み')
with st.expander("■「年度」での絞り込み", False):
#年度選択
    start_year, end_year = st.select_slider(
    '最近の動向を知りたいとか、対象の年度で結果を絞りたい場合は使ってみてください。初期値では全部の年度が選択されてます。',
     options=['2015', '2016', '2017', '2018', '2019', '2020', '2021'],
     value=('2015', '2021'))

start_year = int(start_year)
end_year = int(end_year)

logs_contents_temp = logs[(logs['人分類'].str.contains(option_selected_g)) & (logs['委員会'].str.contains(option_selected_i_txt)) & (logs['内容分類']== "質問" ) & (logs['年度'] >= start_year) & (logs['年度'] <= end_year)]

logs_contents_temp_show = logs_contents_temp[["年月日","会議","内容"]]

logs_contents_temp_moji = logs_contents_temp.groupby('年度').sum()# 年度ごとの文字数

#文字カウント
logs_contents_temp_moji = logs_contents_temp_moji['文字数']

st.header(':cake: 結果表示')
#st.markdown('　「:fork_and_knife: 検索条件」で設定した範囲での発言内容についての結果が表示されます。')


# ワードクラウド作成
logs_contents = logs_contents_temp['内容']

f = open('temp.txt', 'w')#textに書き込み
f.writelines(logs_contents)
f.close()

text = open("temp.txt", encoding="utf8").read()

results = mecab.parse(text)
result = results.split('\n')[:-2][0]

nouns = []
for result in results.split('\n')[:-2]:
        if '名詞' in result.split('\t')[4]:
            nouns.append(result.split('\t')[0])
words = ' '.join(nouns)

#st.markdown('　#### :face_with_monocle: 文字解析の結果')
JST = timezone(timedelta(hours=+9), 'JST')
#dt_now = datetime.datetime.now()
dt_now = datetime.now(JST)

st.write('**[政治家名]**',option_selected_g, '**[対象年度]**',start_year,'-',end_year,'**[作成日時]**',dt_now)

stpwds = ["様","辺","なし","分","款","皆","さん","議会","文","場所","現在","ら","方々","こちら","性","化","場合","対象","一方","皆様","考え","それぞれ","意味","とも","内容","とおり","目","事業","つ","見解","検討","本当","議論","民","地域","万","確認","実際","先ほど","前","後","利用","説明","次","あたり","部分","状況","わけ","話","答弁","資料","半ば","とき","支援","形","今回","中","対応","必要","今後","質問","取り組み","終了","暫時","午前","たち","九十","八十","七十","六十","五十","四十","三十","問題","提出","進行","付託","議案","動議","以上","程度","異議","開会","午後","者","賛成","投票","再開","休憩","質疑","ただいま","議事","号","二十","平成","等","会","日","月","年","年度","委員","中央","点","区","委員会","賛成者","今","中央区","もの","こと","ふう","ところ","ほう","これ","私","わたし","僕","あなた","みんな","ただ","ほか","それ", "もの", "これ", "ところ","ため","うち","ここ","そう","どこ", "つもり", "いつ","あと","もん","はず","こと","そこ","あれ","なに","傍点","まま","事","人","方","何","時","一","二","三","四","五","六","七","八","九","十"]

wc = WordCloud(stopwords=stpwds, width=1280, height=720, background_color='white', font_path = font_path)
wc.generate(words)
wc.to_file('wc.png')
st.image('wc.png')
st.markdown('補足：更新するたびに表示位置などはビミョーに変わります。対象は名詞だけで、「それぞれ」や「問題」など、頻繁に使われるけど中身のないキーワードは除外してます。')

with st.expander("■ 年度単位での発言文字数の推移", False):
#st.markdown('　#### :chart_with_upwards_trend: 年度単位での発言文字数の推移')
    st.markdown('　それぞれの年度でどの程度発言されているのかを推移を示したものです。')
    #チャート作成
    st.bar_chart(logs_contents_temp_moji)
    #集計文字数表示
    st.metric(label="発言文字数", value=len(text))

    #table作成
with st.expander("■ 解析対象の文字列", False):
    #st.markdown('　#### :open_book: 解析対象の文字列')
    st.markdown('　上記の解析結果の対象となった文字列です。もうちょい細かく見たいこともあるかと思い表示させてみました（改行がうまくできてなくてすいません…）')
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

st.header(':paperclip: 情報参照元')
st.markdown('分析の元になっているデータは、[中央区議会 Webサイト](https://www.kugikai.city.chuo.lg.jp/index.html)の「会議録検索」からHTMLファイルをごっそりダウンロードして、その上であれこれ苦心して加工して作成しました。注意して作業はしたつもりですが、一部のデータが欠損等している可能性もありますのでご承知おきください。もし不備等ありましたら[ほづみゆうき](https://twitter.com/ninofku)まで声掛けいただけるとありがたいです。')

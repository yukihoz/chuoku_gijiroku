import random
from st_aggrid import AgGrid
import pandas as pd
import streamlit as st
from collections import Counter
from PIL import Image
import MeCab
mecab = MeCab.Tagger()
import matplotlib.pyplot as plt
from wordcloud import WordCloud
font_path = 'ShipporiMinchoB1-ExtraBold.ttf'
import altair as alt
from datetime import datetime, timedelta, timezone

# 幅を広くする
st.set_page_config(layout="wide")

# 冒頭の説明いろいろ
st.title(':face_with_monocle:  議会見える化プロジェクト(β)@東京都中央区')
st.subheader('「この政治家、どういう考えの人なんだろ？？」と思っても、議会の議事録とか眺めるのしんどいよね…:dizzy_face:')
st.markdown('　政治家って何やってるの？と思っても、、議会の議事録とか見るのはだらだら長くてしんどい。')
st.markdown('　そんな人向けに、政治家の議会での発言を1枚の画像で表示してみよう！」というサービスを作ってみました（いわゆるワードクラウドというやつ）。')
st.markdown('　対象はわたしの住んでる東京都中央区議会、期間は2022年3月時点で入手できた2015年5月から2022年5月まで。')
# 画像の読み込み
image = Image.open('jigazo.png')
st.image(image,width=100)
st.markdown('**作った人：[ほづみゆうき](https://twitter.com/ninofku)**')

#議事録キャッシュ
@st.cache_data
def load_csv(file_path, encoding="utf-8"):
    return pd.read_csv(file_path, encoding=encoding)

logs = load_csv('./gijiroku2015-2022.5.csv')
# 議事録CSVの読み込み
logs = pd.read_csv('./gijiroku2015-2022.5.csv', encoding='UTF-8')

# 議員リストCSVの読み込み（議事録csvから作れるはずだがやってない
giin_list_temp = pd.read_csv('./giin2015-2021.csv', encoding='UTF-8')
giin_list = giin_list_temp['氏名'] # 氏名だけを抜き出したdataframeを作る

# 委員会リストCSVの読み込み（議事録csvから作れるはずだがやってない
iinkai_list_temp = pd.read_csv('./iinkai2015-2021.csv', encoding='UTF-8')
iinkai_list = iinkai_list_temp['委員会'] # 委員会名だけを抜き出したdataframeを作る

# 使い方の説明
st.header(':clipboard: 使い方')
st.markdown('　政治家がランダムに選択され、その政治家のテキスト解析結果が「:cake: 結果表示」に表示されてます。下の「ランダム選択」ボタンを押すと別の人に変わります。')
st.markdown('　「:fork_and_knife: 検索条件」で条件を設定すると、政治家を選択したり「会議体」や「年度」で絞ったりなんかもできます。')

# 議員の名前をURLに持ってたらその人のWCを表示させ、なければランダム表示させる
query_params = st.experimental_get_query_params() # URLにあるクエリをqueary_paramsとして読み込む
if query_params: 
    option_selected_g_temp = query_params.get('giin', None)[0]
else:option_selected_g_temp = random.choice(giin_list)# クエリがなければランダム表示する

# ボタンを押すとランダムで選択される
if st.button('ランダム選択'):
    option_selected_g = random.choice(giin_list)
else:
    option_selected_g = option_selected_g_temp

st.header(':fork_and_knife: 検索条件')

# チェックを入れると、議員をリストから選択する
choice = st.checkbox('政治家を選択する')
if choice:
        option_selected_g = st.selectbox(
        '政治家の名前をどれか選択してください。選んだ政治家の結果が表示されます。',
        giin_list
    )

#対象とする委員会を選択する（指定せずに全件表示させて任意に消せるのが理想だが、現状は全部をゴリっと書いてる）
with st.expander("■「会議体」での絞り込み", False): # 折りたたみ
        option_selected_i = st.multiselect(
        '「XXXX委員会」とかの会議体で結果を絞りたい場合は使ってみてください。初期値では全部が選択されてます。',
        iinkai_list,
        ['臨時会','環境建設委員会','企画総務委員会','区民文教委員会','少子高齢化対策特別委員会','築地等まちづくり及び地域活性化対策特別委員会','東京オリンピック・パラリンピック対策特別委員会','福祉保健委員会','防災等安全対策特別委員会','定例会','決算特別委員会','予算特別委員会','子ども子育て・高齢者対策特別委員会','築地等地域活性化対策特別委員会','全員協議会','コロナウイルス・防災等対策特別委員会','懲罰特別委員会','東京2020大会・晴海地区公共施設整備対策特別委員会'])
        st.markdown('　※ 政治家を選択せずに絞り込みを設定すると勝手に人が変わっちゃいます。その場合は政治家を選択してください。')
option_selected_i = '|'.join(option_selected_i)

#選択した委員会のテキスト化して読み込み（後の条件付けのため　←　なんだったっけ？
f = open('temp_iinkai.txt', 'w')#textに書き込み
f.writelines(option_selected_i)
f.close()
option_selected_i_txt = open("temp_iinkai.txt", encoding="utf8").read()

#対象とする年度を選択する
with st.expander("■「年度」での絞り込み", False):# 折りたたみ
    start_year, end_year = st.select_slider(
    '最近の動向を知りたいとか、対象の年度で結果を絞りたい場合は使ってみてください。初期値では全部の年度が選択されてます。',
     options=['2015', '2016', '2017', '2018', '2019', '2020', '2021', '2022'], # 選択肢として表示する年
     value=('2019', '2022')) # 初期値
    st.markdown('　※ 政治家を選択せずに絞り込みを設定すると勝手に人が変わっちゃいます。その場合は政治家を選択してください。')

start_year = int(start_year)
end_year = int(end_year)

# 設定した条件の人、委員会、年度で議事録ファイルを抽出する
logs_contents_temp = logs[(logs['人分類'].str.contains(option_selected_g)) & (logs['委員会'].str.contains(option_selected_i_txt)) & (logs['年度'] >= start_year) & (logs['年度'] <= end_year)]

# 絞り込んだ議事録ファイルの特定列だけを抽出する
logs_contents_temp_show = logs_contents_temp[["年月日","人分類","内容分類","質問","回答","会議","内容","年度","文字数"]]

# 年度ごとに文字数を集計する
logs_contents_temp_moji = logs_contents_temp.groupby('年度').sum()

# 文字数の部分だけを抽出する
logs_contents_temp_moji = logs_contents_temp_moji['文字数']

st.header(':cake: 結果表示')
# 議事録CSVのうち、発言内容部分のみのデータを作成する
logs_contents = logs_contents_temp['内容']

# テキストファイルとして保存する
f = open('temp.txt', 'w')#textに書き込み
f.writelines(logs_contents)
f.close()

text = open("temp.txt", encoding="utf8").read()

# テキストをmecabで形態素解析する
results = mecab.parse(text)
result = results.split('\n')[:-2][0]

#エラー処理（足したところ
try:
    results = mecab.parse(text)
    if not results or results.strip() == "":
        st.error("形態素解析が失敗しました。入力テキストを確認してください。")
        raise ValueError("形態素解析結果が空です。")
except Exception as e:
    st.error(f"形態素解析中にエラーが発生しました: {e}")
    results = "解析に失敗しました"

if results == "解析に失敗しました":
    st.warning("解析が失敗したため、処理をスキップします。")
else:
    # 通常の処理を続行
    result = results.split('\n')[:-2][0]

# 名詞だけを抜き出す
nouns = []
for result in results.split('\n')[:-2]:
        if '名詞' in result.split('\t')[4]:
            nouns.append(result.split('\t')[0])
words = ' '.join(nouns)

# 日本時刻(JST)に設定する（後の作成日時表示のため
JST = timezone(timedelta(hours=+9), 'JST')
dt_now = datetime.now(JST)

# 対象の議員、年度、作成日時を表示する
st.write('**[政治家名]**',option_selected_g, '**[対象年度]**',start_year,'-',end_year,'**[作成日時]**',dt_now)

# ワードクラウドに使わない文字列を指定する
stpwds = ["視点","視点","認識","取組","辺り","具体","面","令和","様","辺","なし","分","款","皆","さん","議会","文","場所","現在","ら","方々","こちら","性","化","場合","対象","一方","皆様","考え","それぞれ","意味","とも","内容","とおり","目","事業","つ","見解","検討","本当","議論","民","地域","万","確認","実際","先ほど","前","後","利用","説明","次","あたり","部分","状況","わけ","話","答弁","資料","半ば","とき","支援","形","今回","中","対応","必要","今後","質問","取り組み","終了","暫時","午前","たち","九十","八十","七十","六十","五十","四十","三十","問題","提出","進行","付託","議案","動議","以上","程度","異議","開会","午後","者","賛成","投票","再開","休憩","質疑","ただいま","議事","号","二十","平成","等","会","日","月","年","年度","委員","中央","点","区","委員会","賛成者","今","中央区","もの","こと","ふう","ところ","ほう","これ","私","わたし","僕","あなた","みんな","ただ","ほか","それ", "もの", "これ", "ところ","ため","うち","ここ","そう","どこ", "つもり", "いつ","あと","もん","はず","こと","そこ","あれ","なに","傍点","まま","事","人","方","何","時","一","二","三","四","五","六","七","八","九","十"]

# ワードクラウドを作成する
wc = WordCloud(stopwords=stpwds, # 使わない文字列の指定
    width=1000, # サイズ・横
    height=1000, # サイズ・縦
    background_color='white', # 背景の色
    colormap='Dark2', # 文字の色のパターン
    #colormap='coolwarm', 
    font_path = font_path # フォントの場所
)
wc.generate(words)
wc.to_file('wc.png') # ファイルとして保存
st.image('wc.png') # 画像の表示

st.markdown('補足：更新するたびに表示位置などはビミョーに変わります。対象は名詞だけで、「それぞれ」や「問題」など、頻繁に使われるけど中身のないキーワードは除外してます。')

#集計した文字数を集計して表示する
st.metric(label="発言文字数", value=len(text))

with st.expander("■ 年度単位での発言文字数の推移", False):
    st.markdown('　それぞれの年度でどの程度発言されているのかを推移を示したものです。')
    # 年度ごとの文字数を集計してグラフにする
    st.bar_chart(logs_contents_temp_moji)
with st.expander("■ 解析対象の文字列", False):
    st.markdown('　上記の解析結果の対象となった文字列です。もうちょい細かく見たいこともあるかと思い表示させてみました。')
    # 解析対象の文字列の表示のためのテーブル設定
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
        "maxWidth":150,
    },
    {
        "headerName":"内容分類",
        "field":"内容分類",
        "suppressSizeToFit":True,
        "autoHeight":True,
    },
    {
        "headerName":"質問者",
        "field":"質問",
        "suppressSizeToFit":True,
        "wrapText":True,
        "maxWidth":100,
        "autoHeight":True,
    },
    {
        "headerName":"回答者",
        "field":"回答",
        "suppressSizeToFit":True,
        "wrapText":True,
        "maxWidth":100,
        "autoHeight":True,
    },
    {
        "headerName":"発言内容",
        "field":"内容",
        "wrapText":True,
        "autoHeight":True,
        "suppressSizeToFit":True,
        "maxWidth":500,
    },
    {
        "headerName":"人分類",
        "field":"人分類",
        "suppressSizeToFit":True,
        "wrapText":True,
        "autoHeight":True,
    },
    ],
}
    # 解析対象の文字列を表示する
    AgGrid(logs_contents_temp_show, grid_options)

st.header(':paperclip: 情報参照元')
st.markdown('分析の元になっているデータは、[中央区議会 Webサイト](https://www.kugikai.city.chuo.lg.jp/index.html)の「会議録検索」からHTMLファイルをごっそりダウンロードして、その上であれこれ苦心して加工して作成しました。注意して作業はしたつもりですが、一部のデータが欠損等している可能性もありますのでご承知おきください。もし不備等ありましたら[ほづみゆうき](https://twitter.com/ninofku)まで声掛けいただけるとありがたいです。')


#0 事前作業
#ライブラリのインポート
import glob
import pandas as pd
import pandas_profiling as pdp
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error as mae

def data_pre(df):
    #不要列の削除
    df = df.drop(columns="種類", axis=1)
    df = df.drop(columns="地域", axis=1)
    df = df.drop(columns="市区町村名", axis=1)
    df = df.drop(columns="土地の形状", axis=1)
    df = df.drop(columns="間口", axis=1)
    df = df.drop(columns="延床面積（㎡）", axis=1)
    df = df.drop(columns="前面道路：方位", axis=1)
    df = df.drop(columns="前面道路：種類", axis=1)
    df = df.drop(columns="前面道路：幅員（ｍ）", axis=1)
    
        #0 1_1 EDA_都道府県
    pref_jiscode = {
        "北海道": 18, "青森県": 46, "岩手県": 35, "宮城県": 10, "秋田県": 47, "山形県": 45, "福島県": 39, "茨城県": 43, "栃木県": 37, "群馬県": 32, "埼玉県": 8, "千葉県": 12,
        "東京都": 1, "神奈川県": 4, "新潟県": 34, "富山県": 30, "石川県": 16, "福井県": 29, "山梨県": 36, "長野県": 31, "岐阜県": 28, "静岡県": 14, "愛知県": 5, "三重県": 33,
        "滋賀県": 22, "京都府": 3, "大阪府": 2, "兵庫県": 7, "奈良県": 15, "和歌山県": 27, "鳥取県": 44, "島根県": 41, "岡山県": 21, "広島県": 9, "山口県": 38, "徳島県": 24,
        "香川県": 26, "愛媛県": 17, "高知県": 23, "福岡県": 6, "佐賀県": 40, "長崎県": 20, "熊本県": 13, "大分県": 25, "宮崎県": 42, "鹿児島県": 19, "沖縄県": 11
    }    
    df["都道府県名_num"] = df["都道府県名"].replace(pref_jiscode).astype(int)
    df = df.drop(columns="都道府県名", axis=1)

    #元データ
    """
        pref_jiscode = {
            "北海道": 1, "青森県": 2, "岩手県": 3, "宮城県": 4, "秋田県": 5, "山形県": 6, "福島県": 7, "茨城県": 8, "栃木県": 9, "群馬県": 10, "埼玉県": 11, "千葉県": 12,
            "東京都": 13, "神奈川県": 14, "新潟県": 15, "富山県": 16, "石川県": 17, "福井県": 18, "山梨県": 19, "長野県": 20, "岐阜県": 21, "静岡県": 22, "愛知県": 23, "三重県": 24,
            "滋賀県": 25, "京都府": 26, "大阪府": 27, "兵庫県": 28, "奈良県": 29, "和歌山県": 30, "鳥取県": 31, "島根県": 32, "岡山県": 33, "広島県": 34, "山口県": 35, "徳島県": 36,
            "香川県": 37, "愛媛県": 38, "高知県": 39, "福岡県": 40, "佐賀県": 41, "長崎県": 42, "熊本県": 43, "大分県": 44, "宮崎県": 45, "鹿児島県": 46, "沖縄県": 47
        }    
        df["都道府県名_num"] = df["都道府県名"].replace(pref_jiscode).astype(int)
        df = df.drop(columns="都道府県名", axis=1)
    """
    # 1_2 EDA_最寄駅：距離（分）
    replace_min = {
        "30分?60分":45,
        "1H?1H30":75,
        "2H?":120,
        "1H30?2H":105
    }
    df["最寄駅：距離（分）_min"] = df["最寄駅：距離（分）"].replace(replace_min).astype(float)
    df = df.drop(columns="最寄駅：距離（分）", axis=1)

    # 1_3 EDA_間取り

    ## 1_4 EDA_面積（㎡）
    df["面積（㎡）_num"] = df["面積（㎡）"].replace("2000㎡以上", 2000).astype(int)
    df = df.drop(columns="面積（㎡）", axis=1)

    # 1_5 EDA_建築年
    year_list = {}
    for i in df["建築年"].value_counts().keys():
        if ("令和" in i):
            year_list[i] = 4 - int(i[2:3])
        elif ("平成" in i):
            try:
                year_list[i] = 34 - int(i[2:4])
            except ValueError:
                year_list[i] = 34 - int(i[2:3])
        elif ("昭和" in i):
            year_list[i] = 97 - int(i[2:4])
        elif ("戦前" in i):
            year_list[i] = 77
        else:print(i)    #未処理確認

    df["建築年_year"] = df["建築年"].replace(year_list)

    df = df.drop(columns="建築年", axis=1)

    # 1_6 EDA_建物の構造
    str_stength={
        "ＳＲＣ":6,
        "ＳＲＣ、ＲＣ":5.5,
        "ＲＣ":5,
        "ＳＲＣ、ＲＣ、鉄骨造":5,
        "ＳＲＣ、鉄骨造":5,
        "ＲＣ、鉄骨造":4.5,
        "鉄骨造":4,
        "ＲＣ、ブロック造":3.5,
        "軽量鉄骨造":3,
        "ＲＣ、木造":3,
        "ブロック造":2,
        "木造":1
    }

    df["建物の構造_num"] = df["建物の構造"].replace(str_stength)

    df = df.drop(columns="建物の構造", axis=1)

    # 1_7 EDA_用途

    # 1_8 EDA_今後の利用目的

    # 1_9 EDA_都市計画

    # 1_10 EDA_建ぺい率（％）

    # 1_11 EDA_容積率（％）

    # 1_12 EDA_取引時点
    trade_timing = {}
    for i in df["取引時点"].value_counts().keys():
        if("1四半期" in i):
            num = float(i[0:4]+".25")
            trade_timing[i] = num
        elif("2四半期" in i):
            num = float(i[0:4]+".50")
            trade_timing[i] = num
        elif("3四半期" in i):
            num = float(i[0:4]+".75")
            trade_timing[i] = num
        elif("4四半期" in i):
            num = float(i[0:4]+".99")
            trade_timing[i] = num
        else:print("test")    #未処理確認

    df["取引時点_num"] = df["取引時点"].replace(trade_timing)

    df = df.drop(columns="取引時点", axis=1)

    # 1_13 EDA_改装

    # 1_14 EDA_取引の事情等

    # 1_15 EDA_まとめ
    index_array = ["市区町村コード", "都道府県名_num", "地区名", "最寄駅：名称", "最寄駅：距離（分）_min",
                   "間取り", "面積（㎡）_num", "建築年_year", "建物の構造_num", "用途",
                  "今後の利用目的", "都市計画", "建ぺい率（％）", "容積率（％）", "取引時点_num",
                  "改装", "取引の事情等", "取引価格（総額）_log"]
    df = df.reindex(columns=index_array)
    
    for col in ["地区名", "最寄駅：名称", "間取り", "用途", "今後の利用目的", "都市計画", "改装", "取引の事情等"]:
                df[col] = df[col].astype("category")
    print("test")
    return df



































































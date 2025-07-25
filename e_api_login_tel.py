# -*- coding: utf-8 -*-
# Copyright (c) 2021 Tachibana Securities Co., Ltd. All rights reserved.

# 2021.06.24,   yo.
# 2022.10.20 reviced,   yo.
# 2025.07.25 reviced,   yo.
# Python 3.11.2 / debian12
# API v4r7 で動作確認
# 立花証券ｅ支店ＡＰＩ利用のサンプルコード
# ログインして、ログアウトするだけです。

import urllib3
import datetime
import json
import time


#--- 共通コード ------------------------------------------------------

# request項目を保存するクラス。配列として使う。
# 'p_no'、'p_sd_date'は格納せず、func_make_url_requestで生成する。
class class_req :
    def __init__(self) :
        self.str_key = ''
        self.str_value = ''
        
    def add_data(self, work_key, work_value) :
        self.str_key = func_check_json_dquat(work_key)
        self.str_value = func_check_json_dquat(work_value)


# ログイン属性クラス
class class_def_account_property:
    def __init__(self):
        self.p_no = 0               # 累積p_no
        self.sUserId = ''           # request用仮想URL
        self.sPassword = ''         # master用仮想URL
        self.sSecondPassword = ''   # price用仮想URL
        self.sUrl = ''              # event用仮想URL
        self.sJsonOfmt = 5          # 返り値の表示形式指定
        


# 機能: システム時刻を"p_sd_date"の書式の文字列で返す。
# 返値: "p_sd_date"の書式の文字列
# 引数1: システム時刻
# 備考:  "p_sd_date"の書式：YYYY.MM.DD-hh:mm:ss.sss
def func_p_sd_date(int_systime):
    str_psddate = ''
    str_psddate = str_psddate + str(int_systime.year) 
    str_psddate = str_psddate + '.' + ('00' + str(int_systime.month))[-2:]
    str_psddate = str_psddate + '.' + ('00' + str(int_systime.day))[-2:]
    str_psddate = str_psddate + '-' + ('00' + str(int_systime.hour))[-2:]
    str_psddate = str_psddate + ':' + ('00' + str(int_systime.minute))[-2:]
    str_psddate = str_psddate + ':' + ('00' + str(int_systime.second))[-2:]
    str_psddate = str_psddate + '.' + (('000000' + str(int_systime.microsecond))[-6:])[:3]
    return str_psddate


# JSONの値の前後にダブルクオーテーションが無い場合付ける。
def func_check_json_dquat(str_value) :
    if len(str_value) == 0 :
        str_value = '""'
        
    if not str_value[:1] == '"' :
        str_value = '"' + str_value
        
    if not str_value[-1:] == '"' :
        str_value = str_value + '"'
        
    return str_value
    
    
# 受けたテキストの１文字目と最終文字の「"」を削除
# 引数：string
# 返り値：string
def func_strip_dquot(text):
    if len(text) > 0:
        if text[0:1] == '"' :
            text = text[1:]
            
    if len(text) > 0:
        if text[-1] == '\n':
            text = text[0:-1]
        
    if len(text) > 0:
        if text[-1:] == '"':
            text = text[0:-1]
        
    return text
    


# 機能: URLエンコード文字の変換
# 引数1: 文字列
# 返値: URLエンコード文字に変換した文字列
# 
# URLに「#」「+」「/」「:」「=」などの記号を利用した場合エラーとなる場合がある。
# APIへの入力文字列（特にパスワードで記号を利用している場合）で注意が必要。
#   '#' →   '%23'
#   '+' →   '%2B'
#   '/' →   '%2F'
#   ':' →   '%3A'
#   '=' →   '%3D'
def func_replace_urlecnode( str_input ):
    str_encode = ''
    str_replace = ''
    
    for i in range(len(str_input)):
        str_char = str_input[i:i+1]

        if str_char == ' ' :
            str_replace = '%20'       #「 」 → 「%20」 半角空白
        elif str_char == '!' :
            str_replace = '%21'       #「!」 → 「%21」
        elif str_char == '"' :
            str_replace = '%22'       #「"」 → 「%22」
        elif str_char == '#' :
            str_replace = '%23'       #「#」 → 「%23」
        elif str_char == '$' :
            str_replace = '%24'       #「$」 → 「%24」
        elif str_char == '%' :
            str_replace = '%25'       #「%」 → 「%25」
        elif str_char == '&' :
            str_replace = '%26'       #「&」 → 「%26」
        elif str_char == "'" :
            str_replace = '%27'       #「'」 → 「%27」
        elif str_char == '(' :
            str_replace = '%28'       #「(」 → 「%28」
        elif str_char == ')' :
            str_replace = '%29'       #「)」 → 「%29」
        elif str_char == '*' :
            str_replace = '%2A'       #「*」 → 「%2A」
        elif str_char == '+' :
            str_replace = '%2B'       #「+」 → 「%2B」
        elif str_char == ',' :
            str_replace = '%2C'       #「,」 → 「%2C」
        elif str_char == '/' :
            str_replace = '%2F'       #「/」 → 「%2F」
        elif str_char == ':' :
            str_replace = '%3A'       #「:」 → 「%3A」
        elif str_char == ';' :
            str_replace = '%3B'       #「;」 → 「%3B」
        elif str_char == '<' :
            str_replace = '%3C'       #「<」 → 「%3C」
        elif str_char == '=' :
            str_replace = '%3D'       #「=」 → 「%3D」
        elif str_char == '>' :
            str_replace = '%3E'       #「>」 → 「%3E」
        elif str_char == '?' :
            str_replace = '%3F'       #「?」 → 「%3F」
        elif str_char == '@' :
            str_replace = '%40'       #「@」 → 「%40」
        elif str_char == '[' :
            str_replace = '%5B'       #「[」 → 「%5B」
        elif str_char == ']' :
            str_replace = '%5D'       #「]」 → 「%5D」
        elif str_char == '^' :
            str_replace = '%5E'       #「^」 → 「%5E」
        elif str_char == '`' :
            str_replace = '%60'       #「`」 → 「%60」
        elif str_char == '{' :
            str_replace = '%7B'       #「{」 → 「%7B」
        elif str_char == '|' :
            str_replace = '%7C'       #「|」 → 「%7C」
        elif str_char == '}' :
            str_replace = '%7D'       #「}」 → 「%7D」
        elif str_char == '~' :
            str_replace = '%7E'       #「~」 → 「%7E」
        else :
            str_replace = str_char
        str_encode = str_encode + str_replace
    return str_encode


# 機能： ファイルから文字情報を読み込み、その文字列を返す。
# 戻り値： 文字列
# 第１引数： ファイル名
# 備考：　json形式のファイルを想定。
def func_read_from_file(str_fname):
    str_read = ''
    try:
        with open(str_fname, 'r', encoding = 'utf_8') as fin:
            while True:
                line = fin.readline()
                if not len(line):
                    break
                str_read = str_read + line
        return str_read
    except IOError as e:
        print('Can not Write!!!')
        print(type(e))


# 機能： API問合せ文字列を作成し返す。
# 戻り値： api問合せのurl文字列
# 第１引数： ログインは、Trueをセット。それ以外はFalseをセット。
# 第２引数： ログインは、APIのurlをセット。それ以外はログインで返された仮想url（'sUrlRequest'等）の値をセット。
# 第３引数： 要求項目のデータセット。クラスの配列として受取る。
def func_make_url_request(auth_flg, \
                          url_target, \
                          work_class_req) :
    str_url = url_target
    if auth_flg == True :   # ログインの場合
        str_url = str_url + 'auth/'
    str_url = str_url + '?'
    str_url = str_url + func_make_json_format(work_class_req)
    return str_url


# 機能: API問合せ。通常のrequest,price用。
# 返値: API応答（辞書型）
# 第１引数： URL文字列。
# 備考: APIに接続し、requestの文字列を送信し、応答データを辞書型で返す。
#       master取得は専用の func_api_req_muster を利用する。
def func_api_req(str_url): 
    print('送信文字列＝')
    print(str_url)  # 送信する文字列

    # APIに接続
    http = urllib3.PoolManager()
    req = http.request('GET', str_url)
    print("req.status= ", req.status )

    # 取得したデータを、json.loadsを利用できるようにstr型に変換する。日本語はshift-jis。
    bytes_reqdata = req.data
    str_shiftjis = bytes_reqdata.decode("shift-jis", errors="ignore")
    print('返信文字列＝')
    print(str_shiftjis)

    return str_shiftjis


# 機能: class_req型データをjson形式の文字列に変換する。
# 返値: json形式の文字
# 第１引数： class_req型データ
def func_make_json_format(work_class_req):
    str_json_data =  '{\n\t'
    for i in range(len(work_class_req)) :
        if len(work_class_req[i].str_key) > 0:
            str_json_data = str_json_data + work_class_req[i].str_key + ':' + work_class_req[i].str_value + ',\n\t'
    str_json_data = str_json_data[:-3] + '\n}'
    return str_json_data


# 機能： アカウント情報をファイルから取得する
# 引数1: ファイル名
# 引数2: 口座情報（class_def_account_property型）データ
def func_get_acconut_info(fname, class_account_property):
    str_account_info = func_read_from_file(fname)
    # JSON形式の文字列を辞書型で取り出す
    json_account_info = json.loads(str_account_info)

    class_account_property.sUserId = json_account_info.get('sUserId')
    class_account_property.sPassword = json_account_info.get('sPassword')
    class_account_property.sSecondPassword = json_account_info.get('sSecondPassword')
    class_account_property.sUrl = json_account_info.get('sUrl')

    # 返り値の表示形式指定
    class_account_property.sJsonOfmt = json_account_info.get('sJsonOfmt')
    # "5"は "1"（1ビット目ＯＮ）と”4”（3ビット目ＯＮ）の指定となり
    # ブラウザで見や易い形式」且つ「引数項目名称」で応答を返す値指定


# 機能: ファイルに書き込む
# 引数1: 出力ファイル名
# 引数2: 出力するデータ
# 備考:
def func_write_to_file(str_fname_output, str_data):
    try:
        with open(str_fname_output, 'w', encoding = 'utf-8') as fout:
            fout.write(str_data)
    except IOError as e:
        print('Can not Write!!!')
        print(type(e))

#--- 以上 共通コード -------------------------------------------------




    
# ======================================================================================================
# ==== プログラム始点 =================================================================================
# ======================================================================================================

if __name__ == "__main__":
    # --- ファイル名等を設定 ------------------------------------------------------------------
    fname_account_info = "e_api_account_info.txt"
    str_fname_login_response = "e_api_login_response.txt"
    str_fname_info_p_no = "e_api_info_p_no.txt"
    # --- 以上設定項目 -------------------------------------------------------------------------
    
    my_account_property = class_def_account_property()
    # 口座情報をファイルから読み込む。
    func_get_acconut_info(fname_account_info, my_account_property)
    
    my_account_property.p_no = 1          # p_noの初期値をセット。ログイン時は、1。
    
    # ID、パスワード、第２パスワードのURLエンコードをチェックして変換
    my_userid = func_replace_urlecnode(my_account_property.sUserId)
    my_passwd = func_replace_urlecnode(my_account_property.sPassword)
    my_account_property.sSecondPassword = func_replace_urlecnode(my_account_property.sSecondPassword)
    my_url = my_account_property.sUrl

    print('-- login -----------------------------------------------------')
    # 「ｅ支店・ＡＰＩ、ブラウザからの利用方法」に記載のログイン例
    # 'https://demo-kabuka.e-shiten.jp/e_api_v4r1/auth/?{"p_no":"1","p_sd_date":"2020.11.07-13:46:35.000",'
    # '"sCLMID":"CLMAuthLoginRequest","sPassword":"xxxxxx","sUserId":"xxxxxxxx","sJsonOfmt":"5"}'
    #
    # 送信項目の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p2/43 No.1 引数名:CLMAuthLoginRequest を参照してください。
    req_item = [class_req()]
    str_p_sd_date = func_p_sd_date(datetime.datetime.now())     # システム時刻を所定の書式で取得
    
    str_key = '"p_no"'
    str_value = func_check_json_dquat(str(my_account_property.p_no))
    #req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"p_sd_date"'
    str_value = str_p_sd_date
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"sCLMID"'
    str_value = 'CLMAuthLoginRequest'
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"sUserId"'
    str_value = my_userid
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)
    
    str_key = '"sPassword"'
    str_value = my_passwd
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)
    
    # 返り値の表示形式指定
    str_key = '"sJsonOfmt"'
    str_value = my_account_property.sJsonOfmt    # "5"は "1"（1ビット目ＯＮ）と”4”（3ビット目ＯＮ）の指定となり「ブラウザで見や易い形式」且つ「引数項目名称」で応答を返す値指定
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    # ログイン処理
    # URL文字列の作成
    str_url = func_make_url_request(True, \
                                     my_url, \
                                     req_item)
    # ログインとログイン後の電文が違うため、第１引数で指示。
    # ログインはTrue。それ以外はFalse。
    # このプログラムでの仕様。APIの仕様ではない。
        
    # API問合せ
    str_api_response = func_api_req(str_url)
    # 戻り値の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p2/43 No.2 引数名:CLMAuthLoginAck を参照してください。

    # apiの返り値（JSON形式の文字列）を辞書型で取り出す
    json_response = json.loads(str_api_response)


    # 以下、ログインの判定とログイン情報の保存 ------------
    int_p_errno = int(json_response.get('p_errno'))
    # p_erronは、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇ｒ〇）、REQUEST I/F、利用方法、データ仕様」を参照ください。
    if int_p_errno >= 0 :
        int_sResultCode = int(json_response.get('sResultCode'))


    # sResultCodeは、マニュアル
    # 「立花証券・ｅ支店・ＡＰＩ（ｖ〇ｒ〇）、REQUEST I/F、注文入力機能引数項目仕様」
    # (api_request_if_order_vOrO.pdf)
    # の p13/42 「6.メッセージ一覧」を参照ください。
    if int_p_errno ==  0 and int_sResultCode == 0:    # ログインエラーでない場合
        # ---------------------------------------------
        # ログインでの注意点
        #
        # 契約締結前書面が未読の場合、
        # 「int_p_errno = 0 And int_sResultCode = 0」で、
        # sUrlRequest=""、sUrlEvent="" が返されログインできない。
        # ---------------------------------------------
        if len(json_response.get('sUrlRequest')) > 0 :
            # ログイン属性クラスに取得した値をセット
            my_account_property.login_status = True           # login状態 true

            # "p_no"を保存する。
            str_info_p_no = '{\n'
            str_info_p_no = str_info_p_no + '\t' + '"p_no":"' + str(my_account_property.p_no) + '"\n'
            str_info_p_no = str_info_p_no + '}\n'
            func_write_to_file(str_fname_info_p_no, str_info_p_no)
            print('現在の"p_no"を保存しました。 \tファイル名: ', str_fname_info_p_no )            

            # ログイン情報をファイルに書き込む
            func_write_to_file(str_fname_login_response, str_api_response)
            print('loginレスポンスを保存しました。\tファイル名: ', str_fname_login_response )
        else :
            print('契約締結前書面が未読です。')
            print('ブラウザーで標準Webにログインして確認してください。')
            my_account_property.login_status = False       # login状態 false
    else :  # ログインに問題があった場合
        my_account_property.login_status = False           # login状態 false
        print("ログインに失敗しました。")# システム時刻を所定の書式で取得
        print('p_errno:', json_response.get('p_errno'))
        print('p_err:', json_response.get('p_err'))
        print('sResultCode:', json_response.get('sResultCode'))
        print('sResultText:', json_response.get('sResultText'))
        print()

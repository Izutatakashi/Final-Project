import os
import time
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required
import sqlite3
import difflib
from difflib import SequenceMatcher
import requests
import json

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# ########################################################
#   SETTINGS
# get your api key at https://openweathermap.org/
# https://openweathermap.org/のAPIコード．取得してここに入力してください
WEATHER_API = 'write your api code here'
#
# number of texts to create. if you change here you
# must also change index.html
# 文章の下図．変更可能．ただし，index.htmlも変更してください
NUMBER_OF_TEXTS = 15

# administrator's user name and password.If you want to change here
# you must delete 'admin_folder', 'users_folders' and 'touch_typing.db'
# from the system folder. It means that you are starting to set up
# your system for the first time. Do not change if there are already
# other users registered.
# 変更しないことをお勧めします．
ADMIN_USER_NAME = "admin"
ADMIN_INITIAL_PASSWORD = "admin"
DB_NAME = 'touch_typing.db'

# ########################################################
# OTHER SETTINGS
# DO NOT CHANGE THESE SETTINGS
# ほかの設定項目．変更しないでください．
ADMIN_PATH = "./admin_folder"
ADMIN_FOLDER = "admin_folder"
SAMPLE_PATH = "./admin_folder/sample/"
USER_PATH = "./users_folder/"
USER_DIR = "./users_folder"
USERS_FOLDER = "users_folder"
TEXT_FILE = "text_"

# ########################################################
# connect to database. create if it does not exist
# データベースに接続する
conn = sqlite3.connect(DB_NAME)
db = conn.cursor()

# create table 'users'
# 'users'テーブルを作成
db.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, user_name TEXT NOT NULL, user_password TEXT NOT NULL, register_date DEFAULT CURRENT_TIMESTAMP NOT NULL)')

# create table 'user_input'
# 'user_input'テーブルを作成
db.execute('CREATE TABLE IF NOT EXISTS user_input (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, user_name TEXT NOT NULL, input_file_name TEXT NOT NULL,input_done NUMERIC NOT NULL, input_match NUMERIC NOT NULL, last_update DEFAULT CURRENT_TIMESTAMP NOT NULL)')

# create table 'history'
# 'history'テーブルを作成
db.execute('CREATE TABLE IF NOT EXISTS history (id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, activity TEXT NOT NULL, last_update DEFAULT CURRENT_TIMESTAMP NOT NULL)')

# commit and close in order to update the database
# データベースの更新と一旦終了
conn.commit()
conn.close()

# start the database again
# 再度データベースに接続する
conn = sqlite3.connect('touch_typing.db')
db = conn.cursor()

# try to extract user 'admin' from table 'users'
# テーブル'users'から'admin'を抽出してみる
db.execute("SELECT * FROM users WHERE user_name = :name", {"name":ADMIN_USER_NAME})

# fetch the record
# レコードを取り出す
is_admin=db.fetchone()

# if the database was just created and the tables are still empty
# adminユーザーが存在しないときの処理
if is_admin is None:

    # insert the first user. actually, the administrator.
    # テーブルにadminユーザーを登録する
    db.execute("INSERT INTO users(user_name, user_password) VALUES (:user_name, :user_password)",
                {"user_name":ADMIN_USER_NAME, "user_password":generate_password_hash(ADMIN_INITIAL_PASSWORD)})

    # commit and close in order to update the database
    # データベースの更新と一旦終了
    conn.commit()
    conn.close()

# ########################################################
# create 'admin_folder'. It is used to store the sample files
# 管理者フォルダを作成する.サンプルファイルを
# 格納する場所
if not os.path.exists(ADMIN_PATH):
    os.mkdir(ADMIN_FOLDER)


# create folder 'sample' inside 'admin_folder'. It is used to store the sample files
# 管理者フォルダの中にsampleフォルダを作成する.サンプルファイルを
# 格納する場所
if not os.path.exists(SAMPLE_PATH ):
    os.mkdir(SAMPLE_PATH )

# create sample files inside /admin_folder/sample
# フォルダ/admin_folder/sampleの中にサンプルファイルを作成する
for i in range(NUMBER_OF_TEXTS):
    if not os.path.isfile(SAMPLE_PATH + TEXT_FILE + str(i + 1)):
        f = open(SAMPLE_PATH + TEXT_FILE + str(i + 1), 'w')
        f.close()

# create 'users_folder'. It is used to store users' input files
# 管理者とユーザー用のフォルダを作成する.課題作成のファイルを
# 格納する場所
if not os.path.exists(USER_DIR):
    os.mkdir(USERS_FOLDER)

# ########################################################
# this function creates a newly registered user's folder
# inside the folder 'users_folder', and then, create
# files inside it. These files are used to store the texts
# that the user will input.

# フォルダの存在を確認し，存在しないときは作成する．
# また，課題のファイルも作成する
def mkdir_mkfile(user_id, user_name, user_folder, user_file):

    # check whether the user' folder already exists.　If not, create it.
    # フォルダの存在をチェックする.存在しないときは作成
    if not os.path.exists(user_folder):
        os.mkdir(user_folder)

    # start the database again
    # 再度データベースに接続する
    conn = sqlite3.connect('touch_typing.db')
    db = conn.cursor()

    # check whether the user' input files already exist.　If not, create them.
    # ファイルの存在をチェックし，存在しないときはファイルを作成する
    for i in range(NUMBER_OF_TEXTS):
        if not os.path.isfile(user_file + str(i + 1)):
            f = open(user_file + str(i + 1), 'w')
            f.close()

            # insert into user_input table
            # テーブルuser_inputにエントリーを登録する．
            db.execute("INSERT INTO user_input (user_id, user_name, input_file_name, input_done, input_match) VALUES (:user_id, :user_name, :input_file_name, :input_done, :input_match)",
                        {"user_id":user_id, "user_name":user_name, "input_file_name":TEXT_FILE+str(i+1), "input_done":0, "input_match":round(0.00,2)})
            # update database
            # データベースを更新
            conn.commit()

    # close database
    # データベースを閉じる
    conn.close()

    return True

# ########################################################
# create input text files inside /users_folder/admin for user 'admin'
# ユーザーフォルダ/users_folder/admin の中にadmin用の課題のフォルダを作成して，
# その中に空のファイルを格納する
#
mkdir_mkfile(1, 'admin', USER_PATH + 'admin', USER_PATH + 'admin/text_')
#
# ########################################################
# this function requests 'https://get.geojs.io/v1/ip/geo.json' for  weather information
# if either WEATHER_API is not set or the response is empty, default info is returned.
# 天気情報を習得する関数. APIが設定されていない，または，空の応答の場合は
# デフォルトの情報を表示させる

def weather_info():

    # default display
    # 初期設定
    no_weather_info={
        "city": "city",
        "temp": "temp",
        "hum": "hum",
        "condition": "cond"
    }

    weather_info = {}

    # store longitude and latitude in the session
    # 経度と緯度をセッションに入れる
    longitude = session["longitude"]
    latitude  = session["latitude"] #geo_get["latitude"]

    # weather info url
    # 天気予報のサイト
    weather_url = 'https://api.openweathermap.org/data/2.5/weather'

    # request weather info
    # 天気情報を要求
    response = requests.get(weather_url + f'?lat={latitude}&lon={longitude}&appid={WEATHER_API}')

    weather_info = response.json()

    try:
        valid_city = weather_info['name']
    except:
        return no_weather_info

    # if valid response
    # 有効な応答だったら

    # change kelvin temperature into celsius scale
    # 気温をケルビンから摂氏へ変換
    temp = weather_info['main']['temp']-273.15
    # return valid info
    # 有効な情報を返す
    return {
        "city": weather_info['name'],
        "temp": temp,
        "hum": weather_info['main']['humidity'],
        "condition": weather_info['weather'][0]['description']
    }

# ########################################################

@app.route("/")
@login_required
def index():
    """ index function """
    """ユーザーがこれまで作成した課題を抽出する"""

    # store user info
    # ログインしているユーザーの課題作成状況
    user_info = []

    # store all users' current work progress
    # すべてのユーザーの課題作成状況
    all_current_situation = []

    # store all users' activities
    # すべてのユーザーのログインなどの履歴
    all_info = []

    # start the database again
    # 再度データベースに接続する
    conn = sqlite3.connect('touch_typing.db')
    db = conn.cursor()

    # select the user's current work progress situation. Info about all the NUMBER_OF_TEXTS
    # データベースの「user_input」のテーブルから「ユーザー」が入力したものを抽出する
    db.execute("SELECT * FROM user_input WHERE user_id = :user",
                          {"user":session["user_id"]})

    user_db = db.fetchall()

    for row in user_db:

        # open the sample file and obtain its length
        # サンプルファイル、テキストの中の文字数を数える
        sample_file =  open(SAMPLE_PATH + row[3], 'r')
        sample_text = sample_file.read()
        sample_size = len(sample_text)

        sample_file.close()

        # add to the list
        # リストの形でユーザーネーム、進捗状況、一致率、更新日などをだす
        user_info.append(list((row[2],row[3], row[4], sample_size, row[5], row[6])))

    # commit and close in order to update the database
    # データベースの更新と一旦終了
    conn.commit()
    conn.close()

    return render_template("index.html", user_info = user_info, all_info = all_info, all_current_situation=all_current_situation,current_user = session["user_id"], text_inside_file = "", file_name = "")

# ########################################################

@app.route("/show_all_work_in_progess", methods=["GET", "POST"])
@login_required
def show_all_work_in_progess():
    """ this function shows the current work progress of each of the NUMBER_OF_TEXTS """
    """ユーザーの進捗状況を表示させる"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # start the database again
        # 再度データベースに接続する
        conn = sqlite3.connect('touch_typing.db')
        db = conn.cursor()

        # store user info
        # ログインしているユーザーの課題作成状況
        user_info_3 = []

        # store all users' current work progress
        # すべてのユーザーの課題作成状況
        all_current_situation_3 = []

        # store all users' activities
        # すべてのユーザーのログインなどの履歴
        all_info_3 = []

        # select the user's current work situation. Info about all the NUMBER_OF_TEXTS
        # データベースの「user_input」のテーブルから「ユーザー」が入力したものを抽出する
        db.execute("SELECT * FROM user_input WHERE user_id = :user", {"user":session["user_id"]})

        user_db = db.fetchall()

        for row in user_db:
            # open the sample file and obtain its length
            # サンプルファイル、テキストの中の文字数を数える
            sample_file =  open(SAMPLE_PATH + row[3], 'r')
            sample_text = sample_file.read()
            sample_size = len(sample_text)

            sample_file.close()

            # add to the list
            # リストの形でユーザーネーム、進捗状況、一致率、更新日などをだす
            user_info_3.append(list((row[2],row[3], row[4], sample_size, row[5], row[6])))

        # select all users' current work progress situations. Info about all the NUMBER_OF_TEXTS
        # データベースの「user_input」のテーブルからすべての「ユーザー」の進捗状況を抽出する
        db.execute("SELECT * FROM user_input ORDER By user_id")

        all_user_db = db.fetchall()

        for row in all_user_db:
            # open the sample file and obtain its length
            # サンプルファイル、テキストの中の文字数を数える
            sample_file =  open(SAMPLE_PATH + row[3], 'r')
            sample_text = sample_file.read()
            sample_size = len(sample_text)

            sample_file.close()

            match_value = row[5]
            match_ratio = f"{match_value:,.2f}"

            # add to the list
            # リストに追加する
            all_current_situation_3.append(list((row[2],row[3], row[4], sample_size, match_ratio, row[6])))

        # commit and close in order to update the database
        # データベースの更新と一旦終了
        conn.commit()
        conn.close()

        # update index.html
        # index.htmlのページを更新
        return render_template("index.html", user_info=user_info_3, all_info=all_info_3, all_current_situation = all_current_situation_3, current_user = session["user_id"], text_inside_file = "", file_name = "")

    else:
        # Redirect user to /
        # /を表示させる
        return redirect("/")

# ########################################################

@app.route("/hide_all_work_in_progess", methods=["GET", "POST"])
@login_required
def hide_all_work_in_progess():
    """ hide info about users's current work situations """
    """ユーザーの進捗状況の情報を非表示にする"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # start the database
        # データベースに接続する
        conn = sqlite3.connect('touch_typing.db')
        db = conn.cursor()

        # store user info
        # ログインしているユーザーの課題作成状況
        user_info_4 = []

        # store all users' current work progress
        # すべてのユーザーの課題作成状況
        all_current_situation_4 = []

        # store all users' activities
        # すべてのユーザーのログインなどの履歴
        all_info_4 = []

        # select the user's current work situation. Info about all the NUMBER_OF_TEXTS
        # データベースの「user_input」のテーブルから「ユーザー」が入力したものを抽出する
        db.execute("SELECT * FROM user_input WHERE user_id = :user",
                              {"user":session["user_id"]})

        user_db = db.fetchall()

        for row in user_db:
            # open the sample file and obtain its length
            # サンプルファイル、テキストの中の文字数を数える
            sample_file =  open(SAMPLE_PATH + row[3], 'r')
            sample_text = sample_file.read()
            sample_size = len(sample_text)

            sample_file.close()

            # add to the list
            # リストに追加する
            user_info_4.append(list((row[2],row[3], row[4], sample_size, row[5], row[6])))

        # commit and close in order to update the database
        # データベースの更新と一旦終了
        conn.commit()
        conn.close()

        # update index.html
        # index.htmlのページを更新
        return render_template("index.html", user_info = user_info_4, all_info = all_info_4, all_current_situation = all_current_situation_4, current_user = session["user_id"], text_inside_file = "", file_name = "")

    else:
        # Redirect user to /
        # /を表示させる
        return redirect("/")

# ########################################################

@app.route("/show_all_activities", methods=["GET", "POST"])
@login_required
def show_all_activities():
    """ this function shows all the activities """
    """ システム上でのアクティビティを表示する """

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        conn = sqlite3.connect('touch_typing.db')
        db = conn.cursor()

        # start the database
        # データベースに接続する
        conn = sqlite3.connect('touch_typing.db')
        db = conn.cursor()

        # store user info
        # ログインしているユーザーの課題作成状況
        user_info_1 = []

        # store all users' current work progress
        # すべてのユーザーの課題作成状況
        all_current_situation_1 = []

        # store all users' activities
        # すべてのユーザーのログインなどの履歴
        all_info_1 = []

        # select the user's current work situation. Info about all the NUMBER_OF_TEXTS
        # データベースの「user_input」のテーブルから「ユーザー」が入力したものを抽出する
        db.execute("SELECT * FROM user_input WHERE user_id = :user",
                    {"user":session["user_id"]})

        user_db = db.fetchall()

        for row in user_db:
            # open the sample file and obtain its length
            # サンプルファイル、テキストの中の文字数を数える
            sample_file =  open(SAMPLE_PATH + row[3], 'r')
            sample_text = sample_file.read()
            sample_size = len(sample_text)

            sample_file.close()

            # add to the list
            # リストに追加する
            user_info_1.append(list((row[2],row[3], row[4], sample_size, row[5], row[6])))

        # extract all the log activities on the system from table history
        # historyテーブルから全ユーザーの履歴を抽出する
        db.execute("SELECT * FROM history ORDER BY last_update DESC")

        all_db = db.fetchall()

        for all_row in all_db:
            # extract user name from table user_name
            # ユーザー名を抽出する
            db.execute("SELECT user_name FROM users WHERE id = :user_id",
                        {"user_id":all_row[1]})

            user_name = db.fetchone()

            # add to the list
            # リストに追加する
            all_info_1.append(list((user_name[0], all_row[2], all_row[3])))

        # commit and close in order to update the database
        # データベースの更新と一旦終了
        conn.commit()
        conn.close()

        # update index.html
        # index.htmlのページを更新
        return render_template("index.html", user_info=user_info_1, all_info=all_info_1, all_current_situation=all_current_situation_1, current_user=session["user_id"], text_inside_file="", file_name="")

    else:
        # Redirect user to /
        # /を表示させる
        return redirect("/")

# ########################################################

@app.route("/hide_all_activities", methods=["GET", "POST"])
@login_required
def hide_all_activities():
    """ hide all info about users' activities """
    """ すべてのユーザーの履歴情報を非表示にする"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # start the database
        # データベースに接続する
        conn = sqlite3.connect('touch_typing.db')
        db = conn.cursor()

        # store user info
        # ログインしているユーザーの課題作成状況
        user_info_2 = []

        # store all users' current work progress
        # すべてのユーザーの課題作成状況
        all_current_situation_2 = []

        # store all users' activities
        # すべてのユーザーのログインなどの履歴
        all_info_2 = []

        # select the user's current work situation. Info about all the NUMBER_OF_TEXTS
        # データベースの「user_input」のテーブルから「ユーザー」が入力したものを抽出する
        db.execute("SELECT * FROM user_input WHERE user_id = :user",
                              {"user":session["user_id"]})
        user_db = db.fetchall()

        for row in user_db:
            # open the sample file and obtain its length
            # サンプルファイル、テキストの中の文字数を数える
            sample_file =  open(SAMPLE_PATH + row[3], 'r')
            sample_text = sample_file.read()
            sample_size = len(sample_text)

            sample_file.close()

            # add to the list
            # リストに追加する
            user_info_2.append(list((row[2],row[3], row[4], sample_size, row[5], row[6])))

        # commit and close in order to update the database
        # データベースの更新と一旦終了
        conn.commit()
        conn.close()

        # update index.html
        # index.htmlのページを更新
        return render_template("index.html", user_info = user_info_2, all_info = all_info_2, all_current_situation = all_current_situation_2, current_user = session["user_id"], text_inside_file = "", file_name = "")

    else:
        # Redirect user to /
        # /を表示させる
        return redirect("/")

# ########################################################

@app.route("/login", methods=["GET", "POST"])
def login():
    """ this function checks whether the user is authorized to Log in"""
    """ ログインを行う関数 """

    # Forget any user_id
    # セッションを一旦クリアする
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # start the database
        # データベースに接続する
        conn = sqlite3.connect('touch_typing.db')
        db = conn.cursor()

        # Ensure username was submitted
        # ユーザー名の入力を確認
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        # パスワードの入力を確認
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        # ユーザー名の存在を確認
        db.execute("SELECT * FROM users WHERE user_name = :user_name", {"user_name":request.form.get("username")})

        rows=db.fetchone()

        # check the validity of the password
        # 読み込んだやつが1つではないときと暗号化されたパスワードと入力されたパスワードを比較して違うとき
        if not len(rows) != 1 or not check_password_hash(rows[2], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        # すべての条件をくぐった時、セッションを確立
        session["user_id"] = rows[0]

        # set session user_name in order to display on the upper right side of the window
        # 画面右上に表示するユーザー名をセッションに格納する
        session["user_name"] = rows[1]

        # set longitude and latitude as session info in order to pass them to function weather_info
        # 経度と緯度をセッション情報として格納して，weather_info関数に渡す
        session["longitude"] = float(request.form.get("long"))
        session["latitude"] = float(request.form.get("lat"))

        # get weather info
        # 天気予報の情報を抽出する
        weather = weather_info()

        if weather['city'] != 'city':
            # sort the weather info to be displayed on the title bar
            # 情報の整理をする
            session["temperature"] = f"{weather['temp']:,.1f}"
            session["humidity"] = f"{weather['hum']:,.0f}%"
        else:
            session["temperature"] = "temp"
            session["humidity"] = "hum"

        session["city"] = weather['city']
        session["condition"] = weather['condition']

        # record the activity
        # テーブルhistoryに登録
        # historyでも上でのセッションにはいってるユーザーid、ファイルネームはaction、ログインしたことを記録
        db.execute("INSERT INTO history(user_id, activity) VALUES (:user_id, :action)",
            {"user_id":session["user_id"], "action":"LOGIN"})

        # commit and close in order to update the database
        # データベースの更新と一旦終了
        conn.commit()
        conn.close()

        # Redirect user to /
        # /を表示させる
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

# ########################################################

@app.route("/logout")
def logout():
    """ ログアウト """
    """Log user out"""

    # start the database
    # データベースに接続する
    conn = sqlite3.connect('touch_typing.db')
    db = conn.cursor()

    # record the activity
    # テーブルhistoryに登録
    db.execute("INSERT INTO history(user_id,activity) VALUES (:user_id,:action)",{"user_id":session["user_id"], "action":"LOGOUT"})

    # commit and close in order to update the database
    # データベースの更新と一旦終了
    conn.commit()
    conn.close()

    # Forget any user_id
    # セッションをクリアする
    session.clear()

    # Redirect user to /
    # /を表示させる
    return redirect("/")

# ########################################################

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register new user"""
    """ 新しいユーザーを登録する関数 """

    # Forget any user_id
    # セッションをクリアする
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    # Postメソッドにアクセスをしたか場合の処理
    if request.method == "POST":

        # start the database
        # データベースに接続する
        conn = sqlite3.connect('touch_typing.db')
        db = conn.cursor()

        # Ensure username was submitted
        # ユーザー名の入力を確認
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        # パスワードの入力を確認
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # check whether the passwords match
        # パスワードが一致しないときはメッセージを表示して関数から脱出
        elif request.form.get("password") != request.form.get("confirm-password"):
            return apology("The passwords don't match", 403)

        # check whether the user name is already taken.
        # データベースに同じユーザー名の人が存在するときはメッセージを表示して関数から脱出
        else:
            db.execute("SELECT * FROM users WHERE user_name = :user_name",
                    {"user_name":request.form.get("username")})

            user_exists = db.fetchone()

            if user_exists is not None:
                return apology("Username already taken", 403)

        # passed all the tests above. remember the user name
        # すべてのチェックをクリアした．ユーザー名を記録する
        register_name = request.form.get("username")

        # set session user_name
        # セッションを作成する
        session["user_name"] = register_name

        # store the user info into the users table
        # データベースにユーザーを登録
        db.execute("INSERT INTO users(user_name, user_password) VALUES (:user_name, :user_password)",
                     {"user_name":register_name, "user_password":generate_password_hash(request.form.get("password"))})

        # update the database
        # データベースを更新
        conn.commit()

        # extract the registered user name from the table
        # データベースの「ユーザ－」テーブルに登録したデータを抽出する
        db.execute("SELECT * FROM users WHERE user_name = :user_name",
                    {"user_name":register_name})

        rows = db.fetchone()

        # get the user's id and set session user_id
        # セッションを開始する。
        #毎回rowという新しい表がかってにつくられて0番目にコピーして上書きされるので0行目の1列を参照
        session["user_id"] = rows[0]


        # set longitude and latitude as session info in order to pass them to function weather_info
        # 経度と緯度をセッション情報として格納して，weather_info関数に渡す
        session["longitude"] = float(request.form.get("long"))
        session["latitude"] = float(request.form.get("lat"))

        # get weather info
        # 天気予報の情報を抽出する
        weather = weather_info()

        # sort the weather info to be displayed on the title bar
        # 情報の整理をする
        session["city"] = weather['city']
        session["temperature"] = f"{weather['temp']:,.1f}"
        session["humidity"] = f"{weather['hum']:,.0f}%"
        session["condition"] = weather['condition']

        # create user's folder and input files in the folder ./users_folder
        # フォルダusers_folderの中にユーザーのフォルダを作成し，その中に入力用のファイルを作成する
        mkdir_mkfile(rows[0], register_name, USER_PATH + register_name, USER_PATH + register_name + '/' + TEXT_FILE)

        # record the activity
        # テーブルhistoryに登録
        # historyでも上でのセッションにはいってるユーザーid、ファイルネームはaction、ログインしたことを記録
        db.execute("INSERT INTO history(user_id, activity) VALUES (:user_id, :action)",
                    {"user_id":session["user_id"], "action":"SIGN IN"})

        # commit and close in order to update the database
        # データベースの更新と一旦終了
        conn.commit()
        conn.close()

        # Redirect user to /
        # /を表示させる
        return redirect("/")

    # if Get method was used to access the content
    # メソッドにアクセスをしたか場合の処理
    else:
        return render_template("register.html")

# ########################################################

@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    """function used to change the password. login user can only change their own passwords."""
    """ you are not allowed to changed someone else's password unless you are the administrator"""
    """ the administrator can change anyone's password without inputting the correct password"""
    """ but can not leave the current password input blank"""
    """ パスワード変更用の関数．自分以外のパスワードは変更不可能"""
    """ 自分のパスワードを変更する際には，現在のパスワードを入力しなければならない"""
    """ ただし，管理者であれば，ほかのユーザーのパワードを変更できる．そのユーザーの現在の"""
    """ パワードを入力する必要ないが，現在のパスワードの欄を空白にしておいてはならない．"""

    # Postメソッドにアクセスをしたか場合の処理
    if request.method == "POST":

        # start the database
        # データベースに接続する
        conn = sqlite3.connect('touch_typing.db')
        db = conn.cursor()

        # Ensure username was submitted
        # ユーザー名の入力を確認
        if not request.form.get("username"):
            return apology("input your username", 403)

        # Ensure password was submitted
        # パスワードの入力を確認
        elif not request.form.get("current_password"):
            return apology("provide your current password", 403)

        # Ensure new password was submitted
        # 新しいパスワードの入力を確認
        elif not request.form.get("new_password"):
            #flash(request.form.get("new_password"))
            return apology("input your new password", 403)

        # Ensure both new passwords match
        # 新しいパスワードが一致するか確認
        elif request.form.get("new_password") != request.form.get("new_password_again"):
            return apology("new passwords don't match", 403)

        # extract user name from table users
        # テーブルusersからユーザー名を抽出
        else:
            db.execute("SELECT * FROM users WHERE user_name = :user_name",
                        {"user_name":request.form.get("username")})

            current_user = db.fetchone()

            # whether the username is registered
            # ユーザー名がデータベースに登録されているかどうか確認
            if request.form.get("username") != current_user[1]:
                return apology("no such username", 403)

        # extract user name from table users
        # テーブルusersからユーザー名を抽出
        db.execute("SELECT * FROM users WHERE user_name = :user_name",
                    {"user_name":request.form.get("username")})

        user_in_db = db.fetchone()

        # if the user's id is not that of the administrator
        # or the user name does not match the user name of the logged in user
        # ユーザーが管理者ではない，またはユーザー名が現在ログインしているユーザーと一致しない場合
        if (session["user_id"] != 1) and (session["user_id"]  != user_in_db[0]):
                return apology("you are not allowed to change someone else's passwords!", 403)

        # if the user's id is not that of the administrator
        # or the password does not match that of the logged in user
        # ユーザーが管理者ではない，またはパスワードが現在ログインしているユーザーのものと一致しない場合
        if (session["user_id"] != 1) and not check_password_hash(user_in_db[2], request.form.get("current_password")):
                return apology("current password doesn't match!", 403)

        # update the table with new password
        # すべてのチェックをクリアしたらデータベースを更新する
        db.execute("UPDATE users SET user_password = :new_password WHERE id = :user_id AND user_name = :user_name",
                    {"user_id":user_in_db[0], "user_name":user_in_db[1], "new_password":generate_password_hash(request.form.get("new_password"))})

        # update database
        # データベースを更新
        conn.commit()

        # record the activity
        # テーブルhistoryに登録
        db.execute("INSERT INTO history(user_id, activity) VALUES (:user_id, :action)",
                    {"user_id":user_in_db[0], "action":"Change Password"})

        # commit and close in order to update the database
        # データベースの更新と一旦終了
        conn.commit()
        conn.close()

        # Redirect user /
        # /を表示させる
        return redirect("/")

    # if Get method was used to access the content
    # メソッドにアクセスをしたか場合の処理
    else:
        # if Get method was used to access the content
        # メソッドにアクセスをしたか場合の処理
        return render_template("new_password.html")

# ########################################################

@app.route("/sample_file_to_update", methods=["GET", "POST"])
@login_required
def sample_file_to_update():
    """ this function is used only when the user is logged in as administrator """
    """ it is used to update or store the sample text """
    """管理者が選んだ文章をファイルから取り出して，index.htmlのテキストエリアに表示させる"""

    # Postメソッドにアクセスをしたか場合の処理
    if request.method == "POST":

        # start the database
        # データベースに接続する
        conn = sqlite3.connect('touch_typing.db')
        db = conn.cursor()

        # check whether sample file is selected
        # サンプルファイルが選択されているか確認する
        if request.form.get("selected_sample") == 'not_chosen':
            return redirect ("/")

        # open the selected file
        # ファイルを開く．
        open_file = open(SAMPLE_PATH + request.form.get("selected_sample"), 'r')

        # read it
        # 中身を取り出す
        text_inside_file = open_file.read()

        # close the file
        # ファイルを閉じる
        open_file.close

        # store user info
        # ログインしているユーザーの課題作成状況
        user_info_5 = []

        # store all users' current work progress
        # すべてのユーザーの課題作成状況
        all_current_situation_5 = []

        # store all users' activities
        # すべてのユーザーのログインなどの履歴
        all_info_5 = []

        # select the user's current work situation. Info about all the NUMBER_OF_TEXTS
        # データベースの「user_input」のテーブルから「ユーザー」が入力したものを抽出する
        db.execute("SELECT * FROM user_input WHERE user_id = :user",
                              {"user":session["user_id"]})

        user_db = db.fetchall()

        for row in user_db:
            # open the sample file and obtain its length
            # サンプルファイル、テキストの中の文字数を数える
            sample_file =  open(SAMPLE_PATH + row[3], 'r')
            sample_text = sample_file.read()
            sample_size = len(sample_text)

            sample_file.close()

            # add to the list
            # リストに追加する
            user_info_5.append(list((row[2],row[3], row[4], sample_size, row[5], row[6])))

        # commit and close in order to update the database
        # データベースの更新と一旦終了
        conn.commit()
        conn.close()

        # render index.html
        # index.htmlのページにユーザーの情報を表示させる
        return render_template("index.html", user_info = user_info_5, all_info = all_info_5,all_current_situation=all_current_situation_5,current_user = session["user_id"], text_inside_file = text_inside_file, file_name = request.form.get("selected_sample"))

    # Getメソッドにアクセスをしたか場合の処理
    else:
        return render_template("login.html")

# ########################################################

@app.route("/save_sample_text", methods=["GET", "POST"])
@login_required
def save_sample_text():
    """ this function is used only when the user is logged in as administrator """
    """ it is used to save the sample text """
    """管理者がサンプルの文章を送信したときに実行される関数"""

    # Postメソッドにアクセスをしたか場合の処理
    if request.method == "POST":

        # start the database
        # データベースに接続する
        conn = sqlite3.connect('touch_typing.db')
        db = conn.cursor()

        # open, save and close sample file
        # ファイルを開き，保存し，閉じる
        open_file = open(SAMPLE_PATH + request.form.get("selected_sample"), 'w')
        open_file.write(request.form.get("save_sample_text"))
        open_file.close()

        # record the activity
        # テーブルhistoryに登録
        log_message = "updated " + request.form.get("selected_sample")
        db.execute("INSERT INTO history(user_id, activity) VALUES (:user_id, :action)",{"user_id":session["user_id"], "action":log_message})

        # commit and close in order to update the database
        # データベースの更新と一旦終了
        conn.commit()
        conn.close()

        # Redirect user /
        # /を表示させる
        return redirect("/")

    # if Get method was used to access the content
    # メソッドにアクセスをしたか場合の処理
    else:
        return render_template("login.html")

# ########################################################

@app.route("/choose_your_text_to_input", methods=["GET", "POST"])
@login_required
def choose_your_text_to_input():
    """ function to be called when the user selected a file to input """
    """「index.html」で入力する課題が選択された時の処理"""

    # Postメソッドにアクセスをしたか場合の処理
    if request.method == "POST":

        # start the database
        # データベースに接続する
        conn = sqlite3.connect('touch_typing.db')
        db = conn.cursor()

        # check whether sample file is selected
        # サンプルファイルが選択されているか確認する
        if request.form.get("selected_input_file_name") == 'not_chosen':
            return redirect ("/")

        # select the user's current work situation. Info about all the NUMBER_OF_TEXTS
        # データベースの「user_input」のテーブルから「ユーザー」が入力したものを抽出する
        db.execute("SELECT * FROM user_input WHERE user_id = :user",
                    {"user":session["user_id"]})

        current_user = db.fetchone()

        # open file
        # ファイルを開く．
        open_input_file = open(USER_PATH + current_user[2] + '/' + request.form.get("selected_input_file_name"), 'r')

        # read it
        # 中身を取り出す
        text_to_update = open_input_file.read()

        # close file
        # ファイルを閉じる
        open_input_file.close()

        # open sample file
        # サンプルファイルを開く
        open_sample_file = open(SAMPLE_PATH + request.form.get("selected_input_file_name"), 'r')

        # read it
        # 中身を取り出す
        sample_text = open_sample_file.read()

        # close file
        # サンプルファイルを閉じる
        open_sample_file.close()

        # replace '\n' code to html code '<br>'. it is necessary because the sample text
        # will be shown on a new html window. otherwise the '\n' will be ignored
        # html ファイルに出力したときに改行が認識されるようにタグへ変換する
        sample_text=sample_text.replace("\n","<br>")

        # commit and close in order to update the database
        # データベースの更新と一旦終了
        conn.commit()
        conn.close()

        # render input_text.html
        # メインのページの処理へ移動する
        return render_template("input_text.html", text_to_update=text_to_update, file_name=request.form.get("selected_input_file_name"), sample_text=sample_text)

    # if Get method was used to access the content
    # メソッドにアクセスをしたか場合の処理
    else:
        # Redirect user /
        # /を表示させる
        return redirect("/")

# ########################################################

@app.route("/update_my_input_file", methods=["GET", "POST"])
@login_required
def update_my_input_file():
    """ this function updates the input file """
    """「input_text.html」で入力した文章を保存する時の処理"""

    # Postメソッドにアクセスをしたか場合の処理
    if request.method == "POST":

        # start the database
        # データベースに接続する
        conn = sqlite3.connect('touch_typing.db')
        db = conn.cursor()

        # get file name
        # ファイル名を受け取る
        input_text = request.form.get("input_text")

        # get the length of the input file
        # 入力ファイルのサイズを計測する
        size_of_input_text=len(input_text)

        # select the user's current work situation. Info about all the NUMBER_OF_TEXTS
        # データベースの「user_input」のテーブルから「ユーザー」が入力したものを抽出する
        db.execute("SELECT * FROM user_input WHERE user_id = :user",
                    {"user":session["user_id"]})

        # get the user name
        # ユーザー名を格納する
        current_user = db.fetchone()

        # open, save and close the input file
        # ファイルを開いて，テキストを格納する．
        open_write_file = open(USER_PATH + current_user[2] + '/' + request.form.get("input_file_name"), 'w')
        open_write_file.write(input_text)
        open_write_file.close()

        # open, read and close the sample file
        # サンプルファイルを開く．
        open_sample_file = open(SAMPLE_PATH + request.form.get("input_file_name"), 'r')
        sample_text = open_sample_file.read()
        open_sample_file.close()

        # reopen, reread and close the input file
        # ファイルを開いて，格納したテキストを読み取る．
        open_input_file = open(USER_PATH + current_user[2] + '/' + request.form.get("input_file_name"), 'r')
        read_input_text=open_input_file.read()
        open_input_file.close()

        # compute match ration
        # 入力とサンプルファイルを比較し，一致率を計算する
        match_ratio = round(difflib.SequenceMatcher(None, read_input_text, sample_text).ratio()*100,2)

        # update user_input table
        # テーブルuser_inputを更新する
        db.execute("UPDATE user_input SET input_done = :input_done, input_match = :input_match WHERE user_id = :user_id AND input_file_name = :input_file_name",
                    {"input_done":size_of_input_text, "input_match":match_ratio, "user_id":session["user_id"], "input_file_name":request.form.get("input_file_name")})

        # update database
        # データベースを更新
        conn.commit()

        # record the activity
        # テーブルhistoryに登録
        log_message = "updated " + request.form.get("input_file_name")
        db.execute("INSERT INTO history(user_id, activity) VALUES (:user_id, :action)", {"user_id":session["user_id"], "action":log_message})

        # replace '\n' code to html code '<br>'. it is necessary because the sample text
        # will be shown on a new html window. otherwise the '\n' will be ignored
        # html ファイルに出力したときに改行が認識されるようにタグへ変換する
        sample_text=sample_text.replace("\n","<br>")

        # commit and close in order to update the database
        # データベースの更新と一旦終了
        conn.commit()
        conn.close()

        # render input_text.html
        # メインのページの処理へ移動する
        return render_template("input_text.html", text_to_update=input_text, file_name=request.form.get("input_file_name"), sample_text=sample_text)

    # if Get method was used to access the content
    # メソッドにアクセスをしたか場合の処理
    else:
        # render login.html
        # ログインのページへ移動する
        return render_template("login.html")

# ########################################################

@app.route("/history")
@login_required
def history():
    """ this function displays user's activities """
    """履歴の表示"""

    # start the database
    # データベースに接続する
    conn = sqlite3.connect('touch_typing.db')
    db = conn.cursor()

    # store users' activities
    # ユーザーのログインなどの履歴
    user_info = []

    # extract user's activity from history table
    # データベースの「history」テーブルからユーザーの「履歴」を抽出する
    db.execute("SELECT * FROM history WHERE user_id = :user ORDER BY last_update DESC",
                {"user":session["user_id"]})

    user_db = db.fetchall()

    # append the info to the list
    # ユーザの履歴
    for row in user_db:
        user_info.append(list((row[2], row[3])))

    # commit and close in order to update the database
    # データベースの更新と一旦終了
    conn.commit()
    conn.close()

    # render history.html
    # history.htmlのページにユーザーの情報を表示させる
    return render_template("history.html", user_info=user_info, current_user = session["user_id"])

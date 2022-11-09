from flask import Flask, render_template, request, make_response, jsonify, redirect, url_for
import os, json
import jwt, time
import random
import pymysql
from dotenv import load_dotenv
from passlib.hash import sha256_crypt
from functools import wraps

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secretkey'

def create_connection():
    return pymysql.connect(host= os.getenv("RDS_HOST"),
        port = 3306,
        user = os.getenv("RDS_USER"), 
        password = os.getenv("RDS_PSW"),
        database = 'develop'
        )

def create_table():
    db = create_connection()
    cursor = db.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS member_prof(\
        mbr_uid VARCHAR(50) PRIMARY KEY,\
        account VARCHAR(50),\
        password VARCHAR(255),\
        access_token VARCHAR(255),\
        access_expired INT,\
        gender VARCHAR(50),\
        birthday date,\
        job_type VARCHAR(100),\
        industry_type VARCHAR(100),\
        marriage VARCHAR(50),\
        education VARCHAR(50),\
        address_res VARCHAR(1024),\
        address_mail VARCHAR(1024),\
        life_stage_tag VARCHAR(255),\
        digi_level_tag VARCHAR(255),\
        vip VARCHAR(50), \
        sys_update_dt timestamp)")

    cursor.execute("CREATE TABLE IF NOT EXISTS tag(\
        tag_id VARCHAR(50) PRIMARY KEY,\
        tag_name VARCHAR(50))")

    cursor.execute("CREATE TABLE IF NOT EXISTS member_card(\
        mbr_uid VARCHAR(50) PRIMARY KEY, FOREIGN KEY(mbr_uid) REFERENCES member_prof(mbr_uid) ON DELETE CASCADE, \
        card_nbr varchar(100),\
        card_type varchar(100),\
        open_dt date,\
        expire_dt date,\
        card_status varchar(50),\
        card_level varchar(50),\
        prime_flag varchar(50),\
        card_class varchar(100),\
        sys_created_dtm timestamp,\
        sys_updated_dtm timestamp)")

    cursor.execute("CREATE TABLE IF NOT EXISTS member_account(\
        mbr_uid VARCHAR(50) PRIMARY KEY, FOREIGN KEY(mbr_uid) REFERENCES member_prof(mbr_uid) ON DELETE CASCADE, \
        account_nbr varchar(100),\
        account_type varchar(100),\
        open_dt date,\
        account_status varchar(50),\
        sys_created_dtm timestamp,\
        sys_updated_dtm timestamp)")

    cursor.execute("CREATE TABLE IF NOT EXISTS member_insurance(\
        mbr_uid VARCHAR(50) PRIMARY KEY, FOREIGN KEY(mbr_uid) REFERENCES member_prof(mbr_uid) ON DELETE CASCADE, \
        order_id varchar(50),\
        ins_name varchar(100),\
        ins_type varchar(100),\
        order_dt date,\
        start_dt date,\
        expire_dt date,\
        ins_status varchar(50),\
        sys_created_dtm timestamp,\
        sys_updated_dtm timestamp)")

    cursor.execute("CREATE TABLE IF NOT EXISTS member_investment(\
        mbr_uid VARCHAR(50) PRIMARY KEY, FOREIGN KEY(mbr_uid) REFERENCES member_prof(mbr_uid) ON DELETE CASCADE, \
        order_id varchar(50),\
        inv_type varchar(50),\
        inv_name varchar(100),\
        buy_sale varchar(50),\
        amount int,\
        created_dtm datetime,\
        sys_created_dtm timestamp,\
        sys_updated_dtm timestamp)")

    cursor.execute("CREATE TABLE IF NOT EXISTS card_txn(\
        mbr_uid VARCHAR(50) PRIMARY KEY, FOREIGN KEY(mbr_uid) REFERENCES member_prof(mbr_uid) ON DELETE CASCADE, \
        created_dtm timestamp,\
        txn_amt int,\
        payment_method varchar(50),\
        payment_channel varchar(50),\
        abroad_flag boolean,\
        country varchar(50),\
        mcc_category_l1 varchar(100),\
        mcc_category_l2 varchar(100),\
        inst_flag boolean)")

    cursor.execute("CREATE TABLE IF NOT EXISTS tag_result(\
        mbr_uid VARCHAR(50) PRIMARY KEY, FOREIGN KEY(mbr_uid) REFERENCES member_prof(mbr_uid) ON DELETE CASCADE, \
        category VARCHAR(50),\
        sub_category VARCHAR(50),\
        expire_after INT,\
        tag_id VARCHAR(50),\
        tag_name VARCHAR(50),\
        tag_expire_date DATE,\
        FOREIGN KEY(tag_id) REFERENCES tag(tag_id) ON DELETE CASCADE)")

    cursor.execute("CREATE TABLE IF NOT EXISTS web_events(\
        mbr_uid VARCHAR(50) PRIMARY KEY, FOREIGN KEY(mbr_uid) REFERENCES member_prof(mbr_uid) ON DELETE CASCADE, \
        event_time timestamp,\
        event_name VARCHAR(100),\
        web_id VARCHAR(50),\
        attributed_touch_type VARCHAR(30),\
        attributed_touch_time timestamp,\
        event_value VARCHAR(50),\
        event_source VARCHAR(20),\
        channel VARCHAR(50),\
        country_code VARCHAR(10),\
        city VARCHAR(100),\
        ip VARCHAR(30),\
        web_language VARCHAR(30),\
        platform VARCHAR(20),\
        device_type VARCHAR(50),\
        os_version VARCHAR(20),\
        http_referrer VARCHAR(255),\
        original_url VARCHAR(255))")

    cursor.execute("CREATE TABLE IF NOT EXISTS image(\
        image_id VARCHAR(50) PRIMARY KEY,\
        image_name VARCHAR(50))")

    cursor.execute("CREATE TABLE IF NOT EXISTS web_tag(\
        web_id VARCHAR(50),\
        tag_id VARCHAR(50),\
        PRIMARY KEY CLUSTERED(web_id, tag_id),\
        FOREIGN KEY(tag_id) REFERENCES tag(tag_id) ON DELETE CASCADE)")

    cursor.execute("CREATE TABLE IF NOT EXISTS image_tag(\
        image_id VARCHAR(50),\
        tag_id VARCHAR(50),\
        PRIMARY KEY CLUSTERED(image_id, tag_id),\
        FOREIGN KEY(tag_id) REFERENCES tag(tag_id) ON DELETE CASCADE,\
        FOREIGN KEY(image_id) REFERENCES image(image_id) ON DELETE CASCADE)")

    cursor.execute("CREATE TABLE IF NOT EXISTS image_filter(\
        image_id VARCHAR(50),\
        proh_tag VARCHAR(50),\
        PRIMARY KEY CLUSTERD(image_id, proh_tag),\
        FOREIGN KEY(proh_tag) REFERENCES tag(tag_id) ON DELETE CASCADE,\
        FOREIGN KEY(image_id) REFERENCES image(image_id) ON DELETE CASCADE)")

    cursor.execute("CREATE TABLE IF NOT EXISTS member_image(\
        mbr_uid VARCHAR(50), \
        image_id VARCHAR(50),\
        PRIMARY KEY CLUSTERED(mbr_uid, image_id),\
        FOREIGN KEY(mbr_uid) REFERENCES member_prof(mbr_uid) ON DELETE CASCADE,\
        FOREIGN KEY(image_id) REFERENCES image(image_id) ON DELETE CASCADE)")

# sql = "insert into member_prof values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
# cursor.execute(sql,('01', 'A123456789', '$5$rounds=535000$BaEX9uJ.laffwmAB$7RFzPrY.5s7N5TzFes/CVp/UW/vucoKqKO1exhl/Ur6', '0', 3600, 'female', '1999-09-09', 'teacher', 'education', 'N', 'college', 'Taipei City', 'Taipei City', 'freshman', 'high', 'N', '2022-11-11 11:11:11'))
# cursor.execute(sql,('02', 'B123456789', '$5$rounds=535000$BaEX9uJ.laffwmAB$7RFzPrY.5s7N5TzFes/CVp/UW/vucoKqKO1exhl/Ur6', '0', 3600, 'female', '1979-09-09', 'farmer', 'argriculture', 'Y', 'college', 'Taipei City', 'Taipei City', 'newly married', 'high', 'N', '2022-11-11 11:11:11'))
# cursor.execute(sql,('03', 'C123456789', '$5$rounds=535000$BaEX9uJ.laffwmAB$7RFzPrY.5s7N5TzFes/CVp/UW/vucoKqKO1exhl/Ur6', '0', 3600, 'male', '1969-09-09', 'musician', 'art', 'N', 'college', 'Taipei City', 'Taipei City', 'retired', 'high', 'N', '2022-11-11 11:11:11'))
# cursor.execute(sql,('04', 'D123456789', '$5$rounds=535000$BaEX9uJ.laffwmAB$7RFzPrY.5s7N5TzFes/CVp/UW/vucoKqKO1exhl/Ur6', '0', 3600, 'male', '1999-09-09', 'HR', 'IT', 'N', 'college', 'New Taipei City', 'Taipei City', 'freshman', 'high', 'N', '2022-11-11 11:11:11'))
# cursor.execute(sql,('05', 'E123456789', '$5$rounds=535000$BaEX9uJ.laffwmAB$7RFzPrY.5s7N5TzFes/CVp/UW/vucoKqKO1exhl/Ur6', '0', 3600, 'male', '1979-09-09', 'engineer', 'IT', 'Y', 'college', 'Taipei City', 'Taipei City', 'newly married', 'high', 'N', '2022-11-11 11:11:11'))
# cursor.execute(sql,('06', 'F123456789', '$5$rounds=535000$BaEX9uJ.laffwmAB$7RFzPrY.5s7N5TzFes/CVp/UW/vucoKqKO1exhl/Ur6', '0', 3600, 'female', '1969-09-09', 'docter', 'medical', 'Y', 'college', 'Taipei City', 'Taipei City', 'retired', 'low', 'N', '2022-11-11 11:11:11'))
# db.commit()

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        db = create_connection()
        cursor = db.cursor()
        token = None
        # jwt is passed in the request header
        if 'Authorization' in request.headers:
            token = request.headers['Authorization']
        # return 401 if token is not passed
        if not token:
            return render_template('index.html', images=['Picture1.png', 'Picture2.png', 'Picture3.png'], state = '登入')
  
        try:
            # decoding the payload to fetch the stored details

            token = token.split(' ')[1]
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = data['account']
        except:
            return render_template('index.html', images=['Picture1.png', 'Picture2.png', 'Picture3.png'], state = '登入')
        # returns the current logged in users contex to the routes
        return  f(current_user, *args, **kwargs)
  
    return decorated


@app.route("/", methods=['GET'])
@token_required
def home(user):
    print('user:', user)
    db = create_connection()
    cursor = db.cursor()
    sql = "SELECT image_name FROM image \
    JOIN member_image ON image.image_id = member_image.image_id\
    JOIN member_prof ON member_prof.mbr_uid = member_image.mbr_uid\
    WHERE member_prof.account = %s"
    cursor.execute(sql, (user))
    images = cursor.fetchall()
    images = list(x[0] for x in images)
    print(images)
    return render_template("index.html", images=images, state = f'{user}，您好')

@app.route("/login", methods=['POST', 'GET'])
def login():
    db = create_connection()
    cursor = db.cursor()

    account = request.form['email']
    psw = request.form['psw']

    cursor.execute("SELECT account, password FROM member_prof WHERE account=%s", (account))
    member = cursor.fetchall()
    db.commit()
    
    if len(member) == 0:
        return make_response('', 401)
    
    if sha256_crypt.verify(psw, member[0][1]) == False:
        return make_response('', 401)
    
    access_expired = 3600
    payload = {
        'exp': int(time.time()) + access_expired,
        'account': account,
        'password': sha256_crypt.encrypt(psw)
    }
    private_key = open('.ssh/id_rsa', 'r').read()
    access_token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
    
    cursor.execute("UPDATE member_prof SET access_token=%s WHERE account=%s",(access_token, account))
    db.commit()
    return jsonify({'token': access_token})

@app.route("/collectTag", methods=['POST'])
def processUserInfo():
    print(request.get_json())
    update_tag_result_click()
    return render_template("index.html")

def update_tag_result_click():
    # 新增網站點擊事件 web_events 及其對應的 tag_result
    pass

def update_tag_result_prod():
    # 檢查持有的商品，持有的商品可以去抓 tag_result 中，是 buy 開頭的 tag，比較新買的這個商品，是否已經有在 tag 中，再看要怎麼處理
    pass

def insert_tag_profile():
    pass

def insert_tag_prod():
    pass

def insert_tag_trans():
    pass

@app.route("/cardintro")
def card_intro():
    return render_template('card_intro.html')

@app.route("/carddiscount")
def card_discount():
    return render_template('card_discount.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
from flask import Flask, render_template, request, make_response, jsonify, redirect, url_for
import os, json
import jwt, time
import random
import pymysql
from dotenv import load_dotenv
from passlib.hash import sha256_crypt
from functools import wraps
from datetime import datetime
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

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
        risk_preference_tag VARCHAR(255),\
        vip VARCHAR(50), \
        sys_update_dt timestamp)")

    cursor.execute("CREATE TABLE IF NOT EXISTS tag(\
        tag_id VARCHAR(50) PRIMARY KEY,\
        tag_name VARCHAR(50))")

    cursor.execute("CREATE TABLE IF NOT EXISTS member_card(\
        mbr_uid VARCHAR(50), \
        card_type varchar(100),\
        open_dt date,\
        expire_dt date,\
        card_status varchar(50),\
        PRIMARY KEY CLUSTERED(mbr_uid, card_type),\
        FOREIGN KEY(mbr_uid) REFERENCES member_prof(mbr_uid) ON DELETE CASCADE)")

    cursor.execute("CREATE TABLE IF NOT EXISTS member_account(\
        mbr_uid VARCHAR(50), \
        account_type varchar(100),\
        amount INT,\
        open_dt date,\
        account_status varchar(50),\
        PRIMARY KEY CLUSTERED(mbr_uid, account_type),\
        FOREIGN KEY(mbr_uid) REFERENCES member_prof(mbr_uid) ON DELETE CASCADE)")

    cursor.execute("CREATE TABLE IF NOT EXISTS member_insurance(\
        mbr_uid VARCHAR(50), \
        insurance_type varchar(100),\
        start_dt date,\
        expire_dt date,\
        ins_status varchar(50),\
        PRIMARY KEY CLUSTERED(mbr_uid, insurance_type),\
        FOREIGN KEY(mbr_uid) REFERENCES member_prof(mbr_uid) ON DELETE CASCADE)")

    cursor.execute("CREATE TABLE IF NOT EXISTS member_investment(\
        mbr_uid VARCHAR(50), \
        inv_type varchar(50),\
        investment_type varchar(100),\
        amount int,\
        created_dtm datetime,\
        sys_created_dtm timestamp,\
        sys_updated_dtm timestamp,\
        PRIMARY KEY CLUSTERED(mbr_uid, investment_type, created_dtm),\
        FOREIGN KEY(mbr_uid) REFERENCES member_prof(mbr_uid) ON DELETE CASCADE)")

    cursor.execute("CREATE TABLE IF NOT EXISTS card_txn(\
        mbr_uid VARCHAR(50), \
        txn_id INT,\
        created_dtm timestamp,\
        txn_amt int,\
        payment_method varchar(50),\
        abroad_flag boolean,\
        country varchar(50),\
        mcc_category_l1 varchar(100),\
        mcc_category_l2 varchar(100),\
        PRIMARY KEY CLUSTERED(mbr_uid, txn_id),\
        FOREIGN KEY(mbr_uid) REFERENCES member_prof(mbr_uid) ON DELETE CASCADE)")

    cursor.execute("CREATE TABLE IF NOT EXISTS tag_result(\
        mbr_uid VARCHAR(50),\
        tag_id VARCHAR(50),\
        tag_expire_date DATE,\
        PRIMARY KEY CLUSTERED(mbr_uid, tag_id),\
        FOREIGN KEY(mbr_uid) REFERENCES member_prof(mbr_uid) ON DELETE CASCADE, \
        FOREIGN KEY(tag_id) REFERENCES tag(tag_id) ON DELETE CASCADE)")

    cursor.execute("CREATE TABLE IF NOT EXISTS web_events(\
        mbr_uid VARCHAR(50),\
        web_id VARCHAR(50),\
        attributed_touch_time timestamp,\
        PRIMARY KEY CLUSTERED(mbr_uid, web_id, attributed_touch_time),\
        FOREIGN KEY(mbr_uid) REFERENCES member_prof(mbr_uid) ON DELETE CASCADE)")

    cursor.execute("CREATE TABLE IF NOT EXISTS image(\
        image_id VARCHAR(50) PRIMARY KEY,\
        image_name VARCHAR(50),\
        tag_id VARCHAR(50))")

    cursor.execute("CREATE TABLE IF NOT EXISTS web_tag(\
        web_id VARCHAR(50),\
        tag_id VARCHAR(50),\
        PRIMARY KEY CLUSTERED(web_id, tag_id),\
        FOREIGN KEY(tag_id) REFERENCES tag(tag_id) ON DELETE CASCADE)")

    cursor.execute("CREATE TABLE IF NOT EXISTS image_filter(\
        image_id VARCHAR(50),\
        proh_tag VARCHAR(50),\
        details VARCHAR(50),\
        PRIMARY KEY CLUSTERD(image_id, proh_tag),\
        FOREIGN KEY(proh_tag) REFERENCES tag(tag_id) ON DELETE CASCADE,\
        FOREIGN KEY(image_id) REFERENCES image(image_id) ON DELETE CASCADE)")

    cursor.execute("CREATE TABLE IF NOT EXISTS member_image(\
        mbr_uid VARCHAR(50), \
        image_id VARCHAR(50),\
        score FLOAT,\
        PRIMARY KEY CLUSTERED(mbr_uid, image_id),\
        FOREIGN KEY(mbr_uid) REFERENCES member_prof(mbr_uid) ON DELETE CASCADE,\
        FOREIGN KEY(image_id) REFERENCES image(image_id) ON DELETE CASCADE)")


def insert_data():
    db = create_connection()
    cursor = db.cursor()

    # insert member_prof
    sql = "insert into member_prof values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    cursor.execute(sql,('01', 'A123456789', '$5$rounds=535000$BaEX9uJ.laffwmAB$7RFzPrY.5s7N5TzFes/CVp/UW/vucoKqKO1exhl/Ur6', '0', 3600, 'female', '1999-09-09', 'teacher', 'education', 'N', 'college', 'Taipei City', 'Taipei City', 'freshman', 'low', 'N', '2022-11-11 11:11:11'))
    cursor.execute(sql,('02', 'B123456789', '$5$rounds=535000$BaEX9uJ.laffwmAB$7RFzPrY.5s7N5TzFes/CVp/UW/vucoKqKO1exhl/Ur6', '0', 3600, 'female', '1979-09-09', 'manager', 'finance', 'Y', 'college', 'Taipei City', 'Taipei City', 'career peak', 'high', 'N', '2022-11-11 11:11:11'))
    cursor.execute(sql,('03', 'C123456789', '$5$rounds=535000$BaEX9uJ.laffwmAB$7RFzPrY.5s7N5TzFes/CVp/UW/vucoKqKO1exhl/Ur6', '0', 3600, 'female', '1979-09-09', 'musician', 'art', 'N', 'college', 'Taipei City', 'Taipei City', 'retired', 'low', 'N', '2022-11-11 11:11:11'))
    cursor.execute(sql,('04', 'D123456789', '$5$rounds=535000$BaEX9uJ.laffwmAB$7RFzPrY.5s7N5TzFes/CVp/UW/vucoKqKO1exhl/Ur6', '0', 3600, 'male', '1999-09-09', 'farmer', 'argriculture', 'N', 'college', 'New Taipei City', 'Taipei City', 'freshman', 'high', 'N', '2022-11-11 11:11:11'))
    cursor.execute(sql,('05', 'E123456789', '$5$rounds=535000$BaEX9uJ.laffwmAB$7RFzPrY.5s7N5TzFes/CVp/UW/vucoKqKO1exhl/Ur6', '0', 3600, 'male', '1979-09-09', 'engineer', 'IT', 'Y', 'college', 'Taipei City', 'Taipei City', 'newly married', 'low', 'N', '2022-11-11 11:11:11'))
    cursor.execute(sql,('06', 'F123456789', '$5$rounds=535000$BaEX9uJ.laffwmAB$7RFzPrY.5s7N5TzFes/CVp/UW/vucoKqKO1exhl/Ur6', '0', 3600, 'male', '1969-09-09', 'docter', 'medical', 'Y', 'college', 'Taipei City', 'Taipei City', 'retired', 'high', 'N', '2022-11-11 11:11:11'))
    db.commit()

    # insert tag
    sql = "insert into tag values (%s, %s)"
    # profile related
    cursor.execute(sql, ('01', 'freshman'))
    cursor.execute(sql, ('02', 'newly married'))
    cursor.execute(sql, ('03', 'career peak'))
    cursor.execute(sql, ('04', 'retired'))
    cursor.execute(sql, ('05', 'olderly'))
    cursor.execute(sql, ('06', 'risk averse'))
    cursor.execute(sql, ('07', 'risk preference'))
    cursor.execute(sql, ('08', 'male'))
    cursor.execute(sql, ('09', 'female'))
    cursor.execute(sql, ('10', 'wealthy'))
    cursor.execute(sql, ('11', 'middle class'))
    cursor.execute(sql, ('12', 'poor'))
    # web click
    cursor.execute(sql, ('13', 'interested in card'))
    cursor.execute(sql, ('14', 'interested in stock'))
    cursor.execute(sql, ('15', 'interested in fund'))
    cursor.execute(sql, ('16', 'interested in foreign exchange'))
    cursor.execute(sql, ('17', 'interested in structured notes'))
    cursor.execute(sql, ('18', 'interested in insurance'))
    # process
    cursor.execute(sql, ('19', 'having card1'))
    cursor.execute(sql, ('20', 'having card2'))
    cursor.execute(sql, ('21', 'having card3'))
    cursor.execute(sql, ('22', 'having insurance1'))
    cursor.execute(sql, ('23', 'having insurance2'))
    cursor.execute(sql, ('24', 'having insurance3'))
    cursor.execute(sql, ('25', 'having insurance4'))
    cursor.execute(sql, ('26', 'having insurance5'))
    cursor.execute(sql, ('27', 'having insurance6'))
    cursor.execute(sql, ('28', 'having insurance7'))
    cursor.execute(sql, ('29', 'having insurance8'))
    cursor.execute(sql, ('30', 'having insurance9'))
    cursor.execute(sql, ('31', 'having stock1'))
    cursor.execute(sql, ('32', 'having stock2'))
    cursor.execute(sql, ('33', 'having stock3'))
    cursor.execute(sql, ('34', 'having security1'))
    cursor.execute(sql, ('35', 'having security2'))
    cursor.execute(sql, ('36', 'having security3'))
    cursor.execute(sql, ('37', 'having fund1'))
    cursor.execute(sql, ('38', 'having fund2'))
    cursor.execute(sql, ('39', 'having fund3'))
    cursor.execute(sql, ('40', 'having foreign exchange1'))
    cursor.execute(sql, ('41', 'having foreign exchange2'))
    cursor.execute(sql, ('42', 'having foreign exchange3'))
    # life event interests
    cursor.execute(sql, ('43', 'interested in travel'))
    cursor.execute(sql, ('44', 'having pet'))
    cursor.execute(sql, ('45', 'mobile payment'))
    cursor.execute(sql, ('46', 'online shopping'))
    cursor.execute(sql, ('47', 'interested in Japan'))
    cursor.execute(sql, ('48', 'car and motorcycle'))
    cursor.execute(sql, ('49', 'public transportation'))
    cursor.execute(sql, ('50', 'frequent airport user'))
    cursor.execute(sql, ('51', 'interested in US dollar'))
    cursor.execute(sql, ('52', 'interested in RMB'))
    cursor.execute(sql, ('53', 'frequent hospital user'))

    # account
    cursor.execute(sql, ('54', 'having normal account'))
    cursor.execute(sql, ('55', 'having foreign account'))
    cursor.execute(sql, ('56', 'having digital account'))
    cursor.execute(sql, ('57', 'having security account'))
    db.commit()

    # insert image
    sql = "insert into image values (%s, %s, %s)"
    cursor.execute(sql, ('01', '廣告_信用卡_白金卡.png', '13, 43, 50'))
    cursor.execute(sql, ('02', '廣告_信用卡_悠遊聯名卡.png', '13, 45, 49'))
    cursor.execute(sql, ('03', '廣告_信用卡_藍星世界卡.png', '10, 13, 14, 15, 43, 50'))
    cursor.execute(sql, ('04', '廣告_旅平險_一般用戶.png', '18, 43'))
    cursor.execute(sql, ('05', '廣告_信用卡_申辦白金卡日本旅遊.png', '13, 43, 47, 50'))
    cursor.execute(sql, ('06', '廣告_旅平險_卡友優惠.png', '18, 43'))
    cursor.execute(sql, ('07', '廣告_信用卡_白金卡日本旅遊.png', '43, 47, 50'))
    cursor.execute(sql, ('08', '廣告_信用卡_白金卡網購優惠.png', '46'))
    cursor.execute(sql, ('09', '廣告_匯率_白金卡換匯優惠.png', '16'))
    cursor.execute(sql, ('10', '廣告_證券_藍星世界卡投資優惠.png', '14, 15, 16'))
    cursor.execute(sql, ('11', '廣告_信用卡_悠遊聯名卡網購優惠.png', '45, 46'))
    cursor.execute(sql, ('12', '廣告_保險_悠遊聯名卡保險優惠.png', '18, 48'))
    cursor.execute(sql, ('13', '廣告_保險_騎車保險.png', '18, 48'))
    cursor.execute(sql, ('14', '廣告_保險_醫療傷害保險.png', '18, 53'))
    cursor.execute(sql, ('15', '廣告_保險_投資型保險.png', '04, 05, 18'))
    cursor.execute(sql, ('16', '廣告_保險_寵物險.png', '10'))
    cursor.execute(sql, ('17', '廣告_證券_證券開戶.png', '14, 15, 16'))
    cursor.execute(sql, ('18', '廣告_證券_投資理財.png', '14, 15, 16'))
    db.commit()

    # insert image filter
    sql = "INSERT INTO image_filter VALUES(%s, %s, %s)"
    cursor.execute(sql, ('01', '19', '有的會被排除'))
    cursor.execute(sql, ('02', '20', '有的會被排除'))
    cursor.execute(sql, ('03', '21', '有的會被排除'))
    cursor.execute(sql, ('04', '19', '有的會被排除'))
    cursor.execute(sql, ('04', '28', '有的會被排除'))
    cursor.execute(sql, ('05', '19', '有的會被排除'))
    cursor.execute(sql, ('06', '19', '沒有的會被排除'))
    cursor.execute(sql, ('06', '28', '有的會被排除'))
    cursor.execute(sql, ('07', '19', '沒有的會被排除'))
    cursor.execute(sql, ('08', '19', '沒有的會被排除'))
    cursor.execute(sql, ('09', '19', '沒有的會被排除'))
    cursor.execute(sql, ('10', '21', '沒有的會被排除'))
    cursor.execute(sql, ('11', '20', '沒有的會被排除'))
    cursor.execute(sql, ('12', '20', '沒有的會被排除'))
    cursor.execute(sql, ('12', '26', '有的會被排除'))
    cursor.execute(sql, ('13', '20', '有的會被排除'))
    cursor.execute(sql, ('13', '26', '有的會被排除'))
    cursor.execute(sql, ('14', '25', '有的會被排除'))
    cursor.execute(sql, ('14', '27', '有的會被排除'))
    cursor.execute(sql, ('15', '22', '有的會被排除'))
    cursor.execute(sql, ('15', '23', '有的會被排除'))
    cursor.execute(sql, ('15', '24', '有的會被排除'))
    cursor.execute(sql, ('16', '44', '沒有的會被排除'))
    cursor.execute(sql, ('16', '30', '有的會被排除'))
    cursor.execute(sql, ('17', '57', '有的會被排除'))
    cursor.execute(sql, ('18', '21', '有的會被排除'))
    db.commit()

    # insert member account
    sql = "insert into member_account values(%s, %s, %s, %s, %s)"
    cursor.execute(sql, ('01', 'normal', 100000, '2020-01-01', 'active'))
    cursor.execute(sql, ('01', 'digital', 1000, '2020-01-01', 'active'))
    cursor.execute(sql, ('02', 'normal', 9999459, '2020-01-01', 'active'))
    cursor.execute(sql, ('02', 'foreign', 478947, '2020-01-01', 'active'))
    cursor.execute(sql, ('02', 'digital', 47399, '2020-01-01', 'active'))
    cursor.execute(sql, ('02', 'securities', 27930, '2020-01-01', 'active'))
    cursor.execute(sql, ('03', 'normal', 304809, '2020-01-01', 'active'))
    cursor.execute(sql, ('04', 'normal', 7887983, '2020-01-01', 'active'))
    cursor.execute(sql, ('04', 'foreign', 74927, '2020-01-01', 'active'))
    cursor.execute(sql, ('05', 'normal', 5584894, '2020-01-01', 'active'))
    cursor.execute(sql, ('06', 'normal', 80983479, '2020-01-01', 'active'))
    cursor.execute(sql, ('06', 'foreign', 498790, '2020-01-01', 'active'))
    cursor.execute(sql, ('06', 'securities', 749797, '2020-01-01', 'active'))
    db.commit()

    # insert member card
    sql = "insert into member_card values(%s, %s, %s, %s, %s)"
    cursor.execute(sql, ('01', '悠遊聯名卡', '2020-01-01', '2028-01-01', 'active'))
    cursor.execute(sql, ('02', '白金卡', '2020-01-01', '2028-01-01', 'active'))
    cursor.execute(sql, ('02', '藍星世界卡', '2020-01-01', '2028-01-01', 'active'))
    cursor.execute(sql, ('05', '白金卡', '2020-01-01', '2028-01-01', 'active'))
    cursor.execute(sql, ('06', '白金卡', '2020-01-01', '2028-01-01', 'active'))
    cursor.execute(sql, ('06', '藍星世界卡', '2020-01-01', '2028-01-01', 'active'))
    db.commit()

    # insert member insurance
    sql = "insert into member_insurance values(%s, %s, %s, %s, %s)"
    cursor.execute(sql, ('01', '實支實付傷害醫療險', '2020-01-01', '2028-01-01', 'active'))
    cursor.execute(sql, ('01', '變動型終身壽險', '2020-01-01', '2028-01-01', 'active'))
    cursor.execute(sql, ('02', '人生外幣變額年金保險', '2020-01-01', '2028-01-01', 'active'))
    cursor.execute(sql, ('02', '實支實付傷害醫療險', '2020-01-01', '2028-01-01', 'active'))
    cursor.execute(sql, ('03', '人生變額年金保險', '2020-01-01', '2028-01-01', 'active'))
    cursor.execute(sql, ('03', '變動型終身壽險', '2020-01-01', '2028-01-01', 'active'))
    cursor.execute(sql, ('04', '機車強制險', '2020-01-01', '2028-01-01', 'active'))
    cursor.execute(sql, ('04', '意外住院日額傷害保險', '2020-01-01', '2028-01-01', 'active'))
    cursor.execute(sql, ('04', '騎乘機車或自行車傷害保險', '2020-01-01', '2028-01-01', 'active'))
    cursor.execute(sql, ('05', '變動型終身壽險', '2020-01-01', '2028-01-01', 'active'))
    cursor.execute(sql, ('05', '人生變額年金保險', '2020-01-01', '2028-01-01', 'active'))
    cursor.execute(sql, ('06', '寵物險', '2020-01-01', '2028-01-01', 'active'))
    cursor.execute(sql, ('06', '意外住院日額傷害保險', '2020-01-01', '2028-01-01', 'active'))
    cursor.execute(sql, ('06', '變動型終身壽險', '2020-01-01', '2028-01-01', 'active'))
    db.commit()

    # insert member investment
    sql = "insert into member_investment values(%s, %s, %s, %s, %s, %s, %s)"
    cursor.execute(sql, ('01', '外匯', '日幣', 1000, '2022-11-11 11:11:11', '2022-11-11 11:11:11', '2022-11-11 11:11:11'))
    cursor.execute(sql, ('02', '證券', 'IBM', 1000, '2022-11-11 11:11:11', '2022-11-11 11:11:11', '2022-11-11 11:11:11'))
    cursor.execute(sql, ('02', '證券', 'APPLE', 1000, '2022-11-11 11:11:11', '2022-11-11 11:11:11', '2022-11-11 11:11:11'))
    cursor.execute(sql, ('02', '外匯', '美元', 1000, '2022-11-11 11:11:11', '2022-11-11 11:11:11', '2022-11-11 11:11:11'))
    cursor.execute(sql, ('02', '基金', '貝萊德世界科技基金', 1000, '2022-11-11 11:11:11', '2022-11-11 11:11:11', '2022-11-11 11:11:11'))
    cursor.execute(sql, ('04', '股票', '台積電', 1000, '2022-11-11 11:11:11', '2022-11-11 11:11:11', '2022-11-11 11:11:11'))
    cursor.execute(sql, ('04', '股票', '聯發科', 1000, '2022-11-11 11:11:11', '2022-11-11 11:11:11', '2022-11-11 11:11:11'))
    cursor.execute(sql, ('05', '股票', '元大台灣 50', 1000, '2022-11-11 11:11:11', '2022-11-11 11:11:11', '2022-11-11 11:11:11'))
    cursor.execute(sql, ('06', '證券', 'GOOGLE', 1000, '2022-11-11 11:11:11', '2022-11-11 11:11:11', '2022-11-11 11:11:11'))
    cursor.execute(sql, ('06', '證券', 'APPLE', 1000, '2022-11-11 11:11:11', '2022-11-11 11:11:11', '2022-11-11 11:11:11'))
    cursor.execute(sql, ('06', '基金', '台灣高股息基金', 1000, '2022-11-11 11:11:11', '2022-11-11 11:11:11', '2022-11-11 11:11:11'))
    db.commit()

    # insert card transaction
    sql = "insert into card_txn values(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    cursor.execute(sql, ('01', 1, '2022-11-11 11:11:11', 1000, '百貨公司', False, 'Taiwan', '零售', '電燈泡'))
    cursor.execute(sql, ('02', 2, '2022-11-11 11:11:11', 50000, '線上', True, 'United States', '奢侈品', '包包'))
    cursor.execute(sql, ('02', 3, '2022-11-11 11:11:11', 8000, '百貨公司', False, 'Taiwan', '零售', '衣服'))
    cursor.execute(sql, ('05', 4, '2022-11-11 11:11:11', 3000, '百貨公司', False, 'Taiwan', '家具', '沙發'))
    cursor.execute(sql, ('06', 5, '2022-11-11 11:11:11', 2000, '寵物店', False, 'Taiwan', '寵物', '寵物美容'))
    db.commit()
    
    # insert tag result
    sql = "insert into tag_result values(%s, %s, %s)"
    cursor.execute(sql, ('01', '01', '2025-12-01'))
    cursor.execute(sql, ('01', '06', '2025-12-01'))
    cursor.execute(sql, ('01', '09', '2025-12-01'))
    cursor.execute(sql, ('01', '11', '2025-12-01'))
    cursor.execute(sql, ('01', '20', '2025-12-01'))
    cursor.execute(sql, ('01', '24', '2025-12-01'))
    cursor.execute(sql, ('01', '27', '2025-12-01'))
    cursor.execute(sql, ('01', '41', '2025-12-01'))
    cursor.execute(sql, ('01', '43', '2025-12-01'))
    cursor.execute(sql, ('01', '46', '2025-12-01'))
    cursor.execute(sql, ('01', '47', '2025-12-01'))
    cursor.execute(sql, ('01', '49', '2025-12-01'))
    cursor.execute(sql, ('01', '53', '2025-12-01'))
    cursor.execute(sql, ('01', '54', '2025-12-01'))
    cursor.execute(sql, ('01', '56', '2025-12-01'))
    cursor.execute(sql, ('02', '03', '2025-12-01'))
    cursor.execute(sql, ('02', '07', '2025-12-01'))
    cursor.execute(sql, ('02', '09', '2025-12-01'))
    cursor.execute(sql, ('02', '10', '2025-12-01'))
    cursor.execute(sql, ('02', '14', '2025-12-01'))
    cursor.execute(sql, ('02', '19', '2025-12-01'))
    cursor.execute(sql, ('02', '21', '2025-12-01'))
    cursor.execute(sql, ('02', '23', '2025-12-01'))
    cursor.execute(sql, ('02', '27', '2025-12-01'))
    cursor.execute(sql, ('02', '34', '2025-12-01'))
    cursor.execute(sql, ('02', '35', '2025-12-01'))
    cursor.execute(sql, ('02', '38', '2025-12-01'))
    cursor.execute(sql, ('02', '40', '2025-12-01'))
    cursor.execute(sql, ('02', '51', '2025-12-01'))
    cursor.execute(sql, ('02', '54', '2025-12-01'))
    cursor.execute(sql, ('02', '55', '2025-12-01'))
    cursor.execute(sql, ('02', '56', '2025-12-01'))
    cursor.execute(sql, ('02', '57', '2025-12-01'))
    cursor.execute(sql, ('03', '06', '2025-12-01'))
    cursor.execute(sql, ('03', '09', '2025-12-01'))
    cursor.execute(sql, ('03', '22', '2025-12-01'))
    cursor.execute(sql, ('03', '24', '2025-12-01'))
    cursor.execute(sql, ('03', '54', '2025-12-01'))
    cursor.execute(sql, ('04', '01', '2025-12-01'))
    cursor.execute(sql, ('04', '07', '2025-12-01'))
    cursor.execute(sql, ('04', '08', '2025-12-01'))
    cursor.execute(sql, ('04', '25', '2025-12-01'))
    cursor.execute(sql, ('04', '26', '2025-12-01'))
    cursor.execute(sql, ('04', '29', '2025-12-01'))
    cursor.execute(sql, ('04', '32', '2025-12-01'))
    cursor.execute(sql, ('04', '33', '2025-12-01'))
    cursor.execute(sql, ('04', '48', '2025-12-01'))
    cursor.execute(sql, ('04', '53', '2025-12-01'))
    cursor.execute(sql, ('04', '54', '2025-12-01'))
    cursor.execute(sql, ('04', '55', '2025-12-01'))
    cursor.execute(sql, ('05', '02', '2025-12-01'))
    cursor.execute(sql, ('05', '06', '2025-12-01'))
    cursor.execute(sql, ('05', '08', '2025-12-01'))
    cursor.execute(sql, ('05', '19', '2025-12-01'))
    cursor.execute(sql, ('05', '22', '2025-12-01'))
    cursor.execute(sql, ('05', '24', '2025-12-01'))
    cursor.execute(sql, ('05', '31', '2025-12-01'))
    cursor.execute(sql, ('05', '46', '2025-12-01'))
    cursor.execute(sql, ('05', '53', '2025-12-01'))
    cursor.execute(sql, ('05', '54', '2025-12-01'))
    cursor.execute(sql, ('06', '04', '2025-12-01'))
    cursor.execute(sql, ('06', '05', '2025-12-01'))
    cursor.execute(sql, ('06', '07', '2025-12-01'))
    cursor.execute(sql, ('06', '08', '2025-12-01'))
    cursor.execute(sql, ('06', '14', '2025-12-01'))
    cursor.execute(sql, ('06', '15', '2025-12-01'))
    cursor.execute(sql, ('06', '16', '2025-12-01'))
    cursor.execute(sql, ('06', '19', '2025-12-01'))
    cursor.execute(sql, ('06', '21', '2025-12-01'))
    cursor.execute(sql, ('06', '24', '2025-12-01'))
    cursor.execute(sql, ('06', '25', '2025-12-01'))
    cursor.execute(sql, ('06', '30', '2025-12-01'))
    cursor.execute(sql, ('06', '35', '2025-12-01'))
    cursor.execute(sql, ('06', '36', '2025-12-01'))
    cursor.execute(sql, ('06', '37', '2025-12-01'))
    cursor.execute(sql, ('06', '43', '2025-12-01'))
    cursor.execute(sql, ('06', '44', '2025-12-01'))
    cursor.execute(sql, ('06', '50', '2025-12-01'))
    cursor.execute(sql, ('06', '54', '2025-12-01'))
    cursor.execute(sql, ('06', '55', '2025-12-01'))
    cursor.execute(sql, ('06', '57', '2025-12-01'))
    db.commit()

    # insert web tag pair
    sql = "insert into web_tag values(%s, %s)"
    cursor.execute(sql, ('01', '13'))
    cursor.execute(sql, ('01', '43'))
    cursor.execute(sql, ('01', '50'))
    cursor.execute(sql, ('02', '13'))
    cursor.execute(sql, ('02', '45'))
    cursor.execute(sql, ('02', '49'))
    cursor.execute(sql, ('03', '13'))
    cursor.execute(sql, ('03', '14'))
    cursor.execute(sql, ('03', '43'))
    cursor.execute(sql, ('03', '50'))
    cursor.execute(sql, ('04', '13'))
    cursor.execute(sql, ('05', '13'))
    cursor.execute(sql, ('05', '43'))
    cursor.execute(sql, ('06', '13'))
    cursor.execute(sql, ('06', '43'))
    cursor.execute(sql, ('07', '06'))
    cursor.execute(sql, ('07', '14'))
    cursor.execute(sql, ('07', '18'))
    cursor.execute(sql, ('08', '06'))
    cursor.execute(sql, ('08', '14'))
    cursor.execute(sql, ('08', '16'))
    cursor.execute(sql, ('08', '18'))
    cursor.execute(sql, ('09', '18'))
    cursor.execute(sql, ('09', '51'))
    cursor.execute(sql, ('10', '18'))
    cursor.execute(sql, ('10', '53'))
    cursor.execute(sql, ('11', '18'))
    cursor.execute(sql, ('11', '48'))
    cursor.execute(sql, ('11', '53'))
    cursor.execute(sql, ('12', '18'))
    cursor.execute(sql, ('12', '53'))
    cursor.execute(sql, ('13', '18'))
    cursor.execute(sql, ('13', '43'))
    cursor.execute(sql, ('13', '50'))
    cursor.execute(sql, ('14', '18'))
    cursor.execute(sql, ('14', '48'))
    cursor.execute(sql, ('15', '18'))
    cursor.execute(sql, ('15', '44'))
    cursor.execute(sql, ('16', '13'))
    cursor.execute(sql, ('17', '13'))
    cursor.execute(sql, ('17', '45'))
    cursor.execute(sql, ('18', '13'))
    cursor.execute(sql, ('18', '47'))
    cursor.execute(sql, ('19', '13'))
    cursor.execute(sql, ('19', '46'))
    cursor.execute(sql, ('20', '14'))
    cursor.execute(sql, ('21', '14'))
    cursor.execute(sql, ('22', '14'))
    cursor.execute(sql, ('23', '14'))
    cursor.execute(sql, ('24', '14'))
    cursor.execute(sql, ('25', '14'))
    cursor.execute(sql, ('26', '15'))
    cursor.execute(sql, ('27', '15'))
    cursor.execute(sql, ('28', '15'))
    cursor.execute(sql, ('29', '16'))
    cursor.execute(sql, ('30', '16'))
    cursor.execute(sql, ('31', '16'))
    cursor.execute(sql, ('32', '13'))
    cursor.execute(sql, ('32', '46'))
    db.commit()

# create_table()
# insert_data()



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
            return render_template('index.html', images=['廣告_證券_投資理財.png', '廣告_旅平險_一般用戶.png', '廣告_保險_投資型保險.png'], state = '登入')
  
        try:
            # decoding the payload to fetch the stored details

            token = token.split(' ')[1]
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = data['account']
        except:
            return render_template('index.html', images=['廣告_證券_投資理財.png', '廣告_旅平險_一般用戶.png', '廣告_保險_投資型保險.png'], state = '登入')
        # returns the current logged in users contex to the routes
        return  f(current_user, *args, **kwargs)
  
    return decorated


@app.route("/", methods=['GET'])
@token_required
def home(user):
    print('user:', user)
    db = create_connection()
    cursor = db.cursor()
    calculate_recommendation(user)

    sql = "SELECT image_name FROM image \
    JOIN member_image ON image.image_id = member_image.image_id\
    JOIN member_prof ON member_prof.mbr_uid = member_image.mbr_uid\
    WHERE member_prof.account= %s ORDER BY member_image.score DESC LIMIT 3"
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
    #private_key = open('.ssh/id_rsa', 'r').read()
    access_token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
    
    cursor.execute("UPDATE member_prof SET access_token=%s WHERE account=%s",(access_token, account))
    db.commit()
    return jsonify({'token': access_token})

@app.route("/cardintro")
def card_intro():
    return render_template('product.html', category = '信用卡', items=[('cardintro1.png', '白金卡', '當月完成指定任務，次月享指定消費3.5%回饋無上限+跨行轉帳免手續費5次', 'card', '01', '19'), ('cardintro2.png', '悠遊聯名卡', '單月使用悠遊卡功能扣款搭乘捷運/公車滿20次，享NT$50元現金回饋', 'card', '02', '20'), ('cardintro3.png', '藍星世界卡', '消費直接累積「亞洲萬里通」里數，享最優NT$10累積1里數。生日當月最優NT$5累積1里數，累積哩程更快速！', 'card', '03', '21')])

@app.route("/investinsurance")
def invest_insurance():
    return render_template('product.html', category = '投資型保險', items=[('insurance1.png', '人生變額年金保險', '身故保證!附保證最低身故保險金機制之連結類全委帳戶保障。專家代操！與施羅德投信、富邦投信及富達投信合作，為您規劃投資組合配置', 'insurance', '07', '22'), ('insurance2.png', '人生外幣變額年金保險', '委託投資帳戶，每月領取撥回資產，資金運用更靈活', 'insurance', '08', '23'), ('insurance3.png', '變動型終身壽險', '繳費期間六年保障終身，繳費期滿後保額終身增值「利」抗通膨', 'insurance', '09', '24')])

@app.route("/medicalinsurance")
def medical_insurance():
    return render_template('product.html', category = '意外醫療險', items=[('意外醫療險_意外住院日額傷害保險.png', '意外住院日額傷害保險', '小保費大保障，CP值高。提供意外住院醫療保障', 'insurance', '10', '25'), ('意外醫療險_騎乘機車或自行車傷害保險.png', '騎乘機車或自行車傷害保險', '低保費建構高保障，最高200萬意外身故保障，可附加實支實付傷害醫療2萬保障，乘機車或自行車1.5倍給付', 'insurance', '11', '26'), ('意外醫療險_實支實付傷害醫療險.png', '實支實付傷害醫療險', '針對住院或門診期間的實際醫療費用，全盤考量自身病史、工作環境相關風險，減少高額醫療自費費用的負擔', 'insurance', '12', '27')])

@app.route("/otherinsurance")
def other_insurance():
    return render_template('product.html', category = '其他保險', items=[('其他保險_海外旅遊綜合險.png', '海外旅遊綜合險', '不論是身故、失能、傷害醫療、海外突發疾病、個人責任險、旅行不便險及海外急難救助，皆完整提供', 'insurance', '13', '28'), ('其他保險_機車強制險.png', '機車強制險', '不需依車主的性別、年齡及肇事紀錄核定保費，僅須詳實填寫要保書', 'insurance', '14', '29'), ('其他保險_寵物險.png', '寵物險', '門診、住院、手術費用最高給付 80%', 'insurance', '15', '30')])


@app.route("/carddiscount")
def card_discount():
    return render_template('product_unbuyable.html', category='刷卡優惠', items = [('刷卡優惠_VIP旅遊.png', 'VIP 旅遊優惠', '', '05'), ('刷卡優惠_旅遊.png', '旅遊優惠', '', '06'), ('刷卡優惠_雙十一蝦皮.png', '蝦皮雙十一刷卡優惠', '', '19'), ('刷卡優惠_雙十一momo.png', 'momo 雙十一刷卡優惠', '', '32'), ('刷卡優惠_超市.png', '生鮮超市刷卡優惠', '', '18'), ('刷卡優惠_行動支付.png', '行動支付刷卡優惠', '', '17'), ('刷卡優惠_3C.png', '3C 商品刷卡優惠', '', '04'), ('刷卡優惠_百貨.png', '百貨刷卡優惠', '', '16')])

@app.route("/Taiwanstock")
def Taiwanstock():
    return render_template('product_unbuyable.html', category='台股介紹', items = [('台股_元大台灣 50.png', '元大台灣', '', '20'), ('台股_台積電.png', '台積電', '', '21'), ('台股_聯發科.png', '聯發科', '', '22')])

@app.route("/USstock")
def USstock():
    return render_template('product_unbuyable.html', category='美股介紹', items = [('美股_IBM.png', 'IBM', '', '23'), ('美股_AAPL.png', 'APPLE', '', '24'), ('美股_GOOGL.png', 'GOOGLE', '', '25')])

@app.route("/fund")
def fund():
    return render_template('product_unbuyable.html', category='基金介紹', items = [('基金_台灣高股息基金.png', '台灣高股息基金', '', '26'), ('基金_貝萊德世界科技基金.png', '貝萊德世界科技基金', '', '27'), ('基金_那斯達克 100 指數股票型基金.png', '那斯達克 100 指數股票型基金', '', '28')])

@app.route("/foreignexchange")
def foreignexchange():
    return render_template('product_unbuyable.html', category='外匯介紹', items = [('匯率_美元.png', '美元', '', '29'), ('匯率_日圓.png', '日圓', '', '30'), ('匯率_人民幣.png', '人民幣', '', '31')])

def token_required_normal(f):
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
            return render_template('account.html', image='account_normal.png', item=['normal', 'account', '54'])  
        try:
            # decoding the payload to fetch the stored details
            token = token.split(' ')[1]
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = data['account']
        except:
            return render_template('account.html', image='account_normal.png', item=['normal', 'account', '54'])
        # returns the current logged in users contex to the routes
        return  f(current_user, *args, **kwargs)
  
    return decorated

def token_required_foreign(f):
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
            return render_template('account.html', image='account_foreign.png', item=['foreign', 'account', '55'])  
        try:
            # decoding the payload to fetch the stored details
            token = token.split(' ')[1]
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = data['account']
        except:
            return render_template('account.html', image='account_foreign.png', item=['foreign', 'account', '55'])
        # returns the current logged in users contex to the routes
        return  f(current_user, *args, **kwargs)
  
    return decorated

def token_required_digital(f):
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
            return render_template('account.html', image='account_digital.png', item=['digital', 'account', '56'])  
        try:
            # decoding the payload to fetch the stored details
            token = token.split(' ')[1]
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = data['account']
        except:
            return render_template('account.html', image='account_digital.png', item=['digital', 'account', '56'])
        # returns the current logged in users contex to the routes
        return  f(current_user, *args, **kwargs)
  
    return decorated

def token_required_security(f):
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
            return render_template('account.html', image='account_security.png', item=['securities', 'account', '57'])
        try:
            # decoding the payload to fetch the stored details
            token = token.split(' ')[1]
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = data['account']
        except:
            return render_template('account.html', image='account_security.png', item=['securities', 'account', '57'])
        # returns the current logged in users contex to the routes
        return  f(current_user, *args, **kwargs)
  
    return decorated

@app.route("/normalaccount")
@token_required_normal
def normal_account(user):
    db = create_connection()
    cursor = db.cursor()
    cursor.execute("SELECT amount FROM member_account JOIN member_prof ON member_account.mbr_uid = member_prof.mbr_uid WHERE account=%s AND account_type=%s", (user, 'normal'))
    amount = cursor.fetchall()
    return render_template('account_login.html', category='一般', amount=amount[0][0], image=f'{user}.png')

@app.route("/foreignaccount")
@token_required_foreign
def foreign_account(user):
    db = create_connection()
    cursor = db.cursor()
    cursor.execute("SELECT amount FROM member_account JOIN member_prof ON member_account.mbr_uid = member_prof.mbr_uid WHERE account=%s AND account_type=%s", (user, 'foreign'))
    amount = cursor.fetchall()
    if len(amount)==0:
        return render_template('account.html', image='account_foreign.png', item=['foreign', 'account', '55'])
    return render_template('account_login.html', category='外匯', amount=amount[0][0], image=f'{user}.png')

@app.route("/digitalaccount")
@token_required_digital
def digital_account(user):
    db = create_connection()
    cursor = db.cursor()
    cursor.execute("SELECT amount FROM member_account JOIN member_prof ON member_account.mbr_uid = member_prof.mbr_uid WHERE account=%s AND account_type=%s", (user, 'digital'))
    amount = cursor.fetchall()
    if len(amount)==0:
        return render_template('account.html', image='account_digital.png', item=['digital', 'account', '56'])
    return render_template('account_login.html', category='數位', amount=amount[0][0], image=f'{user}.png')

@app.route("/securityaccount")
@token_required_security
def security_account(user):
    db = create_connection()
    cursor = db.cursor()
    cursor.execute("SELECT amount FROM member_account JOIN member_prof ON member_account.mbr_uid = member_prof.mbr_uid WHERE account=%s AND account_type=%s", (user, 'securities'))
    amount = cursor.fetchall()
    if len(amount)==0:
        return render_template('account.html', image='account_security.png', item=['securities', 'account', '57'])
    return render_template('account_login.html', category='證券', amount=amount[0][0], image=f'{user}.png')

@app.route("/manageApply", methods=['POST'])
@token_required
def manage_apply(user):
    db = create_connection()
    cursor = db.cursor()

    item = request.get_json()['item']
    category = request.get_json()['category']
    tag = request.get_json()['tag']

    if category == 'investment':
        return jsonify({'status': 'success'})
    print(item, category, user, tag)

    cursor.execute("SELECT * FROM %s JOIN member_prof ON member_prof.mbr_uid = %s.mbr_uid \
    WHERE %s= '%s' AND account='%s'"%(f'member_{category}', f'member_{category}', f'{category}_type', item, user))
    if len(cursor.fetchall()) != 0:
        return jsonify({'status': '申辦失敗，已持有本商品'})
    
    # insert products
    cursor.execute("SELECT mbr_uid FROM member_prof WHERE account =%s", (user))
    uid = cursor.fetchall()[0][0]
    if category != 'account':
        cursor.execute("INSERT INTO %s VALUES ('%s', '%s', '%s', '%s', 'active')"%(f'member_{category}', uid, item, datetime.today().strftime('%Y-%m-%d'), '2028-01-01'))
    else:
        cursor.execute("INSERT INTO %s VALUES ('%s', '%s', 0, '%s', 'active')"%(f'member_{category}', uid, item, datetime.today().strftime('%Y-%m-%d')))
    db.commit()
    
    # insert newly acquired products tag
    cursor.execute("INSERT INTO tag_result VALUES (%s, %s, '2025-12-01')", (uid, tag))
    db.commit()

    return jsonify({'status': '申辦成功'})

@app.route("/interestTag", methods=['POST'])
@token_required
def interestTag(user):
    db = create_connection()
    cursor = db.cursor()

    web_id = request.get_json()['web_id']
    print(user, web_id)
    # get mbr_uid
    cursor.execute("SELECT mbr_uid FROM member_prof WHERE account =%s", (user))
    uid = cursor.fetchall()[0][0]
    
    cursor.execute("INSERT INTO web_events VALUES (%s, %s, %s)", (uid, web_id, datetime.now().strftime('%Y/%m/%d %H:%M:%S')))
    db.commit()
    update_tag_result_click(uid, web_id)
    return render_template("index.html")

def update_tag_result_click(mbr_uid, web_id):
    # 新增網站點擊事件 web_events 及其對應的 tag_result
    db = create_connection()
    cursor = db.cursor()

    cursor.execute('SELECT COUNT(%s) FROM web_events GROUP BY %s', (web_id, mbr_uid))
    if cursor.fetchall()[0][0] >= 3:
        cursor.execute("SELECT tag_id FROM web_tag WHERE web_id=%s", (web_id))
        tag_ids = [x[0] for x in cursor.fetchall()]
        print(tag_ids)
        for tag_id in tag_ids:
            cursor.execute('SELECT * FROM tag_result WHERE mbr_uid=%s AND tag_id=%s', (mbr_uid, tag_id))
            if len(cursor.fetchall()) == 0:
                cursor.execute("INSERT INTO tag_result VALUES (%s, %s, '2025-12-01')", (mbr_uid, tag_id))
            db.commit()

def calculate_recommendation(user):
    db = create_connection()
    cursor = db.cursor()

    # get mbr_uid
    cursor.execute("SELECT mbr_uid FROM member_prof WHERE account =%s", (user))
    mbr_uid = cursor.fetchall()[0][0]
    
    # get user's tag list from tag_result
    cursor.execute("SELECT tag_id FROM tag_result WHERE mbr_uid=%s", (mbr_uid))
    tags = [x[0] for x in cursor.fetchall()]

    # 判斷 image 的 proh_tag 是否符合 the user's tag list 的條件
    cursor.execute("SELECT image.image_id, tag_id, proh_tag, details FROM image LEFT OUTER JOIN image_filter ON\
    image.image_id = image_filter.image_id")
    image_all = cursor.fetchall()
    update_array = []
    for image in image_all:
        tags2 =  [i.strip() for i in image[1].split(',')]
        score = len(set(tags).intersection(set(tags2)))/len(set(tags).union(set(tags2)))
        if image[3] == '有的會被排除' and image[2] in tags:
            score = -1
        elif image[3] == '沒有的會被排除' and image[2] not in tags:
            score = -1
        

        # update array empty
        if len(update_array)==0:
            update_array.append((mbr_uid, image[0], score))

        # next image different from last one
        elif update_array[-1][1] != image[0]:
            update_array.append((mbr_uid, image[0], score))

        # next image the same as last one
        else:
            #  next image != -1 => no need to update
            if score != -1:
                pass

            # next image == -1 => update
            else:
                del update_array[-1]
                update_array.append((mbr_uid, image[0], score))

        
    cursor.executemany("INSERT INTO member_image VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE score=VALUES(score)", update_array)
    db.commit()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

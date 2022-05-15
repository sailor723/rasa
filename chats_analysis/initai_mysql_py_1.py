from datetime import datetime
from numpy.core.defchararray import index
import pandas as pd
import numpy as np
import sqlalchemy
import mysql.connector
from sqlalchemy import create_engine
from sqlalchemy.dialects.mysql import insert

# create mysql
# 初始化数据库连接，使用pymysql模块
# MySQL的用户：weiping, 密码:, 端口：3306,数据库：medicaldevice

engine = create_engine('mysql+pymysql://weiping:@localhost:3306/test_db')

redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

df.to_sql('Whole_geo', engine, if_exists='replace',index=False)
# df.loc[0].to_sql('Whole_geo', engine, if_exists='replace',index=False,index_label=id)


df = pd.read_csv('t_remind.csv',header=0)
df.drop([0],axis=0)
df.to_sql('t_remind', engine, if_exists='replace',index=False)
# df[df['运单号'] != 'INITIALPOST'].to_sql('Carrier', engine, if_exists='replace',index=False)

# df = pd.read_excel('./器械模拟20210623 - 副本.xls',sheet_name='Geo')


# Creat Primary Key

db = mysql.connector.connect(
    host="localhost",
    user='weiping',
    passwd='',
    auth_plugin='mysql_native_password',
)

mycursor = db.cursor()

mycursor.execute("USE medicaldevice;")
mycursor.execute("ALTER TABLE Whole_geo ADD COLUMN id INT AUTO_INCREMENT PRIMARY KEY")
db.commit()

mycursor.execute("ALTER TABLE Carrier ADD COLUMN id INT AUTO_INCREMENT PRIMARY KEY")
db.commit()

# mycursor.execute("ALTER TABLE Geo ADD COLUMN id INT AUTO_INCREMENT PRIMARY KEY")
# db.commit()



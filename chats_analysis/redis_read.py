# extract redis, write to mysql and flushall redis, need to make sure mysql tracker value is longtext format

from matplotlib.font_manager import json_dump
import redis, json, os
import pandas as pd 
from sqlalchemy import create_engine
import pymysql

DCTA_MYSQL_USER = os.getenv('DCTA_MYSQL_USER')
DCTA_MYSQL_PWD = os.getenv('DCTA_MYSQL_PWD')
DCTA_MYSQL_HOST = os.getenv('DCTA_MYSQL_HOST')
DCTA_MYSQL_PORT  = int(os.getenv('DCTA_MYSQL_PORT'))
DCTA_MYSQL_DB  = os.getenv('DCTA_MYSQL_DB')
DCTA_MYSQL_TABLE  = os.getenv('DCTA_MYSQL_TABLE')
# print('DCTA_MYSQL_USER:', DCTA_MYSQL_USER)
# print('DCTA_MYSQL_PWD:', DCTA_MYSQL_PWD)
# print('DCTA_MYSQL_HOST:', DCTA_MYSQL_HOST)
# print('DCTA_MYSQL_DB:', DCTA_MYSQL_DB)
# print('DCTA_MYSQL_PORT:', DCTA_MYSQL_PORT)
# print('DCTA_MYSQL_TABLE:', DCTA_MYSQL_TABLE)


DCTA_REDIS_HOST = os.getenv('DCTA_REDIS_HOST')
DCTA_REDIS_PORT= int(os.getenv('DCTA_REDIS_PORT'))
DCTA_REDIS_USER = os.getenv('DCTA_REDIS_USER')
DCTA_REDIS_PWD = os.getenv('DCTA_REDIS_PWD')

#连接数据库
conn=pymysql.connect(
    host=DCTA_MYSQL_HOST,
    port=DCTA_MYSQL_PORT,
    user=DCTA_MYSQL_USER,
    password=DCTA_MYSQL_PWD,
    database=DCTA_MYSQL_DB
)

# conn=pymysql.connect(
#     host="127.0.0.1",
#     port=3306,
#     user="root",
#     password="Ecc!123456",
#     database="test_db"
# )


cursor=conn.cursor()

redis_client = redis.Redis(host=DCTA_REDIS_HOST, password=DCTA_REDIS_PWD, port=DCTA_REDIS_PORT, db=0)

# 取前缀为tracker的Key
for redis_key in redis_client.scan_iter("tracker*"):
      
      try:

        data = json.loads(redis_client.get(redis_key))

        data_json = json.dumps(data)

        # 执行sql语句
        sql = 'insert into tracker(tracker_id, value) values(%s, %s)'

        values = (redis_key, data_json)
        cursor.execute(sql, values)

        # 删除key
        redis_client.delete(redis_key)
      except:
        print('Waring Json load, redis_key is', redis_key)
        continue

# 提交之前的操作，如果之前已经执行多次的execute，那么就都进行提交
conn.commit()

# 关闭cursor对象
cursor.close()

# 关闭connection对象
conn.close
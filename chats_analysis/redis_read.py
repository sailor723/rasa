# extract redis, write to mysql and flushall redis, need to make sure mysql tracker value is longtext format

from matplotlib.font_manager import json_dump
import redis, json
import pandas as pd 
from sqlalchemy import create_engine
import pymysql

#连接数据库
conn=pymysql.connect(
    host="127.0.0.1",
    port=3306,
    user="root",
    password="Ecc!123456",
    database="test_db"
)

cursor=conn.cursor()

redis_client = redis.Redis(host='localhost', password='ecc#123456', port=6379, db=0)

# 取前缀为tracker的Key
for redis_key in redis_client.scan_iter("tracker*"):

  data = json.loads(redis_client.get(redis_key))

  data_json = json.dumps(data)

  # 执行sql语句
  sql = 'insert into tracker(tracker_id, value) values(%s, %s)'

  values = (redis_key, data_json)
  cursor.execute(sql, values)

  # 删除key
  redis_client.delete(redis_key)

# 提交之前的操作，如果之前已经执行多次的execute，那么就都进行提交
conn.commit()

# 关闭cursor对象
cursor.close()

# 关闭connection对象
conn.close
# extract redis, write to mysql and flushall redis, need to make sure mysql tracker value is longtext format

import redis, json, os
from sqlalchemy import create_engine
import pymysql

DCTA_MYSQL_USER = os.getenv('DCTA_MYSQL_USER')
DCTA_MYSQL_PWD = os.getenv('DCTA_MYSQL_PWD')
DCTA_MYSQL_HOST = os.getenv('DCTA_MYSQL_HOST')
DCTA_MYSQL_PORT  = int(os.getenv('DCTA_MYSQL_PORT'))
DCTA_MYSQL_DB  = os.getenv('DCTA_MYSQL_DB')
DCTA_MYSQL_TABLE  = os.getenv('DCTA_MYSQL_TABLE')


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


try:
    tablename = 'tracker'

    with conn.cursor() as cur:
        cur.execute("TRUNCATE TABLE %s" % tablename)
    conn.commit()
    conn.close()
    print('MySql Delete Done')
except:
    print('MySql Delete Failed!')


redis_client = redis.Redis(host=DCTA_REDIS_HOST, password=DCTA_REDIS_PWD, port=DCTA_REDIS_PORT, db=0)

try:
    redis_client.flushall
    print('Redis Flushall Done')
except:
    print('Redis Flushall error')


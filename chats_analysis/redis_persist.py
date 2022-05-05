import redis, json, os
import pandas as pd 
from sqlalchemy import create_engine

if __name__ == '__main__':

    engine = create_engine('mysql+pymysql://weiping:@localhost:3306/test_db')

    redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

    redis_client.keys()
    
    redis_output_name = os.path.abspath('redis_output.xlsx')

    for redis_key in redis_client.scan_iter("tracker*"):
      
        data = json.loads(redis_client.get(redis_key))

        df = pd.DataFrame(data['events']) 

        df.to_excel(redis_output_name)

        df = pd.read_excel(redis_output_name)

        df.to_sql('tracker1', engine, if_exists='append',index=False)

        redis_client.delete( redis_key)


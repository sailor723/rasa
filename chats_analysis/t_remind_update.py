import pandas as pd
from sqlalchemy import create_engine
engine = create_engine('mysql+pymysql://weiping:@localhost:3306/test_db')

df = pd.read_sql('t_remind',engine)
df = df.drop([0])

df.user_id == 'Andy'
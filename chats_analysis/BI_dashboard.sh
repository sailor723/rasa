python redis_read.py 
python chats_log_generator.py
python chats_df_generator.py
kill -9 $(lsof -t -i:8501)
streamlit run BI_dashboard.py 
# streamlit run BI_dashboard.py --server.port 8501 > bi.log 2>&1 &

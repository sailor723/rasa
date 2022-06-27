#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# --------------------------------------------------------web服务 start------------------------------------------------#
#Flask ⼀个轻量级的web框架 
import re
import flask, json                          
from flask_cors import *
# import streamlit as st


 # __name__代表当前的python⽂件,把当前的python⽂件当做⼀个服务启动
server = flask.Flask(__name__)     
# 解决跨域
CORS(server, supports_credentials=True)     

@server.route('/login')
def login():

  # 获取前端传递过来的参数
  user = flask.request.values.to_dict()  


  print(user)
#   st.write(user)
  
  return 'success'
# --------------------------------------------------------web服务 end------------------------------------------------#    


# print('total conversation:', df_final.shape[0])

if __name__ =='__main__':
    # port可以指定端⼝，默认端⼝是5000,host默认是服务器，默认是127.0.0.1,debug=True 修改时不关闭服务
    server.run(debug=True,host='172.16.11.59')

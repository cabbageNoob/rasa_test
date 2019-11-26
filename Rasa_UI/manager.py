#!/usr/bin/python
# -*- coding: UTF-8 -*-
#忽略warning警告
import warnings
warnings.filterwarnings("ignore")
import sys
from flask import Flask,render_template,redirect,request
import json
sys.path.append(r'..\rasa_chatbot_cn')
import os

os.chdir(r"..\rasa_chatbot_cn")
import bot
app=Flask(__name__)
agent = bot.Load_model()
os.chdir("..\Rasa_UI")

# 下面开始对于前台的请求做路由控制
@app.route('/',methods=["GET", "POST"])
def index(request="你好"):
    print("handler：", request)
    print("os.getcwd():",os.getcwd())
    return render_template("chat.html",request=request)

import asyncio
@app.route('/api/user',methods=["GET", "POST"])
def user():
    global agent
    response=dict()
    input_text=request.form["input_text"]
    print("input_text: "+request.form["input_text"])
    # result=bot.get_ans(agent,input_text)
    if agent.is_ready():
        # loop = asyncio.get_event_loop()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(bot.get_res(agent, input_text))

    if result is not None:
        print(result)
        res=[]
        for i in range(len(result)):
            res.append(result[i]['text'])
        print(res)
        response['response']=res
        return json.dumps(response)



if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8001)
<!--
 * @Descripttion: 
 * @version: 
 * @Author: cjh (492795090@qq.com)
 * @Date: 2019-12-14 21:56:21
 * @LastEditors: cjh (492795090@qq.com)
 * @LastEditTime: 2019-12-17 12:31:20
 -->

# 根据最新版rasa构建聊天机器人
## 直接rasa shell时并不能启动actions服务
```
rasa run actions --actions actions
```
### 解决办法
先启动actions服务
```
python -m rasa_sdk --actions actions
```
再调用
```
rasa shell --endpoints configs/endpoints.yml
```
## Start rasa server
```
rasa run -m models --enable-api --log-file out.log
rasa run -m models --enable-api --cors "*" --endpoints configs/endpoints.yml -debug
```
## Online Learning
```
rasa interactive -m models --data data --endpoints configs/endpoints.yml
```
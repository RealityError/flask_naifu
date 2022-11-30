#初始化数据库
#判断文件是否存在
import os
if os.path.exists("database/users.db"):
    os.remove("database/users.db")

#创建数据库
import sqlite3
connect = sqlite3.connect("database/users.db")
connect.close()

# SQLAlchemy操作
from main import db,user,user_pic


#导入初始化json
import json
with open("init.json") as json_file:
	data = json.load(json_file)

#获取QQ信息
import requests
import base64
def get_qqinfo(qq):
    url_name = "http://api.usuuu.com/qq/" + str(qq)
    data = json.loads(requests.get(url_name).text)
    base64_data = requests.get(data["data"]["avatar"]).content
    name = data["data"]["name"]
    return base64_data,name




from main import app
with app.app_context():
# 会删除所有继承db.Model的表
    db.drop_all()
# 会创建所有继承自db.Model的表,会丢失数据库表中所有的数据
    db.create_all()

# 初始化数据
#初始化用户信息，可以在json中填写你自己的信息
# """
# 用户信息表,用来存储用户的一些信息
# 用户QQ
# 用户密码
# 用户剩余图片额度
# 用户生成了多少图片
# """
    [pic,user_name] = get_qqinfo(data["QQ"])
    user_master = user(
    user_id=1,
    qq = int(data["QQ"]),
    password = data["password"],
    picture_num = -1,
    pictured_num=0,
    user_name = user_name,
    user_pic = pic
    )

# """
# 用户生成图片信息表,用来存储用户生成图片的信息
# 用户QQ
# 用户生成图片的hash
# 图片大小
# 生成时间
# """
#仅创建表格，不用初始化数据
    pic = user_pic()
# 提交并存储
    db.session.add_all([user_master,pic])
    db.session.commit()


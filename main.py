import base64
from datetime import timedelta
from flask import Flask, render_template, Response, make_response, request, session ,redirect,url_for,flash,get_flashed_messages
import time
import requests


#导入初始化json
import json
with open("init.json") as json_file:
	data = json.load(json_file)
 
 
#初始化webui类
from draw_webui import webui_
from flask_sqlalchemy import SQLAlchemy

#设置日志
import logging
from logging.handlers import TimedRotatingFileHandler
def setup_log():
    # 定义日志输出格式
    fmt_str = '%(asctime)s[level-%(levelname)s][%(name)s]:%(message)s'
    logging.basicConfig(level=logging.INFO)
    # when可设置月、日、时、分、秒等; interval: n个when更新一次; backupCount: 保留m个文件
    files_handle = TimedRotatingFileHandler("log/server.log", when='D', interval=5)  # when S M H D midnight
    # 注意时间的格式，区别 - 和 _ , 格式不对影响日志的删除
    files_handle.suffix = "%Y-%m-%d_%H-%M-%S.txt"
    # 设置日志输出级别和格式
    # files_handle.setLevel(logging.DEBUG)
    formatter = logging.Formatter(fmt_str)
    files_handle.setFormatter(formatter)
    # 添加到日志处理对象集合
    logging.getLogger('').addHandler(files_handle)
 
setup_log()

import os
#获取当前文件夹路径
basedir= os.path.abspath(os.path.dirname(__file__))


#--------------------------flask初始化----------------------------------
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+ os.path.join(basedir,"database/users.db")
# 动态追踪修改设置，如未设置只会提示警告
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
# 使用SQLAlchemy操作数据库的时候可以在后台看到自动生成sql语句，以便于测试
app.config['SQLALCHEMY_ECHO'] = data["SEE_SQL"]
# 创建SQLAlchemy对象，该对象是操作数据库的对象
db = SQLAlchemy(app)

#设置session
app.config['SESSION_USE_SIGNER'] = True  # 是否强制加密，混淆session
app.secret_key  =  data["secret_key"]
app.config['SESSION_PERMANENT'] = False  # sessons是否长期有效，false，则关闭浏览器，session失效
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # session长期有效，则设定session生命周期，整数秒，默认大概不到3小时。

#----------------------------------------------------------------------


#--------------------------数据库对象表----------------------------------

# 用户登录表
#主表
class user(db.Model):
     # 指定模型类对应的表名(不指定就和模型类的类名一样)
    __tablename__ = "UserData"
    
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True,unique=True)
    
    qq = db.Column(db.Integer,unique=True)
    
    password = db.Column(db.String) 
    picture_num = db.Column(db.Integer)
    pictured_num = db.Column(db.Integer)
    user_name = db.Column(db.String)
    user_pic = db.Column(db.BLOB)
#用户图片信息表   
class user_pic(db.Model):
     # 指定模型类对应的表名(不指定就和模型类的类名一样)
    __tablename__ = "UserPic"
    
    pic_id = db.Column(db.Integer, primary_key=True,autoincrement=True,unique=True)
    
    user_id = db.Column(db.Integer)
    
    hash_pic = db.Column(db.String,unique=True)
    prompt = db.Column(db.String)
    Nprompt = db.Column(db.String)
    size_pic = db.Column(db.Float)
    
    
    
    
    
    
    
#----------------------------------------------------------------------

#--------------------------页面跳转逻辑----------------------------------
#根页面
@app.route('/',methods=['GET','POST'])
def root():
    ip = request.remote_addr
    logging.info("IP:"+str(ip)+"访问了网站")
    return render_template("login.html")

#登录页面
@app.route('/login',methods=['GET','POST'])
def start():
    ip = request.remote_addr
    
    
    if request.method == "GET":
        logging.info("IP:"+str(ip)+"访问了网站")
        return render_template("login.html")
    
    elif request.method =='POST':
        
        #获取一些基本的信息  
        qq = request.form.get('QQ_login')
        password =  request.form.get('password_login')
        
        
        #数据库查表
        user_info = user.query.filter_by(qq=qq).first()
        #输出一下尝试登录的信息
        logging.info("IP:"+str(ip)+"的用户(QQ:"+str(request.form.get('QQ_login'))+")登录网站")
        if (qq is None) or (password is None):
            return render_template('login.html', msg="账户或密码不能为空")
        if user_info is None:
            logging.info("IP:"+str(ip)+"的用户登录网站(error_qq)")
            return render_template('login.html', msg="没有该用户")
        
        else:
                        
            if (user_info.password != password) and (user_info.password is not None):
                return render_template('login.html', msg="密码错误")
            
            elif user_info.password == "":
                usee_reg = user.query.filter_by(qq=qq).first()
                usee_reg.password = password
                db.session.commit()
                session['qq'] = str(qq)
                logging.info("IP:"+str(ip)+"的用户(QQ:"+str(request.form.get('QQ_login'))+")登录网站(REG_IN)")
                return redirect("/index")
            else:
                session['qq'] = str(qq)
                logging.info("IP:"+str(ip)+"的用户(QQ:"+str(request.form.get('QQ_login'))+")登录网站(IN)")
                return redirect("/index")

        
        
    return render_template("login.html")

# 注册服务
@app.route('/reg')
def reg():
    if data["reg_switch"] == "OFF":
        return render_template("404.html",msg="已关闭注册")
    else:
        return render_template("reg.html")
#欢迎页
@app.route('/welcome')
def welcome():
    return render_template("welcome.html")

#主页面
@app.route('/index')
def index():
    qq=session.get('qq')
    user_info = user.query.filter_by(qq=qq).first()
    
    
    if qq is None:
        return render_template("login.html",msg = "你干什么？该IP已被记录")
    return render_template(
        "index.html",
        info = str(requests.get("https://v1.hitokoto.cn/?c=f&encode=text").text),       
        name =   user_info.user_name,
        pic64 =  base64.b64encode(user_info.user_pic).decode('utf-8')    
                        )
#naifu端


# 重定向到自建的聊天室
@app.route('/chat')
def chat():
    if data["char_url"] == "":
        return render_template("404.html",msg="未开启聊天室")   
    return redirect(data["char_url"],code=301)
#----------------------------------------------------------------------


#--------------------------登录逻辑----------------------------------










#----------------------------------------------------------------------




#--------------------------图片生成----------------------------------



#绘画网页
@app.route('/naifu')
def naifu():
    return render_template("naifu.html")

#生成
@app.route('/generate-stream',methods=['POST'])
def generate():
    #验证用户的登录状态
    qq=session.get('qq')
    ip = request.remote_addr
    

  
    if request.method == "POST":
        response = Response()       
        img_data = json.loads(request.get_data(as_text=True))
        #初始化数据
        imgdata = webui_(img_data,data)    
        #获取数据
        imgdata.generate(response,data)
        
        return response
    else:
        pass
    
    

#----------------------------------------------------------------------
if __name__ == '__main__':
    
    app.run(debug = True, port = 11451,host="0.0.0.0",threaded=True)
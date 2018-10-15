from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
#from flask_migrate import Migrate
from flask_moment import Moment

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
#migrate = Migrate(app, db)

moment = Moment(app)

#用户认证
login_manger = LoginManager()

#配置用户认证信息
login_manger.init_app(app)
#认证加密程度
login_manger.session_protection = 'strong'
#登陆认证的处理视图
login_manger.login_view = 'loginModule.login'
#登陆提示信息
login_manger.login_message = '请先登录！'
login_manger.login_message_category = 'info'


@login_manger.user_loader  #应置于models.py 文件中
def load_user(userid):
    from models import User
    return User.query.get(userid)


from album import login, views

# set FLASK_APP=manager.py
# flask shell
# from album import db
# db.create_all()

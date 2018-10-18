import os
import uuid
from album import app
from flask_mail import Mail, Message
from itsdangerous import  TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired, BadSignature
from flask import  render_template,flash
from threading import Thread
from flask  import  current_app

def rename_image(old_filename):
    """yapf-pycharm重命名上传图片文件名"""
    ext = os.path.splitext(old_filename)[1]
    new_filename = uuid.uuid4().hex + ext
    return new_filename


def get_filenamewithoutext(filename):
    """去除上传文件的扩展名"""
    filename = os.path.splitext(filename)[0]
    return filename

def send_async_mail(app2,message):
     with app2.app_context():
         mail = Mail(app2)
         mail.send(message)

def set_mail(user):
    s = Serializer(app.config['SECRET_KEY'], 300)
    data = {'email': user.email}
    data.update({'id': user.name})
    token = s.dumps(data)
    mail = Mail()
    mail.init_app(app)
    msg = Message('重置密码', sender=('图片秀','acf@gzjs.gov.cn'), recipients=[user.email])
    #msg.body = render_template('reset_password.txt',token = token, email=email )
    msg.html = render_template('reset_password.html',token = token, name=user.name )
    app2 = current_app._get_current_object()

    #mail.send(msg)

    th = Thread(target= send_async_mail, args= [app2,msg])
    th.start()
    # 使用JWT.io（https://jwt.io ）提供的调试工具
    # https://ninghao.net/blog/2834
    # time.sleep(2)
    # s1 = Serializer(app.config['SECRET_KEY'])
    # data1 = s1.loads(ss)

    return "邮件已发送，5分钟内有效；"

def verify_code(token,  new_password=None):
    s = Serializer(app.config['SECRET_KEY'])
    try:
        data = s.loads(token)
        email = data.get('email')

    except (SignatureExpired, BadSignature):
        flash('验证码过期或签名无效，密码更新失败！')
        return False
    return True
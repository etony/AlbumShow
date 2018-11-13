import os
import uuid
from album import app, db
from flask_mail import Mail, Message
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired, BadSignature
from flask import render_template, flash, redirect, url_for
from threading import Thread
from flask import current_app
from wtforms import ValidationError
import re
from models import User
from PIL import Image


def rename_image(old_filename):
    """yapf-pycharm重命名上传图片文件名"""
    ext = os.path.splitext(old_filename)[1]
    new_filename = uuid.uuid4().hex + ext
    return new_filename


def get_filenamewithoutext(filename):
    """去除上传文件的扩展名"""
    filename = os.path.splitext(filename)[0]
    return filename


def send_async_mail(app2, message):
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
    msg = Message(
        '重置密码', sender=('图片秀', 'acf@gzjs.gov.cn'), recipients=[user.email])
    #msg.body = render_template('reset_password.txt',token = token, email=email )
    msg.html = render_template(
        'reset_password.html', token=token, name=user.name)
    app2 = current_app._get_current_object()

    #mail.send(msg)

    th = Thread(target=send_async_mail, args=[app2, msg])
    th.start()
    # 使用JWT.io（https://jwt.io ）提供的调试工具
    # https://ninghao.net/blog/2834
    # time.sleep(2)
    # s1 = Serializer(app.config['SECRET_KEY'])
    # data1 = s1.loads(ss)

    return "邮件已发送，5分钟内有效；"


def verify_code(token, new_password=None):
    s = Serializer(app.config['SECRET_KEY'])
    try:
        data = s.loads(token)
        email = data.get('email')
        user = User.query.filter_by(email=email).first()
        if user is not None:
            user.set_password(new_password)
            user.active = 1
            user.confirmed = 1
            user.locked = 0
            db.session.commit()
            flash('密码已更新！')
            return redirect(url_for('loginModule.login'))
    except SignatureExpired:
        #except (SignatureExpired, BadSignature) as e:
        flash('验证码过期！')
        return redirect(url_for('loginModule.login'))
    except BadSignature:
        flash('签名验证失败！')
        return redirect(url_for('loginModule.login'))
    return True


def verify_password(password):
    if len(password) < 8:
        raise ValidationError('密码长度不足.')
    if password == password.upper() or password == password.lower():
        raise ValidationError('必须同时包含大小写字母！')
    if not re.compile('([^a-z0-9A-Z])+').findall(password):
        raise ValidationError('密码应包含符号.')
    if not re.compile('[0-9]+').findall(password):
        raise ValidationError('密码应包含数字.')


def verify_picture(user):
    path = os.path.join(app.root_path, 'static')
    filename = os.path.join(path, user.picture)
    filename_s = os.path.join(path, user.picture_s)
    if not os.path.exists(filename):
        user.picture = 'images/timg.jpg'
    if not os.path.exists(filename_s):
        user.picture_s = 'images/user.jpg'
    return user

def verify_picture_size(photofile):
    img = Image.open(photofile)
    if img.size[0]< app.config['UPLOADED_PHOTO_MIN'] or img.size[1]< app.config['UPLOADED_PHOTO_MIN']:
        flash('上传图片分辨率不足！')
        img.close()
        os.remove(photofile)
        return False
    return True

def photo_crop(photofile, region, savepath):
    savepath = os.path.join(os.path.dirname(photofile))
    return True

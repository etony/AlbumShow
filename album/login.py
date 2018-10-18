from flask import Blueprint, render_template, request, flash, redirect, url_for
from forms.loginform import LoginForm, registerForm, resetForm, resetPassForm
from forms.userform import ChangePasswordForm, UploadPictureForm
from forms.uploadform import uploadForm
from forms.userform import userForm
from models import User, SysLog, Photo
from werkzeug import security
from werkzeug.utils import secure_filename
from album import db, app
from PIL import Image

from utils import rename_image, get_filenamewithoutext, set_mail
from forms.uploadform import photos
import os
from flask_login import login_user, logout_user, login_required, current_user, login_fresh, confirm_login
from wtforms import ValidationError
from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired, BadSignature

# loginModule = Blueprint('loginModule', __name__, static_folder='', static_url_path='')
loginModule = Blueprint('loginModule', __name__)


@loginModule.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('viewModule.vlist'))

    loginform = LoginForm()

    if loginform.validate_on_submit():
        email = loginform.email.data.lower()
        passwd = loginform.password.data
        #hash =security.generate_password_hash('12345678',method='pbkdf2:sha256',salt_length=8)

        user = User.query.filter_by(email=email).first()
        if user is not None:
            if security.check_password_hash(user.password_hash, passwd):
                if user.locked != 0:
                    flash('账号被锁定，请与管理员联系!')
                    return redirect(url_for('loginModule.login'))
                if user.active != 1:
                    flash('账号未激活，请激活后重新登录!')
                    return redirect(url_for('loginModule.login'))
                if user.confirmed != 1:
                    flash('账号未确认，请等待系统确认后重新登录!')
                    return redirect(url_for('loginModule.login'))
                login_user(user, loginform.remember_me.data)
                flash('登录成功！')

                log = SysLog(
                    userId=user.userid,
                    userName=email,
                    operContent=request.remote_addr + '登入')
                db.session.add(log)
                db.session.commit()
                return redirect(url_for('viewModule.vlist'))
            else:
                flash('密码错误！')
        else:
            flash('用户不存在！')
    return render_template('login.html', form=loginform)


@loginModule.route("/register", methods=['GET', 'POST'])
def register():
    registerform = registerForm()
    if request.method == 'POST':
        if registerform.validate_on_submit():
            name = registerform.name.data
            email = registerform.email.data
            username = registerform.username.data
            password = registerform.password.data
            user = User(
                name=name,
                userid=username,
                email=email,
                confirmed=0,
                locked=0,
                active=0)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash('注册成功,请登录！')
            return redirect(url_for('loginModule.login'))
        flash('注册失败！')
    return render_template('register.html', form=registerform)


@loginModule.route("/logout")
def logout():
    logout_user()
    flash('用户退出!')
    return redirect(url_for('loginModule.login'))


@loginModule.route("/reset/", methods=['GET', 'POST'])
def reset():
    resetform = resetForm()
    if request.method == 'POST':
        email = resetform.email.data
        user = User.query.filter_by(email=email).first()
        if user is not None:
            user.active = 0
            msg = set_mail(user)
            db.session.commit()
            flash(msg + '请登录注册邮箱，重新激活账号！')
        else:
            flash('邮箱不存在！')
    return render_template('reset.html', form=resetform)


@loginModule.route("/reset_password/<string:token>", methods=['GET', 'POST'])
def reset_password(token):
    resetpassform = resetPassForm()
    s = Serializer(app.config['SECRET_KEY'])

    try:
        data = s.loads(token)
        email = data.get('email')
        if resetpassform.validate_on_submit():
            password = resetpassform.password.data
            user = User.query.filter_by(email=email).first()
            user.set_password(password)
            if user.active == 1:
                flash('验证码失效，密码更新失败！')
                return redirect(url_for('loginModule.login'))
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

    return render_template('reset_pass.html', form=resetpassform)


@loginModule.route("/upload", methods=['GET', 'POST'])
@login_required
def upload():
    uploadform = uploadForm()
    # print('路径:' + app.root_path)
    # print('路径:' + app.config['UPLOADED_PHOTOS_DEST'])
    if uploadform.validate_on_submit():

        filename = uploadform.photo.data.filename
        savename = photos.save(
            uploadform.photo.data, name=rename_image(filename))
        pathname = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], savename)
        pathname_s = os.path.join(app.config['UPLOADED_PHOTOS_DEST'],
                                  's_' + savename)
        img = Image.open(pathname)
        img.thumbnail((200, 200))
        img.save(pathname_s)
        photo = Photo(
            filename=savename,
            filename_s='s_' + savename,
            description=get_filenamewithoutext(filename),
            author_id=current_user.userid)
        db.session.add(photo)
        db.session.commit()
        # if 'file' not in request.files:
        #     flash('未选择上传文件！')
        #     return render_template('upload.html', form = uploadform)
        # file = request.files['file']
        # filename =  rename_image(file.filename)
        # file.save(os.path.join('upload', filename))
        flash('文件上传成功！')
        #f.save(os.path.join('upload', filename))
        # filename_s = resize_image(f, filename, current_app.config['ALBUMY_PHOTO_SIZE']['small'])
        # filename_m = resize_image(f, filename, current_app.config['ALBUMY_PHOTO_SIZE']['medium'])
        # photo = Photo(
        #     filename=filename,
        #     filename_s=filename_s,
        #     filename_m=filename_m,
        #     author=current_user._get_current_object()
        # )
        # db.session.add(photo)
        # db.session.commit()

        # https://blog.csdn.net/pzl_pzl/article/details/80861231
    myphotos = Photo.query.filter_by(author_id=current_user.userid)
    return render_template('upload.html', form=uploadform, myphotos=myphotos)


@loginModule.route("/user")
def modify_user():
    userform = userForm()
    return render_template('user.html', form=userform)


@loginModule.route("/settings/", methods=['GET', 'POST'])
def settings():

    userform = ChangePasswordForm()
    email = current_user.email
    user = User.query.filter_by(email=email).first()
    if request.method == 'POST':
        if userform.validate_on_submit():
            if security.check_password_hash(user.password_hash,
                                            userform.old_password.data):
                user.set_password(userform.password.data)
                flash('密码修改成功！')
                return redirect(url_for('loginModule.settings'))
            flash('原密码不匹配！')

        flash('密码修改失败')
    return render_template('settings.html', form=userform)


@loginModule.route("/settings/picture/", methods=['GET', 'POST'])
def settings_picture():
    userform = UploadPictureForm()
    if request.method == 'POST':
        if userform.validate_on_submit():
            file = request.files['image']
            filename = rename_image(file.filename)
            picture = os.path.join(app.config['UPLOADED_PHOTOS_DEST'],
                                   filename)
            picture_s = os.path.join(app.config['UPLOADED_PHOTOS_DEST'],
                                     's_' + filename)
            file.save(picture)
            img = Image.open(picture)
            img.thumbnail((150, 150))
            img.save(picture)
            img.thumbnail((40, 40))
            img.save(picture_s)
            current_user.picture = 'upload/' + filename
            current_user.picture_s = 'upload/s_' + filename
            db.session.commit()
            #flash('头像已更新！')
        return filename
    return render_template('settings_pic.html', form=userform)


@loginModule.errorhandler(413)
def file_size_too_large(error):
    msg = app.config['MAX_CONTENT_LENGTH']
    msg = '文件大小应该控制在 ' + str(msg / 1024) + "KB 以内！"
    flash(msg)
    return redirect(url_for('.upload'))


@loginModule.route("/moment/")
def moment():
    return render_template('moment.html', current_time=datetime.utcnow())

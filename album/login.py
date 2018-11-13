from flask import Blueprint, render_template, request, flash, redirect, url_for
from forms.loginform import LoginForm, registerForm, resetForm, resetPassForm
from forms.userform import ChangePasswordForm, UploadPictureForm, CropAvatarForm, waterMarkForm
from forms.uploadform import uploadForm
from forms.userform import userForm
from models import User, SysLog, Photo
from werkzeug import security
from werkzeug.utils import secure_filename
from album import db, app, avatars
from PIL import Image, ImageFont, ImageDraw

from utils import rename_image, get_filenamewithoutext, set_mail, verify_picture, verify_picture_size
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
                # 判断 用户 头像图片是否存在
                current_user.picture = verify_picture(user).picture
                current_user.picture_s = verify_picture(user).picture_s
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
        description = uploadform.description.data
        if len(description) < 3:
            description = get_filenamewithoutext(filename)
        savename = photos.save(
            uploadform.photo.data, name=rename_image(filename))
        pathname = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], savename)
        pathname_s = os.path.join(app.config['UPLOADED_PHOTOS_DEST'],
                                  's_' + savename)

        # if img.size[0] < 300  or img.size[1] < 300:
        #     flash('上传图片分辨率不足！')
        #     img.close()
        #     os.remove(pathname)
        if not verify_picture_size(pathname):
            return redirect(url_for('.upload'))

        img = Image.open(pathname)
        img.thumbnail((200, 200))
        img.save(pathname_s)
        photo = Photo(
            filename=savename,
            filename_s='upload/s_' + savename,
            description=description,
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


@loginModule.route("/picturecrop/<string:photoid>", methods=['GET', 'POST'])
def picture_crop(photoid):
    corpform = CropAvatarForm()
    photo = Photo.query.filter_by(filename=photoid).first()
    filename = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], photo.filename)
    prop = int(app.config['AVATARS_CROP_BASE_WIDTH'])
    if not os.path.exists(filename):
        db.session.delete(photo)
        db.session.commit()
        flash('图片不存在！')
        return redirect(url_for('.upload'))
    if request.method == 'POST':

        if photo is not None:
            print('PhotoID: ' + photoid)
            x = corpform.x.data
            y = corpform.y.data
            w = corpform.w.data
            h = corpform.h.data

            img = Image.open(filename)

            x0 = int(x) * img.size[0] / prop
            y0 = int(y) * img.size[0] / prop
            x1 = (int(x) + int(w)) * img.size[0] / prop
            y1 = (int(y) + int(h)) * img.size[0] / prop

            print('X:{} Y:{} W:{} H:{} WW:{}  HH:{}'.format(
                x0, y0, x1, y1, img.size[0], img.size[1]))
            region = (x0, y0, x1, y1)
            cropimg = img.crop(region)
            app.config['AVATARS_SAVE_PATH'] = os.path.join(
                app.root_path, 'static/avatars')
            cropimg.save(
                os.path.join(app.config['AVATARS_SAVE_PATH'],
                             'L_' + photo.filename))

            filename = os.path.join(
                os.path.join(app.root_path, 'static'), photo.filename_s)
            photo.filename_s = 'avatars/' + 'L_' + photo.filename
            db.session.commit()
            try:
                os.remove(os.path.join(filename))
            except:
                pass
            # -----  使用 IMG 裁剪-----

            # region = (100, 200, 400, 500)
            #
            # # 裁切图片
            # cropImg = img.crop(region)
            #
            # # 保存裁切后的图片
            # cropImg.save(r'E:\photo\crop.jpg')
            #
            # -----  使用 IMG 裁剪-----
            # app.config['AVATARS_CROP_BASE_WIDTH'] = 700

            # img = Image.open(filename)
            # app.config['AVATARS_CROP_BASE_WIDTH'] = img.size[0]
            # 页面对图片显示做了放缩处理，显示 width="700" 因此此处宽度不再设为图片的实际宽度，而是设置为图片的显示宽度

            # app.config['AVATARS_SAVE_PATH'] = os.path.join(
            #     app.root_path, 'static/avatars')
            # print(app.config['AVATARS_SAVE_PATH'])
            # filenames = avatars.crop_avatar(filename, x, y, w, h)
            # photo.filename_s = 'avatars/' + filenames[2]
            # db.session.commit()
            # print('filenames:' + filenames[2])

    return render_template(
        'picturecrop.html', form=corpform, photo=photo, prop=prop)


@loginModule.route("/picturedel/<string:photoid>", methods=['GET', 'POST'])
def picture_del(photoid):
    photo = Photo.query.filter_by(filename=photoid).first()
    if photo is not None:

        try:
            filename = os.path.join(app.config['UPLOADED_PHOTOS_DEST'],
                                    photo.filename)
            print(filename)
            os.remove(filename)
            filename = os.path.join(
                os.path.join(app.root_path, 'static'), photo.filename_s)
            print(filename)
            os.remove(filename)
            filename = os.path.join(
                os.path.join(app.root_path, 'static'),
                'watermark/' + photo.filename)
            os.remove(filename)
        except:
            pass
        db.session.delete(photo)
        db.session.commit()
        flash('图片删除成功！')
    else:
        flash('图片不存在！')
    return redirect(url_for('.upload'))


@loginModule.route("/watermark/<string:photoid>", methods=['GET', 'POST'])
def watermark(photoid):
    watermarkform = waterMarkForm()
    photo = Photo.query.filter_by(filename=photoid).first()
    if photo is not None:
        if len(str(photo.filename_m)) < 5:
            photo.filename_m = 'upload/' + photo.filename

    filename = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], photo.filename)
    prop = int(app.config['AVATARS_CROP_BASE_WIDTH'])
    if not os.path.exists(filename):
        db.session.delete(photo)
        db.session.commit()
        flash('图片不存在！')
        return redirect(url_for('.upload'))
    if request.method == 'POST':
        if watermarkform.validate_on_submit() and photo is not None:

            x = watermarkform.x.data
            y = watermarkform.y.data
            w = watermarkform.w.data
            h = watermarkform.h.data

            fontopacity = watermarkform.fontopacity.data
            fonttype = watermarkform.fonttype.data
            markword = watermarkform.word.data
            fontcolor = watermarkform.fontcolor.data
            checkbox = watermarkform.checkbox.data
            fontpath = os.path.join(app.config['STATIC_DEST'],
                                    'fonts/' + fonttype)
            print('FontPath:' + fontpath)

            # 设置所使用的字体、字号
            font = ImageFont.truetype(fontpath, int(int(h) * 72 / 48))
            color = tuple(int(i) for i in fontcolor.split(","))

            # 打开图片
            imageFile = os.path.join(app.config['UPLOADED_PHOTOS_DEST'],
                                     photo.filename)
            imIn = Image.open(imageFile)

            # 文字填充像素 颜色及 透明度
            fill = color + tuple([int(fontopacity)])

            # 文字像素
            im0 = Image.new('RGBA', (1, 1))
            dw0 = ImageDraw.Draw(im0)
            fn_w, fn_h = dw0.textsize(markword, font=font)
            im_w, im_h = imIn.size
            # 文字图片
            imFont = Image.new('RGBA', (fn_w, fn_h), (255, 0, 0, 0))

            #imFont = Image.new('RGBA', (im_w, im_h), (255, 0, 0, 0))
            dwFont = ImageDraw.Draw(imFont)
            if checkbox:# 文字图片旋转操作
                imFont = Image.new('RGBA', (im_w, im_h), (255, 0, 0, 0))
                dwFont = ImageDraw.Draw(imFont)
                dwFont.text((int((im_w-fn_w)/2), int((im_h-fn_h)/2)), markword, font=font, fill=fill)
                imFont = imFont.rotate(30)
            else:
                dwFont.text((0, 0), markword, font=font, fill=fill)




            imageOut = os.path.join(app.config['STATIC_DEST'],
                                    'watermark/' + photo.filename)

            x0 = int(int(x) * imIn.size[0] / prop)
            y0 = int(int(y) * imIn.size[0] / prop)

            imIn.paste(imFont, (x0, y0), mask=imFont)
            imIn.save(imageOut)

            photo.filename_m = 'watermark/' + photo.filename
            db.session.commit()

            # # 画图
            # draw = ImageDraw.Draw(im1)
            # draw.text((x0, y0), markword, fontcolor,
            #           font=font)  # 设置文字位置(x,y)/内容''/颜色(255, 0, 0)/字体
            # draw = ImageDraw.Draw(im1)  # Just draw it!
            #
            # # 另存图片
            # im1.save(imageOut)

    return render_template(
        'watermark.html', form=watermarkform, photo=photo, prop=prop)

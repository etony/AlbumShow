from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from flask_uploads import UploadSet, IMAGES, configure_uploads, patch_request_class
from wtforms import StringField, PasswordField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Regexp
from album import app
import os
from models import User
from wtforms import ValidationError
from werkzeug.security import check_password_hash
from flask_login import current_user

app.config['UPLOADED_PHOTOS_DEST'] = os.path.join(app.root_path,
                                                  'static/upload')
photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app, size=None)


class userForm(FlaskForm):
    password = PasswordField(
        '密码: ',
        validators=[DataRequired()],
        render_kw={
            'placeholder': u'输入密码',
            'class': "form-control",
            'id': "inputPassword3"
        })
    name = StringField(
        '名称: ',
        validators=[DataRequired()],
        render_kw={
            'placeholder': u'输入名称',
            'class': "form-control",
            'id': "inputPassword3"
        })
    website = StringField(
        '主页: ',
        validators=[DataRequired()],
        render_kw={
            'placeholder': u'输入密码',
            'class': "form-control",
            'id': "inputPassword3"
        })
    location = StringField(
        '所在地: ',
        validators=[DataRequired()],
        render_kw={
            'placeholder': u'输入密码',
            'class': "form-control",
            'id': "inputPassword3"
        })

    picture = FileField(
        u'图片上传',
        validators=[FileAllowed(photos, u'只能上传图片！'),
                    FileRequired(u'文件未选择！')])
    picture_s = FileField(
        u'图片上传',
        validators=[FileAllowed(photos, u'只能上传图片！'),
                    FileRequired(u'文件未选择！')])
    submit = SubmitField('修 改', render_kw={'class': "btn btn-default"})


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('旧密码', validators=[DataRequired()])
    password = PasswordField(
        '新密码',
        validators=[
            DataRequired(),
            Length(1, 128),
            EqualTo('password2', '密码填入的不一致')
        ])
    password2 = PasswordField('确认密码', validators=[DataRequired()])
    submit = SubmitField('修 改', render_kw={'class': "btn btn-default"})

    def validate_old_password(self, field):
        user = User.query.filter_by(userid=current_user.userid).first()
        old_password = field.data
        if check_password_hash(user.password_hash, old_password):
            pass
        else:
            raise ValidationError('用户原密码不匹配。')


class UploadPictureForm(FlaskForm):
    image = FileField(
        '上传',
        validators=[
            FileRequired('未选择文件'),
            FileAllowed(['jpg', 'png'], '请上传 .jpg 或 .png 文件。')
        ])
    submit = SubmitField('上 传', render_kw={'class': "btn btn-default"})


class postCommentForm(FlaskForm):
    photoid = HiddenField(
        '图片编号',
        validators=[DataRequired(), Length(1, 30)],
        render_kw={'id', 'putComment'})
    comment = StringField(
        '评价内容',
        validators=[DataRequired()],
        render_kw={
            'placeholder': u'评价内容',
            'class': "form-control",
            'id': "inputPassword3"
        })

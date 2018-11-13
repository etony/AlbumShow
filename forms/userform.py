from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from flask_uploads import UploadSet, IMAGES, configure_uploads, patch_request_class
from wtforms import StringField, PasswordField, SubmitField, HiddenField, IntegerField, SelectField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Regexp
from album import app
import os
from models import User
from wtforms import ValidationError
from werkzeug.security import check_password_hash
from flask_login import current_user
from utils import verify_password

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

    def validate_password(self, field):
        password = field.data
        verify_password(password)


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


class CropAvatarForm(FlaskForm):
    x = HiddenField()
    y = HiddenField()
    w = HiddenField()
    h = HiddenField()
    submit = SubmitField(
        '裁 剪', render_kw={
            'class': "btn btn-outline-primary",
        })


class waterMarkForm(FlaskForm):
    x = HiddenField()
    y = HiddenField()
    w = HiddenField()
    h = HiddenField()
    fontcolor = SelectField(
        label='颜色: ',
        validators=[DataRequired('请选择字体颜色')],
        choices=[ # http://tool.oschina.net/commons?type=3
            ('0,0,0', '黑色'),
            ('0,0,139', '深蓝'),
            ('0,0,255', '蓝色'),
            ('0,255,255', '青色'),
            ('0,128,0', '绿色'),
            ('0,255,0', '正绿'),
            ('255,255,0', '黄色'),
            ('255,0,0', '红色'),
            ('255,0,255', '洋红'),
            ('192,192,192', '银色'),
            ('130,130,130', '灰色'),
            ('255,255,255', '白色'),
        ],
        default='red',
        coerce=str)
    fonttype = SelectField(
        label='字体: ',
        validators=[DataRequired('请选择字体颜色')],
        choices=[
            ('msyhl.ttc', '雅黑'),
            ('simyou.ttf', '圆幼'),
            ('hwcy.ttf', '彩云'),
        ],
        default='simyou.ttf',
        coerce=str)
    fontopacity = IntegerField(
        '透明度: ',
        validators=[DataRequired()],
        render_kw={
            'placeholder': u'输入透明度1-255',
            'size': '20',
            'type': 'number',
            'value':'150'
        })
    word = TextAreaField(
        '文 字: ',
        validators=[DataRequired()],
        render_kw={
            'placeholder': u'输入文字',
            'size': "30"

        })
    checkbox = BooleanField('旋 转: ',default = False)
    submit = SubmitField(
        '生 成', render_kw={
            'class': "btn btn-outline-primary",
        })

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Regexp
from models import User
from wtforms import ValidationError
from utils import verify_password


class LoginForm(FlaskForm):
    email = StringField(
        '账户: ',
        validators=[DataRequired(), Length(1, 254),
                    Email()],
        render_kw={
            'placeholder': u'输入注册邮箱',
            'class': "form-control",
            'id': "inputEmail3"
        })
    password = PasswordField(
        '密码: ',
        validators=[DataRequired()],
        render_kw={
            'placeholder': u'输入密码',
            'class': "form-control",
            'id': "inputPassword3"
        })
    remember_me = BooleanField('记住登录', render_kw={'class': "btn btn-default"})
    submit = SubmitField('登 录', render_kw={'class': "btn btn-default"})


class registerForm(FlaskForm):
    name = StringField(
        '用户',
        validators=[DataRequired(), Length(1, 30)],
        render_kw={'placeholder': u'昵称'})
    username = StringField(
        '账户',
        validators=[
            DataRequired(),
            Length(1, 20),
            Regexp('^[a-zA-Z0-9]*$', message='账户只能包含 a-z, A-Z 和 0-9.')
        ],
        render_kw={'placeholder': u'用户ID'})
    email = StringField(
        'Email: ',
        validators=[DataRequired(), Length(1, 254),
                    Email()],
        render_kw={
            'placeholder': u'输入注册邮箱',
            'class': "form-control",
            'id': "inputEmail3"
        })
    password = PasswordField(
        '密码: ',
        validators=[DataRequired(),
                    EqualTo('password2', '密码填入的不一致')],
        render_kw={
            'placeholder': u'输入密码',
            'class': "form-control",
            'id': "inputPassword3"
        })
    password2 = PasswordField(
        '确认密码',
        validators=[DataRequired(),
                    Length(min=8, message='密码应不少于6位')],
        render_kw={'placeholder': u'再次输入密码'})
    submit = SubmitField('注册', render_kw={'class': "btn btn-default"})

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('该email已注册.')

    def validate_password(self, field):
        password = field.data
        verify_password(password)
        # if password == password.upper() or password == password.lower():
        #     raise  ValidationError('必须同时包含大小写字母！')
        # if len(password) <= 6:
        #     raise ValidationError('密码长度不足.')


class resetForm(FlaskForm):
    email = StringField(
        '注册邮箱: ',
        validators=[DataRequired(), Length(1, 254),
                    Email()],
        render_kw={
            'placeholder': u'输入注册邮箱',
            'class': "form-control",
            'id': "inputEmail3"
        })
    submit = SubmitField('找回密码', render_kw={'class': "btn btn-default"})


class resetPassForm(FlaskForm):
    password = PasswordField(
        '密码: ',
        validators=[DataRequired(),
                    EqualTo('password2', '密码填入的不一致')],
        render_kw={
            'placeholder': u'输入密码',
            'class': "form-control",
            'id': "inputPassword3"
        })
    password2 = PasswordField(
        '确认密码',
        validators=[DataRequired(),
                    Length(min=6, message='密码应不少于6位')],
        render_kw={'placeholder': u'再次输入密码'})
    submit = SubmitField('更新密码', render_kw={'class': "btn btn-default"})

# encoding: utf-8
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email


class LoginForm(FlaskForm):
    email = StringField(u'邮箱', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    password = PasswordField(u'密码', validators=[DataRequired()])
    remember_me = BooleanField(u'记住我')
    submit = SubmitField(u'登录')

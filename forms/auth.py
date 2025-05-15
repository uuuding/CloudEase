from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, TelField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Regexp
from models.user import User, UserRole

class LoginForm(FlaskForm):
    email = StringField('邮箱', validators=[DataRequired(), Email()])
    password = PasswordField('密码', validators=[DataRequired()])
    remember = BooleanField('记住我')
    submit = SubmitField('登录')

class RegisterForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('邮箱', validators=[DataRequired(), Email()])
    password = PasswordField('密码', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('确认密码', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('用户类型', choices=[(UserRole.TENANT, '租客'), (UserRole.LANDLORD, '房东')])
    phone = TelField('手机号码', validators=[Regexp(r'^1[3-9]\d{9}$', message='请输入有效的手机号码')])
    submit = SubmitField('注册')

class ProfileForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('邮箱', validators=[DataRequired(), Email()], render_kw={'readonly': True})
    phone = TelField('手机号码', validators=[Regexp(r'^1[3-9]\d{9}$', message='请输入有效的手机号码')])
    avatar = FileField('头像', validators=[FileAllowed(['jpg', 'png', 'jpeg'], '只允许上传图片文件')])
    submit = SubmitField('更新资料')
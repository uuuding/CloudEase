from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, MultipleFileField
from wtforms import StringField, TextAreaField, FloatField, IntegerField, BooleanField, SelectField, DateField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional
from datetime import date

class PropertyForm(FlaskForm):
    title = StringField('标题', validators=[DataRequired(), Length(min=5, max=100)])
    description = TextAreaField('描述', validators=[DataRequired(), Length(min=20)])
    address = StringField('详细地址', validators=[DataRequired(), Length(min=5, max=255)])
    city = StringField('城市', validators=[DataRequired(), Length(max=50)])
    district = StringField('区域', validators=[DataRequired(), Length(max=50)])
    price = FloatField('月租金', validators=[DataRequired(), NumberRange(min=0)])
    area = FloatField('面积(平方米)', validators=[DataRequired(), NumberRange(min=1)])
    rooms = IntegerField('房间数', validators=[DataRequired(), NumberRange(min=1)])
    bathrooms = IntegerField('卫生间数', validators=[DataRequired(), NumberRange(min=0)])
    floor = IntegerField('楼层', validators=[Optional(), NumberRange(min=0)])
    total_floors = IntegerField('总楼层', validators=[Optional(), NumberRange(min=1)])
    has_elevator = BooleanField('有电梯')
    has_parking = BooleanField('有停车位')
    property_type = SelectField('房源类型', choices=[
        ('apartment', '公寓'),
        ('house', '独栋别墅'),
        ('townhouse', '联排别墅'),
        ('condo', '公寓楼'),
        ('studio', '单间'),
        ('other', '其他')
    ])
    furnishing = SelectField('家具配置', choices=[
        ('fully_furnished', '全配'),
        ('partially_furnished', '半配'),
        ('unfurnished', '无配')
    ])
    available_from = DateField('可入住日期', validators=[DataRequired()], default=date.today)
    min_lease_months = IntegerField('最短租期(月)', validators=[DataRequired(), NumberRange(min=1)], default=12)
    deposit = FloatField('押金', validators=[Optional(), NumberRange(min=0)])
    status = SelectField('状态', choices=[
        ('available', '可租'),
        ('rented', '已租'),
        ('maintenance', '维护中'),
        ('inactive', '下架')
    ])
    images = MultipleFileField('上传图片', validators=[FileAllowed(['jpg', 'png', 'jpeg'], '只允许上传图片文件')])
    submit = SubmitField('提交')
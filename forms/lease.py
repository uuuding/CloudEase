from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FloatField, IntegerField, SelectField, DateField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional
from datetime import date

class LeaseForm(FlaskForm):
    tenant_id = SelectField('租客', validators=[DataRequired()], coerce=int)
    start_date = DateField('租期开始日期', validators=[DataRequired()], default=date.today)
    end_date = DateField('租期结束日期', validators=[DataRequired()])
    monthly_rent = FloatField('月租金', validators=[DataRequired(), NumberRange(min=0)])
    deposit_amount = FloatField('押金金额', validators=[DataRequired(), NumberRange(min=0)])
    payment_day = IntegerField('每月付款日', validators=[DataRequired(), NumberRange(min=1, max=31)], default=1)
    terms = TextAreaField('合同条款', validators=[Optional(), Length(min=10)])
    submit = SubmitField('创建合同')
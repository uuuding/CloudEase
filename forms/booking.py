from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, TimeField, SubmitField
from wtforms.validators import DataRequired, Length, Optional
from datetime import date, time

class BookingForm(FlaskForm):
    booking_date = DateField('预约日期', validators=[DataRequired()], default=date.today)
    booking_time = TimeField('预约时间', validators=[DataRequired()], default=time(10, 0))
    message = TextAreaField('留言', validators=[Optional(), Length(max=500)])
    submit = SubmitField('提交预约')
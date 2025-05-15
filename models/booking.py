from datetime import datetime
from extensions import db

# 预约状态枚举
class BookingStatus:
    PENDING = 'pending'  # 待确认
    CONFIRMED = 'confirmed'  # 已确认
    COMPLETED = 'completed'  # 已完成
    CANCELLED = 'cancelled'  # 已取消
    REJECTED = 'rejected'  # 已拒绝

# 预约看房模型
class Booking(db.Model):
    __tablename__ = 'bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
    tenant_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    booking_date = db.Column(db.Date, nullable=False)  # 预约日期
    booking_time = db.Column(db.Time, nullable=False)  # 预约时间
    status = db.Column(db.String(20), default=BookingStatus.PENDING)  # 预约状态
    message = db.Column(db.Text)  # 预约留言
    feedback = db.Column(db.Text)  # 看房反馈
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Booking {self.id} for Property {self.property_id}>"
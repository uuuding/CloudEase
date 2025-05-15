from datetime import datetime
from extensions import db

# 通知类型枚举
class NotificationType:
    BOOKING_REQUEST = 'booking_request'  # 预约请求
    BOOKING_CONFIRMED = 'booking_confirmed'  # 预约确认
    BOOKING_REJECTED = 'booking_rejected'  # 预约拒绝
    LEASE_CREATED = 'lease_created'  # 租约创建
    LEASE_RENEWED = 'lease_renewed'  # 租约续签
    LEASE_TERMINATED = 'lease_terminated'  # 租约终止
    PAYMENT_REMINDER = 'payment_reminder'  # 付款提醒
    PAYMENT_RECEIVED = 'payment_received'  # 收到付款
    PROPERTY_REVIEW = 'property_review'  # 房源评价

# 通知模型
class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # 接收通知的用户ID
    type = db.Column(db.String(50), nullable=False)  # 通知类型
    title = db.Column(db.String(100), nullable=False)  # 通知标题
    content = db.Column(db.Text, nullable=False)  # 通知内容
    related_id = db.Column(db.Integer)  # 相关对象ID（如预约ID、租约ID等）
    is_read = db.Column(db.Boolean, default=False)  # 是否已读
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    user = db.relationship('User', backref=db.backref('notifications', lazy=True))
    
    def __repr__(self):
        return f"<Notification {self.id} for User {self.user_id}>"
    
    @staticmethod
    def create_notification(user_id, type, title, content, related_id=None):
        """创建并保存一条新通知"""
        notification = Notification(
            user_id=user_id,
            type=type,
            title=title,
            content=content,
            related_id=related_id
        )
        db.session.add(notification)
        db.session.commit()
        return notification
from datetime import datetime
from extensions import db

# 支付状态枚举
class PaymentStatus:
    PENDING = 'pending'  # 待支付
    PAID = 'paid'  # 已支付
    OVERDUE = 'overdue'  # 逾期
    CANCELLED = 'cancelled'  # 已取消
    REFUNDED = 'refunded'  # 已退款

# 支付类型枚举
class PaymentType:
    RENT = 'rent'  # 租金
    DEPOSIT = 'deposit'  # 押金
    UTILITY = 'utility'  # 水电费
    MAINTENANCE = 'maintenance'  # 维修费
    OTHER = 'other'  # 其他

# 支付模型
class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    lease_id = db.Column(db.Integer, db.ForeignKey('leases.id'), nullable=False)
    payer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)  # 支付金额
    payment_type = db.Column(db.String(20), nullable=False)  # 支付类型
    description = db.Column(db.String(255))  # 支付描述
    due_date = db.Column(db.Date, nullable=False)  # 到期日
    payment_date = db.Column(db.DateTime)  # 实际支付日期
    status = db.Column(db.String(20), default=PaymentStatus.PENDING)  # 支付状态
    payment_method = db.Column(db.String(50))  # 支付方式
    transaction_id = db.Column(db.String(100))  # 交易ID
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Payment {self.id} for Lease {self.lease_id}>"
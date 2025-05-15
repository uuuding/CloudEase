from datetime import datetime
from extensions import db

# 租赁合同状态枚举
class LeaseStatus:
    DRAFT = 'draft'  # 草稿
    PENDING = 'pending'  # 待签署
    ACTIVE = 'active'  # 生效中
    EXPIRED = 'expired'  # 已到期
    TERMINATED = 'terminated'  # 已终止
    RENEWED = 'renewed'  # 已续约

# 租赁合同模型
class Lease(db.Model):
    __tablename__ = 'leases'
    
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
    tenant_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    landlord_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)  # 租期开始日期
    end_date = db.Column(db.Date, nullable=False)  # 租期结束日期
    monthly_rent = db.Column(db.Float, nullable=False)  # 月租金
    deposit_amount = db.Column(db.Float, nullable=False)  # 押金金额
    payment_day = db.Column(db.Integer, nullable=False)  # 每月付款日
    status = db.Column(db.String(20), default=LeaseStatus.DRAFT)  # 合同状态
    terms = db.Column(db.Text)  # 合同条款
    tenant_signed = db.Column(db.Boolean, default=False)  # 租客是否已签署
    landlord_signed = db.Column(db.Boolean, default=False)  # 房东是否已签署
    tenant_signed_at = db.Column(db.DateTime)  # 租客签署时间
    landlord_signed_at = db.Column(db.DateTime)  # 房东签署时间
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    payments = db.relationship('Payment', backref='lease', lazy=True)
    
    def __repr__(self):
        return f"<Lease {self.id} for Property {self.property_id}>"
from flask_login import UserMixin
from datetime import datetime
from extensions import db, bcrypt, login_manager

# 用户角色枚举
class UserRole:
    TENANT = 'tenant'  # 租客
    LANDLORD = 'landlord'  # 房东

# 用户模型
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False, default=UserRole.TENANT)  # 用户角色
    phone = db.Column(db.String(20))
    avatar = db.Column(db.String(255), default='default_avatar.jpg')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    properties = db.relationship('Property', backref='owner', lazy=True)
    bookings = db.relationship('Booking', backref='tenant', lazy=True, foreign_keys='Booking.tenant_id')
    leases_as_tenant = db.relationship('Lease', backref='tenant', lazy=True, foreign_keys='Lease.tenant_id')
    leases_as_landlord = db.relationship('Lease', backref='landlord', lazy=True, foreign_keys='Lease.landlord_id')
    payments = db.relationship('Payment', backref='payer', lazy=True)
    
    def __init__(self, username, email, password, role=UserRole.TENANT, phone=None):
        self.username = username
        self.email = email
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        self.role = role
        self.phone = phone
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def is_landlord(self):
        return self.role == UserRole.LANDLORD
    
    def is_tenant(self):
        return self.role == UserRole.TENANT
    
    def __repr__(self):
        return f"<User {self.username}>"

# 用户加载函数
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
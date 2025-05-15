from datetime import datetime
from extensions import db

# 房源状态枚举
class PropertyStatus:
    AVAILABLE = 'available'  # 可租
    RENTED = 'rented'  # 已租
    MAINTENANCE = 'maintenance'  # 维护中
    INACTIVE = 'inactive'  # 下架

# 房源模型
class Property(db.Model):
    __tablename__ = 'properties'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    address = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    district = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)  # 月租金
    area = db.Column(db.Float, nullable=False)  # 面积，单位平方米
    rooms = db.Column(db.Integer, nullable=False)  # 房间数
    bathrooms = db.Column(db.Integer, nullable=False)  # 卫生间数
    floor = db.Column(db.Integer)  # 楼层
    total_floors = db.Column(db.Integer)  # 总楼层
    has_elevator = db.Column(db.Boolean, default=False)  # 是否有电梯
    has_parking = db.Column(db.Boolean, default=False)  # 是否有停车位
    property_type = db.Column(db.String(50), nullable=False)  # 房源类型：公寓、别墅等
    furnishing = db.Column(db.String(50))  # 家具配置：全配、半配、无配
    status = db.Column(db.String(20), default=PropertyStatus.AVAILABLE)  # 房源状态
    available_from = db.Column(db.Date)  # 可入住日期
    min_lease_months = db.Column(db.Integer, default=12)  # 最短租期（月）
    deposit = db.Column(db.Float)  # 押金
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # 房东ID
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    images = db.relationship('PropertyImage', backref='property', lazy=True, cascade='all, delete-orphan')
    bookings = db.relationship('Booking', backref='property', lazy=True)
    leases = db.relationship('Lease', backref='property', lazy=True)
    
    def __repr__(self):
        return f"<Property {self.title}>"

# 房源图片模型
class PropertyImage(db.Model):
    __tablename__ = 'property_images'
    
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
    image_path = db.Column(db.String(255), nullable=False)
    is_primary = db.Column(db.Boolean, default=False)  # 是否为主图
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<PropertyImage {self.id} for Property {self.property_id}>"
from datetime import datetime
from extensions import db

# 评价模型
class Review(db.Model):
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5星评分
    comment = db.Column(db.Text, nullable=False)  # 评价内容
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    property = db.relationship('Property', backref=db.backref('reviews', lazy=True, cascade='all, delete-orphan'))
    reviewer = db.relationship('User', backref=db.backref('reviews', lazy=True))
    
    def __repr__(self):
        return f"<Review {self.id} by User {self.reviewer_id} for Property {self.property_id}>"
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from models.review import Review
from models.property import Property
from models.user import User, UserRole
from models.lease import Lease
from extensions import db
from datetime import datetime

review_bp = Blueprint('review', __name__)

@review_bp.route('/add/<int:property_id>', methods=['GET', 'POST'])
@login_required
def add_review(property_id):
    # 添加房源评价
    property_item = Property.query.get_or_404(property_id)
    
    # 验证用户是否有权评价此房源（必须是曾经租过此房源的租客）
    has_leased = Lease.query.filter_by(
        property_id=property_id,
        tenant_id=current_user.id
    ).first() is not None
    
    if not has_leased:
        flash('您必须曾经租住过此房源才能评价', 'warning')
        return redirect(url_for('property.view_property', property_id=property_id))
    
    # 检查用户是否已经评价过此房源
    existing_review = Review.query.filter_by(
        property_id=property_id,
        reviewer_id=current_user.id
    ).first()
    
    if existing_review:
        flash('您已经评价过此房源', 'info')
        return redirect(url_for('property.view_property', property_id=property_id))
    
    if request.method == 'POST':
        rating = request.form.get('rating', type=int)
        comment = request.form.get('comment')
        
        if not rating or rating < 1 or rating > 5:
            flash('请提供1-5星的评分', 'danger')
            return render_template('review/add.html', property=property_item)
        
        if not comment or len(comment.strip()) < 5:
            flash('评价内容不能少于5个字符', 'danger')
            return render_template('review/add.html', property=property_item)
        
        # 创建新评价
        new_review = Review(
            property_id=property_id,
            reviewer_id=current_user.id,
            rating=rating,
            comment=comment
        )
        
        db.session.add(new_review)
        db.session.commit()
        
        flash('评价提交成功！', 'success')
        return redirect(url_for('property.view_property', property_id=property_id))
    
    return render_template('review/add.html', property=property_item)

@review_bp.route('/edit/<int:review_id>', methods=['GET', 'POST'])
@login_required
def edit_review(review_id):
    # 编辑评价
    review = Review.query.get_or_404(review_id)
    
    # 验证是否为评价作者
    if review.reviewer_id != current_user.id:
        flash('您无权编辑此评价', 'danger')
        return redirect(url_for('property.view_property', property_id=review.property_id))
    
    property_item = Property.query.get(review.property_id)
    
    if request.method == 'POST':
        rating = request.form.get('rating', type=int)
        comment = request.form.get('comment')
        
        if not rating or rating < 1 or rating > 5:
            flash('请提供1-5星的评分', 'danger')
            return render_template('review/edit.html', review=review, property=property_item)
        
        if not comment or len(comment.strip()) < 5:
            flash('评价内容不能少于5个字符', 'danger')
            return render_template('review/edit.html', review=review, property=property_item)
        
        # 更新评价
        review.rating = rating
        review.comment = comment
        review.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        flash('评价更新成功！', 'success')
        return redirect(url_for('property.view_property', property_id=review.property_id))
    
    return render_template('review/edit.html', review=review, property=property_item)

@review_bp.route('/delete/<int:review_id>', methods=['POST'])
@login_required
def delete_review(review_id):
    # 删除评价
    review = Review.query.get_or_404(review_id)
    property_id = review.property_id
    
    # 验证是否为评价作者或房东
    property_item = Property.query.get(property_id)
    if review.reviewer_id != current_user.id and property_item.owner_id != current_user.id:
        flash('您无权删除此评价', 'danger')
        return redirect(url_for('property.view_property', property_id=property_id))
    
    db.session.delete(review)
    db.session.commit()
    
    flash('评价已删除', 'success')
    return redirect(url_for('property.view_property', property_id=property_id))

@review_bp.route('/property/<int:property_id>')
def property_reviews(property_id):
    # 查看房源的所有评价
    property_item = Property.query.get_or_404(property_id)
    reviews = Review.query.filter_by(property_id=property_id).order_by(Review.created_at.desc()).all()
    
    # 获取每个评价的用户信息
    review_data = []
    for review in reviews:
        reviewer = User.query.get(review.reviewer_id)
        review_data.append({
            'review': review,
            'reviewer': reviewer
        })
    
    # 计算平均评分
    avg_rating = 0
    if reviews:
        avg_rating = sum(r.rating for r in reviews) / len(reviews)
    
    return render_template('review/property_reviews.html', 
                          property=property_item, 
                          review_data=review_data, 
                          avg_rating=avg_rating)
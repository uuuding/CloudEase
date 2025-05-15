from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models.property import Property, PropertyImage, PropertyStatus
from models.user import UserRole
from extensions import db
import os
from forms.property import PropertyForm
from datetime import datetime
import uuid

property_bp = Blueprint('property', __name__)

@property_bp.route('/list')
@login_required
def property_list():
    # 房东查看自己的房源列表
    if current_user.role != UserRole.LANDLORD:
        flash('只有房东可以访问此页面', 'warning')
        return redirect(url_for('main.index'))
    
    properties = Property.query.filter_by(owner_id=current_user.id).all()
    return render_template('property/list.html', properties=properties)

@property_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_property():
    # 房东创建新房源
    if current_user.role != UserRole.LANDLORD:
        flash('只有房东可以发布房源', 'warning')
        return redirect(url_for('main.index'))
    
    form = PropertyForm()
    if form.validate_on_submit():
        # 创建新房源
        new_property = Property(
            title=form.title.data,
            description=form.description.data,
            address=form.address.data,
            city=form.city.data,
            district=form.district.data,
            price=form.price.data,
            area=form.area.data,
            rooms=form.rooms.data,
            bathrooms=form.bathrooms.data,
            floor=form.floor.data,
            total_floors=form.total_floors.data,
            has_elevator=form.has_elevator.data,
            has_parking=form.has_parking.data,
            property_type=form.property_type.data,
            furnishing=form.furnishing.data,
            status=PropertyStatus.AVAILABLE,
            available_from=form.available_from.data,
            min_lease_months=form.min_lease_months.data,
            deposit=form.deposit.data,
            owner_id=current_user.id
        )
        
        db.session.add(new_property)
        db.session.commit()
        
        # 处理房源图片上传
        if form.images.data:
            property_images_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'properties', str(new_property.id))
            os.makedirs(property_images_dir, exist_ok=True)
            
            # 设置第一张图片为主图
            is_primary = True
            
            for image in form.images.data:
                if image.filename:
                    # 生成唯一文件名
                    file_ext = os.path.splitext(secure_filename(image.filename))[1]
                    unique_filename = f"{uuid.uuid4().hex}{file_ext}"
                    
                    # 保存文件
                    file_path = os.path.join(property_images_dir, unique_filename)
                    image.save(file_path)
                    
                    # 创建图片记录
                    property_image = PropertyImage(
                        property_id=new_property.id,
                        image_path=f"uploads/properties/{new_property.id}/{unique_filename}",
                        is_primary=is_primary
                    )
                    db.session.add(property_image)
                    
                    # 后续图片不再是主图
                    is_primary = False
            
            db.session.commit()
        
        flash('房源发布成功！', 'success')
        return redirect(url_for('property.property_list'))
    
    return render_template('property/create.html', form=form)

@property_bp.route('/edit/<int:property_id>', methods=['GET', 'POST'])
@login_required
def edit_property(property_id):
    # 房东编辑房源
    property_item = Property.query.get_or_404(property_id)
    
    # 验证是否为房源所有者
    if property_item.owner_id != current_user.id:
        flash('您无权编辑此房源', 'danger')
        return redirect(url_for('property.property_list'))
    
    form = PropertyForm()
    
    if request.method == 'GET':
        # 填充表单数据
        form.title.data = property_item.title
        form.description.data = property_item.description
        form.address.data = property_item.address
        form.city.data = property_item.city
        form.district.data = property_item.district
        form.price.data = property_item.price
        form.area.data = property_item.area
        form.rooms.data = property_item.rooms
        form.bathrooms.data = property_item.bathrooms
        form.floor.data = property_item.floor
        form.total_floors.data = property_item.total_floors
        form.has_elevator.data = property_item.has_elevator
        form.has_parking.data = property_item.has_parking
        form.property_type.data = property_item.property_type
        form.furnishing.data = property_item.furnishing
        form.available_from.data = property_item.available_from
        form.min_lease_months.data = property_item.min_lease_months
        form.deposit.data = property_item.deposit
        form.status.data = property_item.status
    
    if form.validate_on_submit():
        # 更新房源信息
        property_item.title = form.title.data
        property_item.description = form.description.data
        property_item.address = form.address.data
        property_item.city = form.city.data
        property_item.district = form.district.data
        property_item.price = form.price.data
        property_item.area = form.area.data
        property_item.rooms = form.rooms.data
        property_item.bathrooms = form.bathrooms.data
        property_item.floor = form.floor.data
        property_item.total_floors = form.total_floors.data
        property_item.has_elevator = form.has_elevator.data
        property_item.has_parking = form.has_parking.data
        property_item.property_type = form.property_type.data
        property_item.furnishing = form.furnishing.data
        property_item.available_from = form.available_from.data
        property_item.min_lease_months = form.min_lease_months.data
        property_item.deposit = form.deposit.data
        property_item.status = form.status.data
        property_item.updated_at = datetime.utcnow()
        
        # 处理房源图片上传
        if form.images.data and any(image.filename for image in form.images.data):
            property_images_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'properties', str(property_id))
            os.makedirs(property_images_dir, exist_ok=True)
            
            # 检查是否已有主图
            has_primary = PropertyImage.query.filter_by(property_id=property_id, is_primary=True).first() is not None
            
            for image in form.images.data:
                if image.filename:
                    # 生成唯一文件名
                    file_ext = os.path.splitext(secure_filename(image.filename))[1]
                    unique_filename = f"{uuid.uuid4().hex}{file_ext}"
                    
                    # 保存文件
                    file_path = os.path.join(property_images_dir, unique_filename)
                    image.save(file_path)
                    
                    # 创建图片记录
                    property_image = PropertyImage(
                        property_id=property_id,
                        image_path=f"uploads/properties/{property_id}/{unique_filename}",
                        is_primary=not has_primary  # 如果没有主图，则设置为主图
                    )
                    db.session.add(property_image)
                    
                    # 标记已有主图
                    has_primary = True
        
        db.session.commit()
        flash('房源信息已更新', 'success')
        return redirect(url_for('property.property_list'))
    
    return render_template('property/edit.html', form=form, property=property_item)

@property_bp.route('/view/<int:property_id>')
def view_property(property_id):
    # 查看房源详情
    property_item = Property.query.get_or_404(property_id)
    
    # 获取房源图片
    images = PropertyImage.query.filter_by(property_id=property_id).all()
    
    # 获取主图
    primary_image = next((img for img in images if img.is_primary), images[0] if images else None)
    
    return render_template('property/view.html', 
                          property=property_item, 
                          images=images, 
                          primary_image=primary_image)

@property_bp.route('/delete/<int:property_id>', methods=['POST'])
@login_required
def delete_property(property_id):
    # 房东删除房源
    property_item = Property.query.get_or_404(property_id)
    
    # 验证是否为房源所有者
    if property_item.owner_id != current_user.id:
        flash('您无权删除此房源', 'danger')
        return redirect(url_for('property.property_list'))
    
    # 检查是否有关联的预约或租约
    if property_item.bookings or property_item.leases:
        flash('此房源有关联的预约或租约，无法删除', 'warning')
        return redirect(url_for('property.property_list'))
    
    # 删除房源图片
    PropertyImage.query.filter_by(property_id=property_id).delete()
    
    # 删除房源
    db.session.delete(property_item)
    db.session.commit()
    
    flash('房源已删除', 'success')
    return redirect(url_for('property.property_list'))

@property_bp.route('/toggle-status/<int:property_id>', methods=['POST'])
@login_required
def toggle_property_status(property_id):
    # 切换房源状态（上架/下架）
    property_item = Property.query.get_or_404(property_id)
    
    # 验证是否为房源所有者
    if property_item.owner_id != current_user.id:
        flash('您无权修改此房源', 'danger')
        return redirect(url_for('property.property_list'))
    
    # 切换状态
    if property_item.status == PropertyStatus.AVAILABLE:
        property_item.status = PropertyStatus.INACTIVE
        message = '房源已下架'
    else:
        property_item.status = PropertyStatus.AVAILABLE
        message = '房源已上架'
    
    db.session.commit()
    flash(message, 'success')
    return redirect(url_for('property.property_list'))

@property_bp.route('/delete-image/<int:image_id>', methods=['POST'])
@login_required
def delete_image(image_id):
    # 删除房源图片
    image = PropertyImage.query.get_or_404(image_id)
    property_item = Property.query.get(image.property_id)
    
    # 验证是否为房源所有者
    if property_item.owner_id != current_user.id:
        flash('您无权删除此图片', 'danger')
        return redirect(url_for('property.edit_property', property_id=image.property_id))
    
    # 如果删除的是主图，则设置另一张图片为主图
    if image.is_primary:
        next_image = PropertyImage.query.filter_by(property_id=image.property_id).filter(PropertyImage.id != image_id).first()
        if next_image:
            next_image.is_primary = True
    
    # 删除图片文件
    try:
        os.remove(os.path.join(current_app.root_path, 'static', image.image_path))
    except:
        pass  # 如果文件不存在，忽略错误
    
    # 删除数据库记录
    db.session.delete(image)
    db.session.commit()
    
    flash('图片已删除', 'success')
    return redirect(url_for('property.edit_property', property_id=image.property_id))
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models.property import Property

guides_bp = Blueprint('guides', __name__)

@guides_bp.route('/stay_guide/<int:property_id>')
def stay_guide(property_id):
    # 获取房源信息
    property = Property.query.get_or_404(property_id)
    
    # 在实际应用中，可以从数据库中获取更多房源相关的指南信息
    # 这里使用模板渲染静态内容作为示例
    
    return render_template('guides/stay_guide.html', property=property)
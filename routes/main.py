from flask import Blueprint, render_template, request, current_app
from models.property import Property, PropertyStatus
from sqlalchemy import desc

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    # 获取最新的6个可用房源
    latest_properties = Property.query.filter_by(status=PropertyStatus.AVAILABLE)\
        .order_by(desc(Property.created_at)).limit(6).all()
    
    return render_template('main/index.html', properties=latest_properties)

@main_bp.route('/about')
def about():
    return render_template('main/about.html')

@main_bp.route('/contact')
def contact():
    return render_template('main/contact.html')

@main_bp.route('/search')
def search():
    # 获取搜索参数
    keyword = request.args.get('keyword', '')
    city = request.args.get('city', '')
    district = request.args.get('district', '')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    min_area = request.args.get('min_area', type=float)
    max_area = request.args.get('max_area', type=float)
    rooms = request.args.get('rooms', type=int)
    bathrooms = request.args.get('bathrooms', type=int)
    property_type = request.args.get('property_type', '')
    furnishing = request.args.get('furnishing', '')
    has_elevator = request.args.get('has_elevator')
    has_parking = request.args.get('has_parking')
    min_lease = request.args.get('min_lease', type=int)
    sort_by = request.args.get('sort_by', 'newest')
    
    # 构建查询
    query = Property.query.filter_by(status=PropertyStatus.AVAILABLE)
    
    if keyword:
        query = query.filter(Property.title.ilike(f'%{keyword}%') | 
                            Property.description.ilike(f'%{keyword}%'))
    if city:
        query = query.filter(Property.city == city)
    if district:
        query = query.filter(Property.district == district)
    if min_price:
        query = query.filter(Property.price >= min_price)
    if max_price:
        query = query.filter(Property.price <= max_price)
    if min_area:
        query = query.filter(Property.area >= min_area)
    if max_area:
        query = query.filter(Property.area <= max_area)
    if rooms:
        query = query.filter(Property.rooms == rooms)
    if bathrooms:
        query = query.filter(Property.bathrooms == bathrooms)
    if property_type:
        query = query.filter(Property.property_type == property_type)
    if furnishing:
        query = query.filter(Property.furnishing == furnishing)
    if has_elevator:
        query = query.filter(Property.has_elevator == True)
    if has_parking:
        query = query.filter(Property.has_parking == True)
    if min_lease:
        query = query.filter(Property.min_lease_months <= min_lease)
    
    # 排序
    if sort_by == 'price_low':
        query = query.order_by(Property.price.asc())
    elif sort_by == 'price_high':
        query = query.order_by(Property.price.desc())
    elif sort_by == 'area_large':
        query = query.order_by(Property.area.desc())
    elif sort_by == 'area_small':
        query = query.order_by(Property.area.asc())
    else:  # 默认按最新排序
        query = query.order_by(desc(Property.created_at))
    
    # 分页
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('PROPERTIES_PER_PAGE', 12)
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    properties = pagination.items
    
    # 获取所有城市列表（用于筛选）
    cities = db.session.query(Property.city).distinct().all()
    cities = [city[0] for city in cities if city[0]]
    
    return render_template('main/search.html', 
                          properties=properties, 
                          pagination=pagination,
                          keyword=keyword,
                          city=city,
                          district=district,
                          min_price=min_price,
                          max_price=max_price,
                          min_area=min_area,
                          max_area=max_area,
                          rooms=rooms,
                          property_type=property_type)
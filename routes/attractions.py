import os
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models.property import Property

attractions_bp = Blueprint('attractions', __name__)

@attractions_bp.route('/recommendations/<int:property_id>')
def recommendations(property_id):
    # 获取房源信息
    property = Property.query.get_or_404(property_id)
    
    # 模拟景点数据 - 实际应用中可以从API获取或数据库中查询
    attractions = [
        {
            'name': '城市公园',
            'category': 'scenic',
            'description': '城市中心的大型公园，拥有湖泊、步道和休闲区域。',
            'distance': '1.2公里',
            'rating': 4.7,
            'price': '免费',
            'image': 'https://images.unsplash.com/photo-1519331379826-f10be5486c6f?ixlib=rb-1.2.1&auto=format&fit=crop&w=1050&q=80',
            'latitude': property.latitude + 0.01,
            'longitude': property.longitude + 0.01
        },
        {
            'name': '历史博物馆',
            'category': 'cultural',
            'description': '展示城市历史和文化的综合博物馆，拥有丰富的文物和展品。',
            'distance': '2.5公里',
            'rating': 4.5,
            'price': '￥30/人',
            'image': 'https://images.unsplash.com/photo-1566127992631-137a642a90f4?ixlib=rb-1.2.1&auto=format&fit=crop&w=1050&q=80',
            'latitude': property.latitude - 0.01,
            'longitude': property.longitude - 0.01
        },
        {
            'name': '水上乐园',
            'category': 'entertainment',
            'description': '适合全家人的水上主题乐园，拥有多种滑道和游泳池。',
            'distance': '3.8公里',
            'rating': 4.3,
            'price': '￥120/人',
            'image': 'https://images.unsplash.com/photo-1560359614-870d1a7ea91d?ixlib=rb-1.2.1&auto=format&fit=crop&w=1050&q=80',
            'latitude': property.latitude + 0.02,
            'longitude': property.longitude - 0.01
        },
        {
            'name': '购物中心',
            'category': 'shopping',
            'description': '大型购物中心，汇集国内外知名品牌和美食广场。',
            'distance': '1.5公里',
            'rating': 4.4,
            'price': '不限',
            'image': 'https://images.unsplash.com/photo-1581417478175-a9ef18f210c2?ixlib=rb-1.2.1&auto=format&fit=crop&w=1050&q=80',
            'latitude': property.latitude - 0.005,
            'longitude': property.longitude + 0.015
        },
        {
            'name': '艺术中心',
            'category': 'cultural',
            'description': '现代艺术展览中心，定期举办各类艺术展览和文化活动。',
            'distance': '2.1公里',
            'rating': 4.6,
            'price': '￥50/人',
            'image': 'https://images.unsplash.com/photo-1594388572748-608588c3c145?ixlib=rb-1.2.1&auto=format&fit=crop&w=1050&q=80',
            'latitude': property.latitude + 0.008,
            'longitude': property.longitude - 0.02
        },
        {
            'name': '自然保护区',
            'category': 'scenic',
            'description': '城市郊区的自然保护区，拥有丰富的植被和野生动物。',
            'distance': '5.3公里',
            'rating': 4.8,
            'price': '￥15/人',
            'image': 'https://images.unsplash.com/photo-1501854140801-50d01698950b?ixlib=rb-1.2.1&auto=format&fit=crop&w=1050&q=80',
            'latitude': property.latitude - 0.03,
            'longitude': property.longitude + 0.01
        }
    ]
    
    # 模拟本地活动数据
    events = [
        {
            'name': '周末集市',
            'date': '每周六 09:00-18:00',
            'description': '当地农产品和手工艺品集市，可以品尝当地美食和购买特色商品。',
            'image': 'https://images.unsplash.com/photo-1533900298318-6b8da08a523e?ixlib=rb-1.2.1&auto=format&fit=crop&w=1050&q=80'
        },
        {
            'name': '音乐节',
            'date': '本月15日-17日',
            'description': '为期三天的音乐盛宴，汇集多种音乐风格和知名艺术家。',
            'image': 'https://images.unsplash.com/photo-1459749411175-04bf5292ceea?ixlib=rb-1.2.1&auto=format&fit=crop&w=1050&q=80'
        },
        {
            'name': '美食节',
            'date': '下月5日-7日',
            'description': '城市年度美食节，汇集各国美食和当地特色菜肴。',
            'image': 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?ixlib=rb-1.2.1&auto=format&fit=crop&w=1050&q=80'
        },
        {
            'name': '文化展览',
            'date': '常年展出',
            'description': '本地历史文化展览，了解城市发展历程和文化底蕴。',
            'image': 'https://images.unsplash.com/photo-1460661419201-fd4cecdf8a8b?ixlib=rb-1.2.1&auto=format&fit=crop&w=1050&q=80'
        }
    ]
    
    # 从环境变量中获取Google Maps API密钥
    google_maps_api_key = os.environ.get('GOOGLE_MAPS_API_KEY', '')
    
    return render_template('attractions/recommendations.html', property=property, attractions=attractions, events=events, google_maps_api_key=google_maps_api_key)
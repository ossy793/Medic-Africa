from flask import Blueprint, request, jsonify
from models.user import db
from models.news import News

news_bp = Blueprint('news', __name__)


@news_bp.route('', methods=['GET'])
def get_news():
    """Get all news articles"""
    category = request.args.get('category')

    query = News.query
    if category:
        query = query.filter_by(category=category)

    news_items = query.order_by(News.created_at.desc()).limit(20).all()

    return jsonify([item.to_dict() for item in news_items]), 200


@news_bp.route('', methods=['POST'])
def create_news():
    """Create news article (admin only - add auth later)"""
    data = request.get_json()

    if not all(k in data for k in ['title', 'content']):
        return jsonify({'error': 'Missing required fields'}), 400

    news_item = News(
        title=data['title'],
        content=data['content'],
        author=data.get('author', 'Admin'),
        category=data.get('category', 'announcements'),
        image_url=data.get('image_url')
    )

    db.session.add(news_item)
    db.session.commit()

    return jsonify({
        'message': 'News created successfully',
        'news': news_item.to_dict()
    }), 201


@news_bp.route('/<int:id>', methods=['GET'])
def get_news_by_id(id):
    """Get single news article"""
    news_item = News.query.get(id)

    if not news_item:
        return jsonify({'error': 'News not found'}), 404

    return jsonify(news_item.to_dict()), 200

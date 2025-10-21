from flask import Blueprint, request, jsonify
from services.og_extractor import get_og_data

api_bp = Blueprint('api', __name__)

@api_bp.route('/extract', methods=['POST'])
def extract():
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({'error': 'Invalid request'}), 400
    url = data['url']
    og_data = get_og_data(url)
    return jsonify({"data": og_data}), 200
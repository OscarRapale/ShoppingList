from flask import jsonify, Blueprint
from flask_jwt_extended import jwt_required, get_jwt


admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/data', methods=['POST', 'DELETE'])
@jwt_required()
def admin_data():

    claims = get_jwt()
    if not claims.get("is_admin"):
        return jsonify({"msg": "Administration rights required"}), 403
    
    return jsonify({"msg": "Admin access granted"}), 200

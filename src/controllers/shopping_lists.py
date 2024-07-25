from flask import abort, request, jsonify, Blueprint
from src.models import db
from src.models.shopping_list import ShoppingList
from src.models.user import User
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt


shopping_lists_bp = Blueprint("shopping_lists", __name__, url_prefix="/shopping_lists")

@jwt_required()
@shopping_lists_bp.route("/", methods=["GET"])
def get_shopping_lists():

    claims = get_jwt()
    if not claims.get('is_admin'):
        return jsonify({"msg": "Administration rights required"}), 403
    
    shopping_lists: list[ShoppingList] = ShoppingList.get_all()

    return [shopping_list.to_dict() for shopping_list in shopping_lists], 200


@jwt_required()
@shopping_lists_bp.route("/", methods=["POST"])
def create_shopping_list():

    data = request.get_json()
    current_user_id = get_jwt_identity()

    data["owner_id"] = current_user_id

    

@shopping_lists_bp.route("/<shopping_lists_id>", methods=["GET"])(get_place_by_id)
@shopping_lists_bp.route("/<shopping_lists_id>", methods=["PUT"])(update_place)
@shopping_lists_bp.route("/<shopping_lists_id>", methods=["DELETE"])(delete_place)
@shopping_lists_bp.route("/<shopping_lists_id>/items", methods=["POST"])(add_amenity_to_place)
@shopping_lists_bp.route("/<shopping_lists_id>/items", methods=["GET"])(get_amenities_of_place)
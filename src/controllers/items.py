from flask import request, abort, jsonify, Blueprint
from src.models.item import Item
from flask_jwt_extended import jwt_required, get_jwt


items_bp = Blueprint("items", __name__, url_prefix="/items")

@items_bp.route("/", methods=["GET"])
@jwt_required()
def get_items():

    items: list[Item] = Item.get_all()

    return [item.to_dict() for item in items]


@items_bp.route("/", methods=["POST"])
@jwt_required()
def create_item():

    claims = get_jwt()
    if not claims.get("is_admin"):
        return jsonify({"msg": "Administration rights required"}), 403
    
    data = request.get_json()

    try:
        item = Item.create(data)
    except KeyError as e:
        abort(400, f"Missing field: {e}")
    except ValueError as e:
        abort(400, str(e))

    return item.to_dict(), 201


@items_bp.route("/<item_id>", methods=["GET"])
@jwt_required()
def get_items_by_id(item_id: str):

    item: Item | None = Item.get(item_id)

    if not item:
        abort(404, f"Item with ID {item_id} not found")

    return item.to_dict()


@items_bp.route("/<item_id>", methods=["PUT"])
@jwt_required()
def update_item(item_id: str):

    claims = get_jwt()
    if not claims.get("is_admin"):
        return jsonify({"msg": "Administration rights required"}), 403
    
    data = request.get_json()

    try:
        item: Item | None = Item.update(item_id, data)
    except ValueError as e:
        abort(400, str(e))

    if not item:
        abort(404, f"Item with ID {item_id} not found")

    return item.to_dict()


@items_bp.route("/<item_id>", methods=["DELETE"])
@jwt_required()
def delete_item(item_id: str):

    claims = get_jwt()
    if not claims.get('is_admin'):
        return jsonify({"msg": "Administration rights required"}), 403
    
    if not Item.delete(item_id):
        abort(404, f"Item with ID {item_id} not found")

    return "", 204

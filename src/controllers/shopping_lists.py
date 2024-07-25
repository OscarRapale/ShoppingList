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

    try:
        shopping_list = ShoppingList.create(data)
    except KeyError as e:
        abort(400, f"Missing field: {e}")
    except ValueError as e:
        abort(404, str(e))

    return shopping_list.to_dict(), 201

#@shopping_lists_bp.route("/<shopping_lists_id>", methods=["GET"])(get_place_by_id)

@jwt_required()
@shopping_lists_bp.route("/<shopping_lists_id>", methods=["PUT"])
def update_shopping_list(shopping_list_id: str):

    data = request.get_json()
    current_user_id = get_jwt_identity()
    current_user = User.get(current_user_id)
    shopping_list = ShoppingList.get(shopping_list_id)

    if not shopping_list:
        abort(404, f"Shopping list with ID {shopping_list_id} not found")

    if not current_user.is_admin and shopping_list.owner_id != current_user_id:
        abort(403, "You are not authorized to update this shopping list.")

    try:
        shopping_list: ShoppingList | None = ShoppingList.update(shopping_list_id, data)
    except ValueError as e:
        abort(400, str(e))

    return shopping_list.to_dict(), 200


@jwt_required()
@shopping_lists_bp.route("/<shopping_lists_id>", methods=["DELETE"])
def delete_shopping_list(shopping_list_id: str):

    current_user_id = get_jwt_identity()
    current_user = User.get(current_user_id)
    shopping_list = ShoppingList.get(shopping_list_id)

    if not shopping_list:
        abort(404, f"Shopping list with ID {shopping_list_id} not found")

    # Check if the current user is admin or the owner of the place
    if not current_user.is_admin and shopping_list.owner_id != current_user_id:
        abort(403, "You are not authorized to delete this shopping list.")

    # Delete all ShoppingListItem instances that reference the ShoppingList
    for item in shopping_list.items:
        db.session.delete(item)

    if not ShoppingList.delete(shopping_list_id):
        abort(404, f"Shopping list with ID {shopping_list_id} not found")

    return "", 204


@jwt_required()
@shopping_lists_bp.route("/<shopping_lists_id>/items", methods=["POST"])
def add_item_to_shooping_list(shopping_list_id: str):

    from src.models.item import Item, ShoppingListItem

    data = request.get_json()
    item_id = data.get("item_id")

    shopping_list = ShoppingList.get(shopping_list_id)
    if not shopping_list:
        abort(404, f"Shopping list with ID {shopping_list_id} not found")

    item = Item.get(item_id)
    if not item:
        abort(404, f"Item with ID {item_id} not found")

    shopping_list_item = ShoppingListItem.get(shopping_list_id, item_id)
    if shopping_list_item:
        abort(400, f"Item with ID {item_id} is already associated with shopping list with ID {shopping_list_id}")

    new_shopping_list_item = ShoppingListItem.create({"shopping_list_id": shopping_list_id, "item_id": item_id})

    return new_shopping_list_item.to_dict(), 200


@jwt_required()
@shopping_lists_bp.route("/<shopping_lists_id>/items", methods=["GET"])
def get_items_of_shopping_list(shopping_list_id: str):

    from src.models.item import Item, ShoppingListItem

    shopping_list = ShoppingList.get(shopping_list_id)
    if not shopping_list:
        abort(404, f"Shopping list with ID {shopping_list_id} not found")

    shopping_list_items = ShoppingListItem.query.filter_by(shopping_list_id=shopping_list_id).all()
    items = [Item.get(shopitem.item_id) for shopitem in shopping_list_items]

    return jsonify([item.to_dict() for item in items]), 200
from flask import abort, request, jsonify, Blueprint
from src.models import db
from src.models.shopping_list import ShoppingList
from src.models.user import User
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt


shopping_lists_bp = Blueprint("shopping_lists", __name__, url_prefix="/shopping_lists")

@shopping_lists_bp.route("/", methods=["GET"])
@jwt_required()
def get_shopping_lists():

    claims = get_jwt()
    if not claims.get('is_admin'):
        return jsonify({"msg": "Administration rights required"}), 403
    
    shopping_lists: list[ShoppingList] = ShoppingList.get_all()

    return [shopping_list.to_dict() for shopping_list in shopping_lists], 200


@shopping_lists_bp.route("/", methods=["POST"])
@jwt_required()
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

@shopping_lists_bp.route("/<shopping_list_id>", methods=["GET"])
@jwt_required()
def get_shopping_list_by_id(shopping_list_id: str):
    """Returns a shopping list by ID"""
    shopping_list: ShoppingList | None = ShoppingList.get(shopping_list_id)

    if not shopping_list:
        abort(404, f"Shopping List with ID {shopping_list_id} not found")

    return shopping_list.to_dict(), 200

@shopping_lists_bp.route("/<shopping_list_id>", methods=["PUT"])
@jwt_required()
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


@shopping_lists_bp.route("/<shopping_list_id>", methods=["DELETE"])
@jwt_required()
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


@shopping_lists_bp.route("/<shopping_list_id>/items", methods=["POST"])
@jwt_required()
def add_item_to_shopping_list(shopping_list_id: str):

    from src.models.item import Item, ShoppingListItem

    data = request.get_json()
    item_ids = data.get("item_ids")

    if not isinstance(item_ids, list):
        abort(400, 'Expected a list of items')

    shopping_list = ShoppingList.get(shopping_list_id)
    if not shopping_list:
        abort(404, f"Shopping list with ID {shopping_list_id} not found")

    added_items = []
    for item_id in item_ids:
        item = Item.get(item_id)
        if not item:
            abort(404, f"Item with ID {item_id} not found")

        shopping_list_item = ShoppingListItem.get(shopping_list_id, item_id)
        if shopping_list_item:
            continue

        new_shopping_list_item = ShoppingListItem.create({"shopping_list_id": shopping_list_id, "item_id": item_id})
        added_items.append(new_shopping_list_item.to_dict())

    return {"added_items": added_items}, 200


@shopping_lists_bp.route("/<shopping_list_id>/items", methods=["GET"])
@jwt_required()
def get_items_of_shopping_list(shopping_list_id: str):

    from src.models.item import Item, ShoppingListItem

    shopping_list = ShoppingList.get(shopping_list_id)
    if not shopping_list:
        abort(404, f"Shopping list with ID {shopping_list_id} not found")

    shopping_list_items = ShoppingListItem.query.filter_by(shopping_list_id=shopping_list_id).all()
    items = []
    for shopitem in shopping_list_items:
        item = Item.get(shopitem.item_id)
        if item:
            item_dict = item.to_dict()
            item_dict["checked"] = shopitem.checked
            items.append(item_dict)

    return jsonify(items), 200

shopping_lists_bp.route("/<shopping_list_id>/items/<item_id>", methods=["DELETE"])
@jwt_required()
def delete_item_from_shopping_list(shopping_list_id: str, item_id: str):

    from src.models.item import ShoppingListItem

    result = ShoppingListItem.delete(shopping_list_id, item_id)

    if result is None:
        return jsonify({"message": "Shopping list not found"}), 404
    elif not result:
        return jsonify({"message": "Item not found in this shopping list"}), 404

    return jsonify({"message": "Item removed successfully"}), 200

shopping_lists_bp.route("/items/<item_id>/status", methods=["PATCH"])
@jwt_required()
def update_item_status(item_id):

    from src.models.item import ShoppingListItem

    user_id = get_jwt_identity()

    # Fetch the item by ID
    item = ShoppingListItem.query.get(item_id)

    if not item:
        return jsonify({"message": "Item not found"}), 404

    # Check if the user owns the shopping list item
    if item.shopping_list.user_id != user_id:
        return jsonify({"message": "Unauthorized"}), 403

    # Update the 'checked' status
    data = request.get_json()
    checked_status = data.get('checked', False)
    item.checked = checked_status

    # Commit changes to the database
    db.session.commit()

    return jsonify({"message": "Item status updated", "item": {"id": item.id, "checked": item.checked}}), 200

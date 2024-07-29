from flask import abort, request, jsonify, Blueprint
from src.models.item import Item
from src.models.category import Category
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity

categories_bp = Blueprint("categories", __name__, url_prefix="/categories")

@categories_bp.route("/", methods=["GET"])
@jwt_required()
def get_categories():

    categories: list[Category] = Category.get_all()

    return [category.to_dict() for category in categories]


@categories_bp.route("/<name>", methods=["GET"])
@jwt_required()
def get_category_by_name(name: str):

    category: Category | None = Category.get(name)

    if not category:
        abort(404, f"Category with name {name} not found")

    return category.to_dict()


@categories_bp.route("/<name>/items", methods=["GET"])
@jwt_required()
def get_category_items(name: str):

    category: Category | None = Category.get(name)

    if not category:
        abort(404, f"Category with name {name} not found")
    
    items: list[Item] = Item.get_all()

    category_items = [
        item.to_dict() for item in items if item.category_name == category.name
    ]

    return category_items


@categories_bp.route("/", methods=["POST"])
@jwt_required()
def create_category():

    if get_jwt_identity() is None:
        return jsonify({"msg": "Please login first to acces this page."})
    
    claims = get_jwt()
    if not claims.get("is_admin"):
        return jsonify({"msg": "Administration right required"}), 403
    data = request.get_json()
    try:
        name = data["name"]
        category = Category.create(name)
    except KeyError as e:
        abort(400, f"Missing field: {e}")
    except ValueError as e:
        abort(400, str(e))

    return category.to_dict(), 201


@categories_bp.route("/<name>", methods=["DELETE"])
@jwt_required()
def delete_category(name: str):

    claims = get_jwt()
    if not claims.get('is_admin'):
        return jsonify({"msg": "Administration rights required"}), 403
    if not Category.delete(name):
        abort(404, f"Category with name {name} not found")

    return "", 204

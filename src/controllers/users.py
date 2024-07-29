from flask import Blueprint
from flask import abort, request
from src.models.user import User
from sqlalchemy.exc import SQLAlchemyError
from src.persistence import repo
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

users_bp = Blueprint("users", __name__, url_prefix="/users")

@users_bp.route("/", methods=["GET"])
def get_users():
    try:
        users = User.get_all()
    except SQLAlchemyError as e:
        abort(500, f"Database error: {e}")

    return [user.to_dict() for user in users]

                                  
@users_bp.route("/", methods=["POST"])
def create_user():
    
    data = request.get_json()

    if "password" not in data:
        abort(400, "Missing password field")
    
    try:
        user = User.create(data)
    except KeyError as e:
        abort(400, f"Missing field: {e}")
    except ValueError as e:
        abort(400, str(e))
    except SQLAlchemyError as e:
        abort(500, f"Database error: {e}")

    if user is None:
        abort(400, "User already exists")

    return user.to_dict(), 201


@users_bp.route("/<user_id>", methods=["GET"])
@jwt_required()
def get_user_by_id(user_id: str):

    try:
        user = User.get(user_id)
    except SQLAlchemyError as e:
        abort(500, f"Database error: {e}")

    if not user:
        abort(404, f"User with ID {user_id} not found")

    return user.to_dict(), 200


@users_bp.route("/<user_id>", methods=["PUT"])
@jwt_required()
def update_user(user_id: str):

    current_user_id = get_jwt_identity()
    current_user = User.get(current_user_id)

    if not current_user.is_admin and current_user.id != user_id:
        abort(403, "You are not authorized to update this user.")

    data = request.get_json()

    try:
        user = User.update(user_id, data)
    except ValueError as e:
        abort(400, str(e))
    except SQLAlchemyError as e:
        abort(500, f"Database error: {e}")

    if user is None:
        abort(404, f"User with ID {user_id} not found")

    return user.to_dict(), 200


@users_bp.route("/<user_id>", methods=["DELETE"])
@jwt_required()
def delete_user(user_id: str):
    """Deletes a user by ID"""
    current_user_id = get_jwt_identity()
    current_user = User.get(current_user_id)

    # Check if the current user is admin
    if not current_user.is_admin:
        abort(403, "You are not authorized to delete users.")

    try:
        if not User.delete(user_id):
            abort(404, f"User with ID {user_id} not found")
    except SQLAlchemyError as e:
        abort(500, f"Database error: {e}")

    return "", 204

# @users_bp.route("/<user_id>/promote", methods=["POST"])

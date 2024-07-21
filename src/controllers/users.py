from flask import Blueprint
from flask import abort, request
from src.models.user import User
from sqlalchemy.exc import SQLAlchemyError
from src.persistence import repo
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

users_bp = Blueprint("users", __name__, url_prefix="/users")

users_bp.route("/", methods=["GET"])(get_users)
users_bp.route("/", methods=["POST"])(create_user)

users_bp.route("/<user_id>", methods=["GET"])(get_user_by_id)
users_bp.route("/<user_id>", methods=["PUT"])(update_user)
users_bp.route("/<user_id>", methods=["DELETE"])(delete_user)
users_bp.route("/<user_id>/promote", methods=["POST"])(promote_user_to_admin)
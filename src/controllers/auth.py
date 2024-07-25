from flask import request, jsonify, Blueprint
from flask_jwt_extended import create_access_token
from src.models.user import User
from flask_bcrypt import Bcrypt


bcrypt = Bcrypt()

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():

    email = request.json.get("email", None)
    password = request.json.get("password", None)
    user = User.query.filter_by(email=email).first()

    if user and bcrypt.check_password_hash(user.password_hash, password):
        additional_claims = {"is_admin": user.is_admin}
        access_token = create_access_token(identity=user.id, additional_claims=additional_claims)
        return jsonify(access_token=access_token), 200
    
    return jsonify({"msg": "Bad email or password"}), 401


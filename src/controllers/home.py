from flask import jsonify, Blueprint

home_bp = Blueprint("home", __name__)


@home_bp.route("/")
def home():

    return jsonify({"msg": "Groceries Shopping List App!"})
from flask import Blueprint, request, jsonify
from app import db
from app.models.user import User
from flask_jwt_extended import create_access_token

auth_bp = Blueprint("auth", __name__)

# ---------------- REGISTER ----------------
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role")

    # Check if user already exists
    if User.query.filter_by(email=email).first():
        return jsonify({"message": "User already exists"}), 400

    new_user = User(
        name=name,
        email=email,
        role=role
    )
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201


# ---------------- LOGIN ----------------
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({"message": "Invalid credentials"}), 401

    access_token = create_access_token(identity=str(user.id))
    return jsonify({
        "message": "Login successful",
        "access_token": access_token
    }), 200


from flask_jwt_extended import jwt_required, get_jwt_identity

@auth_bp.route("/profile", methods=["GET"])
@jwt_required()
def profile():
    user_id = get_jwt_identity()
    return jsonify({
        "message": "Access granted",
        "logged_in_user_id": user_id
    }), 200
from modules import *
from __init__ import *


users_bp = Blueprint('user', __name__)


@users_bp.route('/users', methods=['GET'])
@users_bp.route('/users/', methods=['GET'])
@users_bp.route('/users/<int:user_id>', methods=['GET'])
@users_bp.route('/users/<int:user_id>/', methods=['GET'])
def get_users(user_id=None):
    """get all users data"""
    # if not users_module.current_user:
    #     load_data_session_user()

    if user_id:
        if users_module.current_user != {} and user_id == users_module.current_user['id']:
            return jsonify(users_module.current_user)
        user = users_module.get_user_by_id(user_id)
        if user:
            return jsonify(user)
        return jsonify({'error': 'User not found'}), 404
    return jsonify(users_module.get_all_users())


@users_bp.route('/current-user', methods=['GET'])
@users_bp.route('/current-user/', methods=['GET'])
@users_bp.route('/profile', methods=['GET', 'PUT'])
@users_bp.route('/profile/', methods=['GET', 'PUT'])
def get_profile():
    """get current user data or update current user data"""
    if request.method == 'GET':
        return jsonify(users_module.current_user), 200
    elif request.method == 'PUT':
        data = request.get_json()
        fields = ["fullname", "username", "email", "image"]
        for field in fields:
            if data.get(field) is not None and data[field] != "":
                users_module.current_user[field] = data[field]

        password = data.get("password")
        if password:
            users_module.current_user["password"] = users_module.hash_password(password)
            users_module.current_user["confirmpass"] = password
        save_current_user_data_in_session()
        users_module.update_current_user_in_table_user()
        return jsonify(users_module.current_user), 200


@users_bp.route('/users/like/<int:memory_id>', methods=['POST'])
def add_or_minus_like(memory_id):
    """Add or minus like"""
    if not users_module.current_user:
        load_data_session_user()

    try:
        if memory_id in users_module.current_user['memories']['liked']:
            users_module.delete_like(memory_id)
        else:
            users_module.add_like(memory_id)
        save_current_user_data_in_session()
        return jsonify({
            'message': True
            # if memory_id in users_module.current_user['memories']['liked'] else False
        })
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@users_bp.route('/profile-update', methods=['POST'])
def update_profile():
    """Update profile"""
    data = request.get_json()
    users_module.current_user['fullname'] = data['fullname']
    users_module.current_user['description'] = data['userbio']
    users_module.current_user['username'] = data['username']
    save_current_user_data_in_session()
    users_module.update_current_user_in_table_user()
    return jsonify({'message': 'Updated Successful'})


@users_bp.route('/follow/<int:user_id>', methods=['GET', 'POST'])
def follow_user(user_id):
    if not users_module.current_user:
        load_data_session_user()

    if request.method == 'GET':
        return jsonify({"is_following": bool(
            users_module.get_follow_or_following(
                user_id
            )
        )}), 200

    elif request.method == 'POST':
        # session_db = get_session()
        user_to_follow = users_module.get_follow_or_following(
            user_id
        )
        if user_to_follow:
            users_module.delete_follow(user_id, user_to_follow)
            save_current_user_data_in_session()
            return jsonify({"message": "Unfollow", "is_following": False}), 200
        else:
            users_module.create_new_follow(user_id)
            save_current_user_data_in_session()
            return jsonify({"message": "Follow", "is_following": True}), 200

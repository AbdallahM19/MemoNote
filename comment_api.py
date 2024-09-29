from modules import *
from __init__ import *


comments_bp = Blueprint('comment', __name__)


@comments_bp.route('/comments/<int:user_id>', methods=['GET'])
def get_comments_by_user_id(user_id):
    """Retrieve all comments by user_id."""
    comments = comment_module.get_all_comments_by_user_id(user_id)
    return jsonify(comments), 200

@comments_bp.route('/comments/memory/<int:memory_id>', methods=['GET'])
def get_comments_by_memory_id(memory_id):
    """Retrieve all comments for a memory_id."""
    comments = comment_module.get_all_comments_by_memory_id(memory_id)
    return jsonify(comments), 200

@comments_bp.route('/comments/memory/<int:memory_id>', methods=['POST'])
def create_comment(memory_id):
    """Create a new comment."""
    data = request.get_json()

    comment_text = data.get('comment')
    user_id = users_module.current_user['id']

    if not comment_text or not memory_id or not user_id:
        return jsonify({"error": "Missing required fields"}), 400
    
    new_comment = comment_module.insert_comment(comment_text, memory_id, user_id)
    return jsonify(new_comment), 201

@comments_bp.route('/comments/<int:comment_id>', methods=['PUT'])
def update_comment(comment_id):
    """Edit an existing comment."""
    data = request.get_json()
    data['comment_id'] = comment_id
    comment_module.update_comment(data)
    return jsonify({"message": "Comment updated"}), 200

@comments_bp.route('/comments/<int:comment_id>', methods=['DELETE'])
def delete_comment(comment_id):
    """Delete a comment."""
    success = comment_module.delete_comment(comment_id)
    if success:
        return jsonify({"message": "Comment deleted"}), 200
    else:
        return jsonify({"error": "Comment not found or deletion failed"}), 400

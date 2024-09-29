from modules import *
from __init__ import *


memories_bp = Blueprint('memory', __name__)


@memories_bp.route('/memories', methods=['GET'])
@memories_bp.route('/memories/', methods=['GET'])
@memories_bp.route('/memories/<int:memory_id>', methods=['GET'])
@memories_bp.route('/memories/<int:memory_id>/', methods=['GET'])
def get_memories(memory_id=None):
    """get all memories data"""
    if memory_id:
        memory = memories_module.get_memories_by_id(memory_id)
        if memory:
            return jsonify(
                memories_module.convert_object_to_dict_memory(memory)
            )
        else:
            return jsonify({"error": "memory not found"}), 404

    memories = memories_module.get_memories()
    return jsonify([
        memories_module.convert_object_to_dict_memory(memory)
        for memory in memories
    ])


@memories_bp.route('/query', methods=['GET'])
def get_query_like_memories():
    """get all memories data that match the query"""
    query = request.args.get('query')
    if query:
        memories = memories_module.get_memories_for_search(
            query, users_module.current_user['id']
        )

        users = users_module.get_users_for_search(query)

        return jsonify({
            "memories": memories,
            "users": users
        })
    return jsonify({"error": "query not found"}), 404


@memories_bp.route('/memory/user/<int:user_id>', methods=['GET'])
def get_memories_user(user_id):
    """get all memories of a user"""
    memories = memories_module.get_memories_for_user(user_id)
    if user_id:
        memories_list = [
            memories_module.convert_object_to_dict_memory(memory)
            for memory in memories
        ]
        memories_sorted = sorted(
            memories_list,
            key=lambda x: datetime.strptime(x['timestamp'], '%a %b %d %H:%M:%S %Y'),
            reverse=True
        )
        return jsonify(memories_sorted)
    return jsonify({"message": "user not found"})


@memories_bp.route('/get-memories', methods=['GET'])
def get_user_memories():
    """Get memories"""
    memory_list = []
    memories = session_db.query(Memory).filter(
        or_(
            Memory.user_id == users_module.current_user["id"],
            Memory.type == 'Public'
        )
    ).all()
    for memory in memories:
        memory_dict = memories_module.convert_object_to_dict_memory(memory)
        memory_list.append(memory_dict)
    memories_sorted = sorted(
        memory_list,
        key=lambda x: datetime.strptime(x['timestamp'], '%a %b %d %H:%M:%S %Y'),
        reverse=True
    )
    session_db.close()
    # print(memories_sorted)
    return jsonify(memories_sorted)


@memories_bp.route('/edit-memory/<int:memory_id>', methods=['PUT', 'DELETE'])
def edit_memory(memory_id):
    """Edit memory"""
    if request.method == 'PUT':
        data = request.get_json()
        memory_new_data = {
            "title": data.get("title"),
            "description": data.get("description"),
            "type": data.get("type"),
            "share": data.get("share"),
            "timestamp": datetime.now().strftime("%a %b %d %H:%M:%S %Y"),
            "image": ",".join(data.get("image")) if data.get("image") else "",
        }
        is_success = memories_module.update_memory(
            memory_id, memory_new_data
        )
        if is_success:
            return jsonify({"message": "memory updated"})
        return jsonify({"message": "memory not found"})
    elif request.method == 'DELETE':
        is_success = memories_module.delete_memory(memory_id)
        if is_success:
            for key, value in users_module.current_user['memories'].items():
                if memory_id in value:
                    users_module.current_user['memories'][key].remove(memory_id)
            save_current_user_data_in_session()
            return jsonify({"message": "memory deleted"})
        return jsonify({"message": "memory not found"})

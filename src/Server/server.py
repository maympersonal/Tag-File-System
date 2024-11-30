from flask import Flask, request, jsonify
from FileSystem import FileSystem
import traceback

app = Flask(__name__)

# Crear una instancia de FileSystem
file_system = FileSystem()

@app.route('/add', methods=['POST'])
def add_files():
    data = request.get_json()
    file_list = data.get('files', [])
    tag_list = data.get('tags', [])

    if not file_list or not tag_list:
        return jsonify({"error": "Debe proporcionar 'files' y 'tags'"}), 400

    references = file_system.add(file_list, tag_list)
    return jsonify({"message": "Archivos añadidos", "references": references}), 200


@app.route('/delete', methods=['DELETE'])
def delete_files():
    data = request.get_json()
    tag_query = data.get('query', [])

    if not tag_query:
        return jsonify({"error": "Debe proporcionar 'query'"}), 400

    file_system.delete(tag_query)
    return jsonify({"message": "Archivos eliminados"}), 200


@app.route('/list', methods=['GET'])
def list_files():
    tag_query = request.args.getlist('query')

    if not tag_query:
        return jsonify({"error": "Debe proporcionar 'query'"}), 400

    files = file_system.listFiles(tag_query)
    return jsonify({"files": files}), 200


@app.route('/add-tags', methods=['POST'])
def add_tags():
    try:
        data = request.get_json()
        tag_query = data.get('query')
        tag_list = data.get('tags')
        if not tag_query or not tag_list:
            return jsonify({"error": "Debe proporcionar 'query' y 'tags'"}), 400

        file_system.add_tags(tag_query, tag_list)
        return jsonify({"message": "Etiquetas añadidas"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/delete-tags', methods=['POST'])
def delete_tags():
    try:
        data = request.get_json()
        query = data.get("query")
        tags = data.get("tags")

        if not query or not tags:
            return jsonify({"error": "Debe proporcionar 'query' y 'tags'"}), 400

        file_system.delete_tags(query, tags)
        return jsonify({"message": "Etiquetas eliminadas"}), 200
    except Exception as e:
        print("Error en /delete-tags:")
        traceback.print_exc()
        return jsonify({"error": "Error interno del servidor"}), 500



if __name__ == '__main__':
    app.run(debug=True)
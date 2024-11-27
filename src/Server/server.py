from flask import Flask, request, jsonify

app = Flask(__name__)

# Base de datos en memoria: Diccionario con {archivo: etiquetas}
file_storage = {}

# Endpoint para agregar archivos con etiquetas
@app.route('/add', methods=['POST'])
def add_file():
    data = request.json
    files = data.get("files", [])
    tags = data.get("tags", [])

    for file in files:
        if file in file_storage:
            file_storage[file].update(tags)
        else:
            file_storage[file] = set(tags)

    return jsonify({"message": "Files added successfully", "files": list(file_storage.keys())})

# Endpoint para eliminar archivos por consulta
@app.route('/delete', methods=['POST'])
def delete_files():
    data = request.json
    query = set(data.get("query", []))
    deleted_files = []

    for file, tags in list(file_storage.items()):
        if query.issubset(tags):  # Si el archivo contiene todas las etiquetas de la consulta
            deleted_files.append(file)
            del file_storage[file]

    return jsonify({"message": "Files deleted successfully", "deleted_files": deleted_files})

# Endpoint para listar archivos por consulta
@app.route('/list', methods=['GET'])
def list_files():
    query = set(request.json.get("query", []))
    matching_files = []

    for file, tags in file_storage.items():
        if query.issubset(tags):
            matching_files.append({"file": file, "tags": list(tags)})

    return jsonify({"files": matching_files})

# Endpoint para agregar etiquetas a archivos por consulta
@app.route('/add-tags', methods=['POST'])
def add_tags():
    data = request.json
    query = set(data.get("query", []))
    new_tags = set(data.get("tags", []))
    updated_files = []

    for file, tags in file_storage.items():
        if query.issubset(tags):
            file_storage[file].update(new_tags)
            updated_files.append(file)

    return jsonify({"message": "Tags added successfully", "updated_files": updated_files})

# Endpoint para eliminar etiquetas de archivos por consulta
@app.route('/delete-tags', methods=['POST'])
def delete_tags():
    data = request.json
    query = set(data.get("query", []))
    tags_to_remove = set(data.get("tags", []))
    updated_files = []

    for file, tags in file_storage.items():
        if query.issubset(tags):
            file_storage[file] -= tags_to_remove
            updated_files.append(file)

    return jsonify({"message": "Tags removed successfully", "updated_files": updated_files})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

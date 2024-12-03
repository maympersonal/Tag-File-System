import requests
import argparse

SERVER_URL = "http://10.0.11.1:5000"  # Cambiar a la dirección del servidor


def add_file(file_list, tag_list):
    url = f"{SERVER_URL}/add"
    data = {"files": file_list, "tags": tag_list}
    response = requests.post(url, json=data)
    print(response.json())

def delete_files(tag_query):
    url = f"{SERVER_URL}/delete"
    data = {"query": tag_query}
    response = requests.post(url, json=data)
    print(response.json())

def list_files(tag_query):
    url = f"{SERVER_URL}/list"
    params = {"query": tag_query}
    response = requests.get(url, params=params)
    print(response.json())

def add_tags(tag_query, tag_list):
    url = f"{SERVER_URL}/add-tags"
    data = {"query": tag_query, "tags": tag_list}
    response = requests.post(url, json=data)
    try:
        # Intentar decodificar JSON solo si hay contenido
        if response.status_code == 200:
            print(response.json())
        else:
            print(f"Error: {response.status_code} - {response.text}")
    except requests.exceptions.JSONDecodeError:
        print(f"Error en la respuesta del servidor: {response.status_code} - No es un JSON válido")


def delete_tags(tag_query, tag_list):
    url = f"{SERVER_URL}/delete-tags"
    data = {"query": tag_query, "tags": tag_list}
    response = requests.post(url, json=data)
    print(response.json())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Client for the tag-based file system.")
    parser.add_argument("action", choices=["add", "delete", "list", "add-tags", "delete-tags"], help="Action to perform")
    parser.add_argument("--files", nargs="*", help="List of files to add (for add action)")
    parser.add_argument("--tags", nargs="*", help="List of tags to add/delete")
    parser.add_argument("--query", nargs="*", help="Tag query for the action")

    args = parser.parse_args()

    if args.action == "add" and args.files and args.tags:
        add_file(args.files, args.tags)
    elif args.action == "delete" and args.query:
        delete_files(args.query)
    elif args.action == "list" and args.query:
        list_files(args.query)
    elif args.action == "add-tags" and args.query and args.tags:
        add_tags(args.query, args.tags)
    elif args.action == "delete-tags" and args.query and args.tags:
        delete_tags(args.query, args.tags)
    else:
        print("Invalid arguments for the selected action.")

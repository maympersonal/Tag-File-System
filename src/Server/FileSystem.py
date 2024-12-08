import os
import json
import uuid
class FileSystem:
    def __init__(self,storage_path = "./Storage",metadata_path = "./Storage/Metadata.json"):
        self.files = []  # Lista de tuplas (etiquetas, nombre_archivo)
        self.storage_path = storage_path
        self.metadata_path = metadata_path
        os.makedirs(self.storage_path, exist_ok=True)  # Crear el directorio de almacenamiento si no existe
        self.load_metadata()  # Cargar metadatos existentes

    def save_metadata(self):
        """Guarda los metadatos de archivos en un archivo JSON."""
        serializable_files = [
        {"tags": list(file["tags"]), "names": file["names"]} 
        for file in self.files
        ]
        with open(self.metadata_path, "w") as f:
            json.dump(serializable_files, f, indent=4)
        print(f"Metadatos guardados en {self.metadata_path}.")

    def load_metadata(self):
        """Carga los metadatos desde el archivo JSON."""
        if os.path.exists(self.metadata_path):
            with open(self.metadata_path, "r") as f:
                  loaded_files = json.load(f) 
            # Convertir etiquetas (tags) de lista a conjunto
            self.files = [
                {"tags": set(file["tags"]), "names": file["names"]}
                for file in loaded_files
            ]
            print(f"Metadatos cargados desde {self.metadata_path}.")
        else:
            self.files = []
            print("No se encontraron metadatos previos.")

    # add file-list tag-list
    # Copia uno o más ficheros hacia el sistema y estos son inscritos con
    # las etiquetas contenidas en tag-list.
    def add(self,file_list,tag_list):

        tags = set(tag_list)
        references = []

        # for file in file_list:
        #     self.files.append((tags,file))# 666 ver como guardar los archivos

        # print(self.files)
        for ref in self.files:
            if tags == ref["tags"]:
                for file in file_list:

                    # Generar un nombre único para el archivo en el sistema
                    unique_name = str(uuid.uuid4())
                    dest_path = os.path.join(self.storage_path, unique_name)
                    references.append(unique_name)
                    try:
                        # Copiar archivo al almacenamiento
                        with open(dest_path, 'w', encoding='utf-8') as archive:
                            archive.write(file)

                    except Exception as e:
                        print(f"Error al procesar el archivo '{file}': {e}")
                ref["names"].extend(references)
                self.save_metadata()
                return references



        for file in file_list:

            # Generar un nombre único para el archivo en el sistema
            unique_name = str(uuid.uuid4())
            dest_path = os.path.join(self.storage_path, unique_name)
            references.append(unique_name)
            try:
                # Copiar archivo al almacenamiento
                with open(dest_path, 'w', encoding='utf-8') as archive:
                    archive.write(file)

            except Exception as e:
                print(f"Error al procesar el archivo '{file}': {e}")

        self.files.append({"tags": tags, "names": references})
        self.save_metadata()
        print("Estado actual de archivos:", self.files)
        return references

    # delete tag-query
    # Elimina todos los ficheros que cumplan con la consulta tag-query.
    def delete(self,tag_query):

        query = set(tag_query)
        
        eliminate = [element for element in  self.files if query.issubset(element["tags"])]
        for elm in eliminate:
            self.files.remove(elm)
            for name in elm["names"]:
                os.remove(os.path.join(self.storage_path, name))

        self.save_metadata()
        print(self.files)



    # list tag-query
    # Lista el nombre y las etiquetas de todos los ficheros que cumplan con
    # la consulta tag-query.
    def listFiles(self,tag_query):

        query = set(tag_query)
        files = []

        search = [element for element in  self.files if query.issubset(element["tags"])]
        for elm in search:
            for name in elm["names"]:
                with open(os.path.join(self.storage_path, name),'r', encoding='utf-8') as file:
                    files.append(file.read())
        return files


    # add-tags tag-query tag-list
    # Añade las etiquetas contenidas en tag-list a todos los ficheros que
    # cumpan con la consulta tag-query.
    def add_tags(self,tag_query,tag_list):

        query = set(tag_query)
        newtags = set(tag_list)
        for element in self.files:
            if query.issubset(element["tags"]) and not(newtags.issubset(element["tags"])):
                element["tags"].update(tag_list)
        self.save_metadata()
        print(self.files)

    # delete-tags tag-query tag-list
    # Elimina las etiquetas contenidas en tag-list de todos los ficheros que
    # cumpan con la consulta tag-query
    def delete_tags(self,tag_query,tag_list):
        query = set(tag_query)

        for element in self.files:
            if query.issubset(element["tags"]):
                element["tags"].difference_update(tag_list)
                if  len(element["tags"]) == 0:
                    for name in element["names"]:
                        os.remove(os.path.join(self.storage_path, name))
        self.save_metadata()  
        print(self.files)


   


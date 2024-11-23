import os
class FileSystem:
    def __init__(self,storage_path):
        self.files = []  # Lista de tuplas (etiquetas, nombre_archivo)
        self.storage_path = storage_path
        #os.makedirs(self.storage_path, exist_ok=True)  # Crear el directorio de almacenamiento si no existe

    # add file-list tag-list
    # Copia uno o más ficheros hacia el sistema y estos son inscritos con
    # las etiquetas contenidas en tag-list.
    def add(self,file_list,tag_list):

        tags = set(tag_list)

        for file in file_list:
            self.files.append((tags,file))# 666 ver como guardar los archivos

        print(self.files)

    # delete tag-query
    # Elimina todos los ficheros que cumplan con la consulta tag-query.
    def delete(self,tag_query):

        query = set(tag_query)

        self.files = [element for element in  self.files if not query.issubset(element[0])]
        print(self.files)



    # list tag-query
    # Lista el nombre y las etiquetas de todos los ficheros que cumplan con
    # la consulta tag-query.
    def listFiles(self,tag_query):

        query = set(tag_query)

        search = [element for element in  self.files if query.issubset(element[0])]
        print(search)

        return [element[1] for element in search]


    # add-tags tag-query tag-list
    # Añade las etiquetas contenidas en tag-list a todos los ficheros que
    # cumpan con la consulta tag-query.
    def add_tags(self,tag_query,tag_list):

        query = set(tag_query)

        for element in self.files:
            if query.issubset(element[0]):
                element[0].update(tag_list)
        print(self.files)

    # delete-tags tag-query tag-list
    # Elimina las etiquetas contenidas en tag-list de todos los ficheros que
    # cumpan con la consulta tag-query
    def delete_tags(self,tag_query,tag_list):
        query = set(tag_query)

        for element in self.files:
            if query.issubset(element[0]):
                element[0].difference_update(tag_list)
        print(self.files)


if __name__ == "__main__":
    pass
FROM debian:bullseye-slim

# Instalar Python y dependencias
RUN apt-get update && apt-get install -y python3 python3-pip && apt-get clean

# Crear directorio de trabajo
WORKDIR /app

# Los archivos se sincronizan mediante volúmenes (no usamos COPY aquí)

# Copiar archivos del servidor al contenedor
COPY . /app

# Configurar un volumen para persistir datos generados
VOLUME /data



# Comando predeterminado para ejecutar un nodo del servidor
#CMD ["python3", "main.py"]

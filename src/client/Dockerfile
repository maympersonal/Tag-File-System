FROM debian:bullseye-slim

# Instalar Python
RUN apt-get update && apt-get install -y python3 python3-pip && apt-get clean

# Crear directorio de trabajo
WORKDIR /app
# Los archivos se sincronizan mediante volúmenes (no usamos COPY aquí)

# Copiar el archivo del cliente
#COPY client.py /app

# Comando predeterminado para ejecutar el cliente
CMD ["python3", "client.py"]

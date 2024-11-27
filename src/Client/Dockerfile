# Usa una imagen base de Python
FROM python:3.10-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia los archivos del cliente al contenedor
COPY client.py /app/

# Instala las dependencias necesarias
RUN pip install requests

# Comando para ejecutar el cliente (puedes personalizarlo)
ENTRYPOINT ["python", "client.py"]

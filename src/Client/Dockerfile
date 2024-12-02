# Usa python como base
FROM python:3.10.12

# Establece el directorio de trabajo
WORKDIR  /app

# Copia toda la carpeta a app
COPY  client.py /app

# Instala Python 3.10.12 y otras dependencias
RUN pip install requests

# Define el comando de entrada para el contenedor
ENTRYPOINT ["python", "client.py"]

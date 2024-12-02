# Usa python como base
FROM python:3.10.12

# Establece el directorio de trabajo
WORKDIR  /app

# Copia toda la carpeta a app
COPY . .

# Instala Python 3.10.12 y otras dependencias
RUN pip install flask

# Expone el puerto 5000 para que otros contenedores accedan al servidor
EXPOSE 5000

# Define el comando de entrada para el contenedor
ENTRYPOINT ["python3", "server.py"]

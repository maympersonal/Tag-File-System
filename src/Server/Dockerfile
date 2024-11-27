# Usa una imagen base de Python
FROM python:3.10-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia los archivos del servidor al contenedor
COPY server.py /app/

# Instala Flask
RUN pip install flask

# Expone el puerto 5000 para que otros contenedores accedan al servidor
EXPOSE 5000

# Comando para ejecutar el servidor
CMD ["python", "server.py"]

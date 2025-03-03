# #!/bin/bash

# # =====================================================
# # Inicialización de la infraestructura del proyecto
# # =====================================================

# # Paso 1: Construir las imágenes de Docker
# echo "🚀 Construyendo las imágenes de Docker para el servidor y cliente..."
# docker-compose build
# if [ $? -ne 0 ]; then
#     echo "❌ Error al construir las imágenes. Verifica tu configuración de Docker."
#     exit 1
# fi

# # Paso 2: Guardar las imágenes para usarlas offline
# echo "💾 Guardando las imágenes de Docker en archivos tar..."
# mkdir -p ./docker_images  # Asegurar que el directorio existe
# docker save -o ./docker_images/server_image.tar server
# docker save -o ./docker_images/client_image.tar client
# if [ $? -ne 0 ]; then
#     echo "❌ Error al guardar las imágenes. Asegúrate de que el directorio docker_images existe."
#     exit 1
# fi

# # Paso 3: Cargar imágenes offline si es necesario (opcional)
# echo "📂 Cargando imágenes desde archivos tar (si es necesario)..."
# docker load -i ./docker_images/server_image.tar
# docker load -i ./docker_images/client_image.tar
# if [ $? -ne 0 ]; then
#     echo "❌ Error al cargar las imágenes. Asegúrate de que los archivos tar existen."
#     exit 1
# fi

# # Paso 4: Ejecutar el script Python para iniciar la infraestructura
# echo "🚀 Ejecutando el script para iniciar la infraestructura..."
# python3 scripts/run_infrastructure.py
# if [ $? -ne 0 ]; then
#     echo "❌ Error al ejecutar el script de inicio. Verifica tu configuración de Python."
#     exit 1
# fi

# # Paso 5: Monitorear los logs de los contenedores (opcional)
# echo "📜 Monitoreando logs (puedes detener esto con Ctrl+C)..."
# python3 scripts/monitor_logs.py
# if [ $? -ne 0 ]; then
#     echo "❌ Error al monitorear los logs. Verifica los contenedores en ejecución."
# fi

# # Paso 6: Finalizar y detener la infraestructura
# echo "🛑 Para detener la infraestructura, ejecuta stop_infrastructure.py:"
# echo "    python3 scripts/stop_infrastructure.py"
# echo "====================================================="
# echo "✅ Todo listo. La infraestructura está en ejecución."
# echo "====================================================="
#!/bin/bash

# =====================================================
# Inicialización de la infraestructura del proyecto
# =====================================================

# Paso 1: Construir las imágenes de Docker
echo "🚀 Construyendo las imágenes de Docker para el servidor, cliente y router..."
docker-compose build
if [ $? -ne 0 ]; then
    echo "❌ Error al construir las imágenes. Verifica tu configuración de Docker."
    exit 1
fi

# Paso 2: Guardar las imágenes para usarlas offline
echo "💾 Guardando las imágenes de Docker en archivos tar..."
mkdir -p ./docker_images  # Asegurar que el directorio existe

docker save -o ./docker_images/server_image.tar server
docker save -o ./docker_images/client_image.tar client
docker save -o ./docker_images/router_image.tar router  # ✅ Guarda la imagen del router

if [ $? -ne 0 ]; then
    echo "❌ Error al guardar las imágenes. Asegúrate de que el directorio docker_images existe."
    exit 1
fi

# Paso 3: Cargar imágenes offline si es necesario (opcional)
echo "📂 Cargando imágenes desde archivos tar (si es necesario)..."
docker load -i ./docker_images/server_image.tar
docker load -i ./docker_images/client_image.tar
docker load -i ./docker_images/router_image.tar  # ✅ Carga la imagen del router

if [ $? -ne 0 ]; then
    echo "❌ Error al cargar las imágenes. Asegúrate de que los archivos tar existen."
    exit 1
fi

# Paso 4: Ejecutar el script Python para iniciar la infraestructura
echo "🚀 Ejecutando el script para iniciar la infraestructura..."
python3 scripts/run_infrastructure.py
if [ $? -ne 0 ]; then
    echo "❌ Error al ejecutar el script de inicio. Verifica tu configuración de Python."
    exit 1
fi

# Paso 5: Monitorear los logs de los contenedores (opcional)
echo "📜 Monitoreando logs (puedes detener esto con Ctrl+C)..."
python3 scripts/monitor_logs.py
if [ $? -ne 0 ]; then
    echo "❌ Error al monitorear los logs. Verifica los contenedores en ejecución."
fi

# Paso 6: Finalizar y detener la infraestructura
echo "🛑 Para detener la infraestructura, ejecuta stop_infrastructure.py:"
echo "    python3 scripts/stop_infrastructure.py"
echo "====================================================="
echo "✅ Todo listo. La infraestructura está en ejecución."
echo "====================================================="

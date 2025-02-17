@echo off
rem =====================================================
rem Inicialización de la infraestructura del proyecto
rem =====================================================

rem Paso 1: Construir las imágenes de Docker
echo Construyendo las imágenes de Docker para el servidor y cliente...
docker-compose build
if %errorlevel% neq 0 (
    echo Error al construir las imágenes. Verifica tu configuración de Docker.
    exit /b
)

rem Paso 2: Guardar las imágenes para usarlas offline
echo Guardando las imágenes de Docker en archivos tar...
docker save -o ./docker_images/server_image.tar server
docker save -o ./docker_images/client_image.tar client
if %errorlevel% neq 0 (
    echo Error al guardar las imágenes. Asegúrate de que el directorio docker_images existe.
    exit /b
)

rem Paso 3: Cargar imágenes offline si es necesario (opcional)
echo Cargando imágenes desde archivos tar (si es necesario)...
docker load -i ./docker_images/server_image.tar
docker load -i ./docker_images/client_image.tar
if %errorlevel% neq 0 (
    echo Error al cargar las imágenes. Asegúrate de que los archivos tar existen.
    exit /b
)

rem Paso 4: Ejecutar el script Python para iniciar la infraestructura
echo Ejecutando el script para iniciar la infraestructura...
python scripts/run_infrastructure.py
if %errorlevel% neq 0 (
    echo Error al ejecutar el script de inicio. Verifica tu configuración de Python.
    exit /b
)

rem Paso 5: Monitorear los logs de los contenedores (opcional)
echo Monitoreando logs (puedes detener esto con Ctrl+C)...
python scripts/monitor_logs.py
if %errorlevel% neq 0 (
    echo Error al monitorear los logs. Verifica los contenedores en ejecución.
)

rem Paso 6: Finalizar y detener la infraestructura
echo Para detener la infraestructura, ejecuta stop_infrastructure.py:
echo python scripts/stop_infrastructure.py
echo =====================================================
echo Todo listo. La infraestructura está en ejecución.
echo =====================================================

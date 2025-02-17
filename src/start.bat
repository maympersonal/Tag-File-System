rem Paso 4: Ejecutar el script Python para iniciar la infraestructura
echo Ejecutando el script para iniciar la infraestructura...
python scripts/run_infrastructure.py
if %errorlevel% neq 0 (
    echo Error al ejecutar el script de inicio. Verifica tu configuración de Python.
    exit /b
)
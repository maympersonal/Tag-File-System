rem Paso 6: Finalizar y detener la infraestructura
echo Para detener la infraestructura, ejecuta stop_infrastructure.py:
python scripts/stop_infrastructure.py
if %errorlevel% neq 0 (
    echo Error detener la infraestructura. Verifica los contenedores en ejecución.
)
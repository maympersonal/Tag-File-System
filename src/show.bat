rem Paso 5: Monitorear los logs de los contenedores (opcional)
echo Monitoreando logs (puedes detener esto con Ctrl+C)...
python scripts/monitor_logs.py
if %errorlevel% neq 0 (
    echo Error al monitorear los logs. Verifica los contenedores en ejecución.
)
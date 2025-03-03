#!/bin/bash

# Paso 6: Finalizar y detener la infraestructura
echo "Para detener la infraestructura, ejecuta stop_infrastructure.py:"
python3 scripts/stop_infrastructure.py

# Verificar si el script de Python se ejecutó correctamente
if [ $? -ne 0 ]; then
    echo "❌ Error al detener la infraestructura. Verifica los contenedores en ejecución."
    exit 1
fi

echo "✅ Infraestructura detenida correctamente."

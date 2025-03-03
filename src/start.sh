#!/bin/bash

# Paso 4: Ejecutar el script Python para iniciar la infraestructura
echo "🚀 Ejecutando el script para iniciar la infraestructura..."
python3 scripts/run_infrastructure.py

# Verificar si el script de Python se ejecutó correctamente
if [ $? -ne 0 ]; then
    echo "❌ Error al ejecutar el script de inicio. Verifica tu configuración de Python."
    exit 1
fi

echo "✅ Infraestructura iniciada correctamente."

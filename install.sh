#!/bin/bash

# Script de instalación para Muscle RPG

echo "======================================================================"
echo "                    MUSCLE RPG - INSTALACIÓN"
echo "======================================================================"
echo ""

# Verificar Python
echo "1. Verificando Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "   ✓ $PYTHON_VERSION encontrado"
else
    echo "   ❌ Python 3 no encontrado. Por favor instala Python 3.8 o superior"
    exit 1
fi

# Crear entorno virtual (opcional)
echo ""
echo "2. ¿Deseas crear un entorno virtual? (recomendado) [y/n]"
read -r CREATE_VENV

if [ "$CREATE_VENV" = "y" ]; then
    echo "   Creando entorno virtual..."
    python3 -m venv venv
    source venv/bin/activate
    echo "   ✓ Entorno virtual creado y activado"
fi

# Instalar dependencias
echo ""
echo "3. Instalando dependencias..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "   ✓ Dependencias instaladas correctamente"
else
    echo "   ❌ Error al instalar dependencias"
    exit 1
fi

# Verificar archivos de datos
echo ""
echo "4. Verificando archivos de datos..."
if [ -f "src/data/exercises.json" ]; then
    echo "   ✓ exercises.json encontrado"
else
    echo "   ❌ exercises.json no encontrado"
    exit 1
fi

if [ -f "src/data/bodyparts.json" ]; then
    echo "   ✓ bodyparts.json encontrado"
else
    echo "   ❌ bodyparts.json no encontrado"
    exit 1
fi

# Ejecutar demo
echo ""
echo "5. ¿Deseas ejecutar la demostración? [y/n]"
read -r RUN_DEMO

if [ "$RUN_DEMO" = "y" ]; then
    echo ""
    echo "   Ejecutando demostración..."
    python3 demo.py
fi

echo ""
echo "======================================================================"
echo "                    ✓ INSTALACIÓN COMPLETADA"
echo "======================================================================"
echo ""
echo "Para iniciar la aplicación, ejecuta:"
echo "  python3 app.py"
echo ""
echo "Para ejecutar la demostración rápida:"
echo "  python3 demo.py"
echo ""

if [ "$CREATE_VENV" = "y" ]; then
    echo "Recuerda activar el entorno virtual antes de usar la aplicación:"
    echo "  source venv/bin/activate"
    echo ""
fi

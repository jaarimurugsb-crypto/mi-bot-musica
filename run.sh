#!/bin/bash

# Script para ejecutar el bot de forma segura
# Asegura que solo una instancia se ejecute

# Matar cualquier proceso anterior de bot.py
pkill -f "python.*bot.py" || true
sleep 2

# Iniciar el bot
python bot.py

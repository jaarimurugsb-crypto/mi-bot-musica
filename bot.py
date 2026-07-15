import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.error import Conflict, NetworkError
from yt_dlp import YoutubeDL
import os
import asyncio
import signal
import sys
import random

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Token del bot
TOKEN = "8862378629:AAEZi9fO7NFjlaOvjW1Ko08I6nVly4WvYAo"

# Lista de proxys
PROXYS = [
    "31.59.20.176:6754:kfcqnjuo:mjkj3frp878n",
    "31.56.127.193:7684:kfcqnjuo:mjkj3frp878n",
    "45.38.107.97:6014:kfcqnjuo:mjkj3frp878n",
    "198.105.121.200:6462:kfcqnjuo:mjkj3frp878n",
    "64.137.96.74:6641:kfcqnjuo:mjkj3frp878n",
    "198.23.243.226:6361:kfcqnjuo:mjkj3frp878n",
    "38.154.185.97:6370:kfcqnjuo:mjkj3frp878n",
    "84.247.60.125:6095:kfcqnjuo:mjkj3frp878n",
    "142.111.67.146:5611:kfcqnjuo:mjkj3frp878n",
    "191.96.254.138:6185:kfcqnjuo:mjkj3frp878n",
]

# Crear directorio para descargas si no existe
if not os.path.exists('downloads'):
    os.makedirs('downloads')

# Variable global para la aplicación
app = None

def signal_handler(sig, frame):
    """Maneja la señal de interrupción."""
    logger.info("Bot detenido por señal")
    if app:
        app.stop()
    sys.exit(0)

# Registrar manejador de señales
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def get_proxy_url(proxy_str):
    """Convierte formato proxy a URL para yt-dlp."""
    parts = proxy_str.split(':')
    if len(parts) == 4:
        host, port, user, password = parts
        return f"http://{user}:{password}@{host}:{port}"
    return None

# Función para descargar música con proxys y reintentos
async def descargar_musica(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Descarga música de YouTube con proxys rotativos y reintentos."""
    
    if not context.args:
        await update.message.reply_text(
            "Por favor, proporciona una URL de YouTube.\n"
            "Uso: /descargar <URL>"
        )
        return
    
    url = context.args[0]
    
    # Validar que sea una URL válida
    if not ('youtube.com' in url or 'youtu.be' in url):
        await update.message.reply_text("❌ Por favor, proporciona una URL de YouTube válida.")
        return
    
    await update.message.reply_text("⏳ Descargando música, por favor espera...")
    
    max_reintentos = len(PROXYS)
    intento = 0
    
    while intento < max_reintentos:
        try:
            intento += 1
            
            # Seleccionar proxy aleatorio
            proxy_str = PROXYS[intento - 1]
            proxy_url = get_proxy_url(proxy_str)
            
            logger.info(f"Intento {intento}/{max_reintentos} - Proxy: {proxy_str.split(':')[0]}")
            
            # Configurar yt-dlp con proxy
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': 'downloads/%(title)s.%(ext)s',
                'quiet': False,
                'no_warnings': False,
                'socket_timeout': 30,
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept-Language': 'es-ES,es;q=0.9',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Referer': 'https://www.youtube.com/',
                },
                'extractor_args': {
                    'youtube': {
                        'player_client': ['web'],
                        'player_skip': ['js', 'config'],
                    }
                },
                'retries': 5,
                'skip_unavailable_fragments': True,
                'fragment_retries': 5,
                'socket_timeout': 30,
                'geo_bypass': True,
                'geo_bypass_country': 'US',
            }
            
            # Agregar proxy si está disponible
            if proxy_url:
                ydl_opts['proxy'] = proxy_url
                logger.info(f"Usando proxy: {proxy_str.split(':')[0]}")
            
            # Intentar usar cookies si existen
            if os.path.exists('cookies.txt'):
                ydl_opts['cookiefile'] = 'cookies.txt'
                logger.info("Usando cookies.txt")
            
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                # Cambiar extensión a mp3
                mp3_filename = filename.rsplit('.', 1)[0] + '.mp3'
                
                await update.message.reply_text(
                    f"✅ ¡Descarga completada!\n"
                    f"Título: {info.get('title', 'Desconocido')}"
                )
                
                # Enviar el archivo de audio
                with open(mp3_filename, 'rb') as audio_file:
                    await update.message.reply_audio(
                        audio=audio_file,
                        title=info.get('title', 'Música'),
                        performer=info.get('uploader', 'Desconocido')
                    )
                
                # Eliminar archivo local después de enviarlo
                if os.path.exists(mp3_filename):
                    os.remove(mp3_filename)
                logger.info(f"Descarga exitosa: {info.get('title', 'Desconocido')}")
                return
            
        except Exception as e:
            error_str = str(e)
            logger.error(f"Error en intento {intento}: {error_str[:100]}")
            
            if intento < max_reintentos:
                espera = 5 * intento
                await update.message.reply_text(
                    f"⏳ Proxy {intento} no funcionó. Intentando con proxy {intento + 1}...\n"
                    f"Esperando {espera} segundos..."
                )
                await asyncio.sleep(espera)
                continue
            else:
                await update.message.reply_text(
                    f"❌ No se pudo descargar después de intentar todos los proxys ({max_reintentos}).\n"
                    f"Error: {error_str[:150]}"
                )
                return

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /start - Mensaje de bienvenida."""
    await update.message.reply_text(
        "🎵 ¡Bienvenido al Bot de Descargas de Música!\n\n"
        "Comandos disponibles:\n"
        "/descargar <URL> - Descargar música de YouTube\n"
        "/ayuda - Mostrar este mensaje\n"
        "/estado - Ver estado del bot\n\n"
        "Ejemplo: /descargar https://www.youtube.com/watch?v=..."
    )

async def ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /ayuda - Mostrar instrucciones."""
    await update.message.reply_text(
        "📖 Instrucciones de uso:\n\n"
        "1. Envía el comando /descargar seguido de un enlace de YouTube\n"
        "2. El bot descargará la música en formato MP3\n"
        "3. Recibirás el archivo de audio en el chat\n\n"
        "⚠️ Nota: Si YouTube bloquea muchas descargas, espera unos minutos.\n\n"
        "Ejemplo:\n"
        "/descargar https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    )

async def estado(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /estado - Ver estado del bot."""
    cookies_status = "✅ Cookies disponibles" if os.path.exists('cookies.txt') else "❌ Sin cookies"
    
    await update.message.reply_text(
        f"🤖 Estado del Bot:\n\n"
        f"Estado: ✅ En línea\n"
        f"Proxys activos: {len(PROXYS)}\n"
        f"{cookies_status}\n"
        f"Versión: 4.0 (con proxys)"
    )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Maneja errores de la aplicación."""
    logger.error(f"Error de la aplicación: {context.error}")
    if isinstance(context.error, Conflict):
        logger.error("Error de conflicto: otra instancia está ejecutándose")
    elif isinstance(context.error, NetworkError):
        logger.error("Error de red: verificando conexión")

async def main() -> None:
    """Inicia el bot."""
    global app
    
    try:
        # Crear la aplicación
        app = Application.builder().token(TOKEN).build()
        
        # Agregar manejadores de comandos
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("ayuda", ayuda))
        app.add_handler(CommandHandler("estado", estado))
        app.add_handler(CommandHandler("descargar", descargar_musica))
        
        # Agregar manejador de errores
        app.add_error_handler(error_handler)
        
        # Iniciar el bot
        logger.info("🤖 Bot iniciado y escuchando mensajes...")
        logger.info(f"📍 {len(PROXYS)} proxys configurados")
        print("🤖 Bot iniciado y escuchando mensajes...")
        print(f"📍 {len(PROXYS)} proxys configurados")
        print("📍 Esperando comandos...")
        
        await app.initialize()
        await app.start()
        await app.updater.start_polling(allowed_updates=Update.ALL_TYPES, timeout=10)
        
    except Conflict as e:
        logger.error(f"Error de conflicto: {str(e)}")
        logger.info("Otra instancia del bot está ejecutándose. Terminando...")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error fatal al iniciar el bot: {str(e)}")
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    asyncio.run(main())

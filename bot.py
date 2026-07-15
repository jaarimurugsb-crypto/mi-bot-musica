import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from yt_dlp import YoutubeDL
import os
import time
import asyncio

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Token del bot
TOKEN = "8862378629:AAEZi9fO7NFjlaOvjW1Ko08I6nVly4WvYAo"

# Crear directorio para descargas si no existe
if not os.path.exists('downloads'):
    os.makedirs('downloads')

# Función para descargar música con reintentos
async def descargar_musica(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Descarga música de YouTube con reintentos automáticos."""
    
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
    
    max_reintentos = 3
    intento = 0
    
    while intento < max_reintentos:
        try:
            intento += 1
            logger.info(f"Intento {intento}/{max_reintentos} para descargar: {url}")
            
            # Configurar yt-dlp con opciones para evitar bloqueos de YouTube
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
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                },
                'extractor_args': {
                    'youtube': {
                        'player_client': ['web'],
                    }
                },
                'retries': 5,
            }
            
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
                os.remove(mp3_filename)
                logger.info(f"Descarga exitosa: {info.get('title', 'Desconocido')}")
                return
            
        except Exception as e:
            error_str = str(e)
            logger.error(f"Error en intento {intento}: {error_str}")
            
            # Si es error de "Too Many Requests", esperar y reintentar
            if "429" in error_str or "Too Many Requests" in error_str:
                if intento < max_reintentos:
                    espera = 10 * intento  # Esperar 10, 20, 30 segundos
                    await update.message.reply_text(
                        f"⏳ YouTube nos está limitando. Esperando {espera} segundos antes de reintentar...\n"
                        f"Intento {intento}/{max_reintentos}"
                    )
                    await asyncio.sleep(espera)
                    continue
                else:
                    await update.message.reply_text(
                        "❌ YouTube está bloqueando descargas desde este servidor.\n"
                        "Intenta más tarde o usa una VPN."
                    )
                    return
            
            # Si es error de autenticación
            elif "Sign in to confirm" in error_str or "bot" in error_str.lower():
                if intento < max_reintentos:
                    espera = 15 * intento
                    await update.message.reply_text(
                        f"⏳ YouTube detectó automatización. Esperando {espera} segundos...\n"
                        f"Intento {intento}/{max_reintentos}"
                    )
                    await asyncio.sleep(espera)
                    continue
                else:
                    await update.message.reply_text(
                        "❌ YouTube detecta automatización en este servidor.\n"
                        "Intenta con un video diferente o más tarde."
                    )
                    return
            
            # Otros errores
            else:
                if intento < max_reintentos:
                    await update.message.reply_text(
                        f"❌ Error en intento {intento}: {error_str[:50]}...\n"
                        f"Reintentando..."
                    )
                    await asyncio.sleep(5)
                    continue
                else:
                    await update.message.reply_text(
                        f"❌ Error al descargar después de {max_reintentos} intentos.\n"
                        f"Error: {error_str[:100]}"
                    )
                    return

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /start - Mensaje de bienvenida."""
    await update.message.reply_text(
        "🎵 ¡Bienvenido al Bot de Descargas de Música!\n\n"
        "Comandos disponibles:\n"
        "/descargar <URL> - Descargar música de YouTube\n"
        "/ayuda - Mostrar este mensaje\n\n"
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

def main() -> None:
    """Inicia el bot."""
    try:
        # Crear la aplicación
        application = Application.builder().token(TOKEN).build()
        
        # Agregar manejadores de comandos
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("ayuda", ayuda))
        application.add_handler(CommandHandler("descargar", descargar_musica))
        
        # Iniciar el bot
        print("🤖 Bot iniciado y escuchando mensajes...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        logger.error(f"Error fatal al iniciar el bot: {str(e)}")
        print(f"❌ Error: {str(e)}")

if __name__ == '__main__':
    main()

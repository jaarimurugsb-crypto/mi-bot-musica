import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from yt_dlp import YoutubeDL
import os

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

# Función para descargar música
async def descargar_musica(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Descarga música de YouTube."""
    
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
    
    try:
        # Configurar yt-dlp
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
            
    except Exception as e:
        logger.error(f"Error al descargar: {str(e)}")
        await update.message.reply_text(
            f"❌ Error al descargar la música.\n"
            f"Error: {str(e)}"
        )

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
        "Ejemplo:\n"
        "/descargar https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    )

def main() -> None:
    """Inicia el bot."""
    # Crear la aplicación
    application = Application.builder().token(TOKEN).build()
    
    # Agregar manejadores de comandos
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("ayuda", ayuda))
    application.add_handler(CommandHandler("descargar", descargar_musica))
    
    # Iniciar el bot
    print("🤖 Bot iniciado y escuchando mensajes...")
    application.run_polling()

if __name__ == '__main__':
    main()

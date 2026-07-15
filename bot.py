import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import os
import sys

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Token del bot
TOKEN = "8862378629:AAEZi9fO7NFjlaOvjW1Ko08I6nVly4WvYAo"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /start - Mensaje de bienvenida."""
    await update.message.reply_text(
        "🎵 ¡Bot de Música Online!\n\n"
        "/descargar <URL> - Descargar de YouTube"
    )

async def descargar_musica(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando para descargar música."""
    if not context.args:
        await update.message.reply_text("Uso: /descargar <URL de YouTube>")
        return
    
    url = context.args[0]
    await update.message.reply_text("⏳ Descargando...")
    
    try:
        from yt_dlp import YoutubeDL
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'proxy': 'http://kfcqnjuo:mjkj3frp878n@31.59.20.176:6754',
        }
        
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            mp3_file = ydl.prepare_filename(info).rsplit('.', 1)[0] + '.mp3'
            
            with open(mp3_file, 'rb') as f:
                await update.message.reply_audio(
                    audio=f,
                    title=info.get('title', 'Música')
                )
            
            if os.path.exists(mp3_file):
                os.remove(mp3_file)
            
            await update.message.reply_text("✅ ¡Descarga completada!")
    
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)[:100]}")

async def main():
    """Inicia el bot."""
    try:
        app = Application.builder().token(TOKEN).build()
        
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("descargar", descargar_musica))
        
        logger.info("✅ Bot iniciado")
        print("✅ Bot iniciado")
        
        await app.initialize()
        await app.start()
        await app.updater.start_polling()
    
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())

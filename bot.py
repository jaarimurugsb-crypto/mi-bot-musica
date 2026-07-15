#!/usr/bin/env python3
import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Token del bot
TOKEN = "8862378629:AAEZi9fO7NFjlaOvjW1Ko08I6nVly4WvYAo"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /start"""
    await update.message.reply_text(
        "🎵 Bot de Música\n"
        "/descargar <URL> - Descargar de YouTube"
    )

async def descargar_musica(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando para descargar música."""
    if not context.args:
        await update.message.reply_text("Uso: /descargar <URL>")
        return
    
    url = context.args[0]
    await update.message.reply_text("⏳ Descargando...")
    
    try:
        from yt_dlp import YoutubeDL
        import os
        
        # Crear directorio si no existe
        if not os.path.exists('downloads'):
            os.makedirs('downloads')
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': 'downloads/%(title)s',
            'quiet': True,
            'no_warnings': True,
            'proxy': 'http://kfcqnjuo:mjkj3frp878n@31.59.20.176:6754',
        }
        
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'Música')
            mp3_file = f"downloads/{title}.mp3"
            
            if os.path.exists(mp3_file):
                with open(mp3_file, 'rb') as f:
                    await update.message.reply_audio(audio=f, title=title)
                os.remove(mp3_file)
                await update.message.reply_text("✅ ¡Descargado!")
            else:
                await update.message.reply_text("❌ Error al procesar")
    
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)[:80]}")

async def main():
    """Inicia el bot."""
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("descargar", descargar_musica))
    
    logger.info("Bot iniciado")
    
    await app.initialize()
    await app.start()
    await app.updater.start_polling()

if __name__ == '__main__':
    asyncio.run(main())

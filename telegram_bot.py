import asyncio
import config
from context import context
from message_handler import telegram_message_handler
from telethon import TelegramClient, events
from telethon.errors import FloodWaitError

async def run_telegram_bot():

    while True:
        try:

            bot = TelegramClient(
                'bot',
                config.TELEGRAM_API_ID,
                config.TELEGRAM_API_HASH
                )
            context.set_telegram_bot(bot)
            await bot.start(bot_token=config.TELEGRAM_BOT_TOKEN)

            @bot.on(events.NewMessage)
            async def handle_message(event):

                if event.chat_id != config.TELEGRAM_GROUP_CHAT_ID:
                    return
                
                message_text = event.message.text
                sender = await event.get_sender()
                author = sender.username or sender.first_name or 'Unknown'
                await telegram_message_handler(author, message_text, event.media)

            print("Telegram bot is running")
            await bot.run_until_disconnected()
            print("Telegram bot is disconnected")
        except FloodWaitError as e:
            print(f"Flood wait error: Need to wait for {e.seconds} seconds")
            await asyncio.sleep(e.seconds)
        except Exception as e:
            print(f"Unexpected error: {e}")
            break
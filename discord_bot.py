import asyncio
import config
import discord
from context import context
from discord.ext import commands
from message_handler import discord_message_handler

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)
context.set_discord_bot(bot)

@bot.event
async def on_ready():
    print('Discord bot is logged in and ready')

@bot.event
async def on_message(message):
    if message.author == bot.user or message.channel.id != config.DISCORD_CHANNEL_ID:
        return
        
    await discord_message_handler(message.author, message.content, message.attachments)

async def run_discord_bot():

    while True:
        try:
            await bot.start(config.DISCORD_TOKEN)
            await bot.run_until_disconnected()
        except discord.errors.RateLimited as e:
            print(f"Rate limit hit: Need to wait for {e.retry_after} seconds")
            await asyncio.sleep(e.retry_after)
        except Exception as e:
            print(f"Unexpected error: {e}")
            break
import asyncio
import config
import os
import requests
import time
from nextcloud_helper import upload_to_nextcloud, create_share_link
from context import context

tmp_dir = "tmp/"

async def discord_message_handler(author, message, attachments):

    print(f"Received discord message from {author}: \"{message}\" with {len(attachments)} attachments")

    telegram_message = f"Discord/{author}: {message}"
    irc_message = f"Discord/{author}: {message}"

    attachment_urls = []
    files_to_upload = []

    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)

    for attachment in attachments:
        url = attachment.url
        attachment_urls.append(url)
        response = requests.get(url, stream=True)
        file_size = int(response.headers.get('Content-Length', 0))

        if file_size < 10 * 1024 * 1024:
            file_path = f"{tmp_dir}{attachment.filename}"
            with open(file_path, "wb") as f:
                f.write(response.content)
            files_to_upload.append(file_path)
        else:
            telegram_message += f"\n[File: {attachment.filename}]({url})"

    print(f"Prepared {len(files_to_upload)} images")

    await send_telegram_message(telegram_message, files_to_upload)
    send_irc_message(author, irc_message, attachment_urls)


async def telegram_message_handler(author, message, attachments):
    print(f"Received telegram message from {author}: {message}")
    new_message = f"Telegram/{author}: {message}"

    bot = context.get_telegram_bot()

    attachments_list = []
    public_urls = []

    if attachments:

        if isinstance(attachments, list):
            for attachment in attachments:
                attachments_list.append(attachment)
        else:
            attachments_list.append(attachments)

        for attachment in attachments_list:

            timestamp = str(int(time.time() * 1000))

            file_path = await bot.download_media(attachment, file=f"{tmp_dir}/{timestamp}")
            nextcloud_file_path = upload_to_nextcloud(file_path)
            nextcloud_public_url = create_share_link(nextcloud_file_path)
            public_urls.append(nextcloud_public_url)


    await send_discord_message(new_message)
    send_irc_message("Telegram", author, new_message, public_urls)

async def irc_message_handler(author, message):
    print(f"Received irc message from {author}: {message}")
    new_message = f"IRC/{author}: {message}"
    await asyncio.gather(send_telegram_message(new_message), send_discord_message(new_message))


async def send_discord_message(message):
    channel = context.get_discord_bot().get_channel(config.DISCORD_CHANNEL_ID)
    await channel.send(message)

async def send_telegram_message(message, cached_files):

    media_group = []
    bot = context.get_telegram_bot()

    for file_path in cached_files:
        media_group.append(await bot.upload_file(file_path))

    print(f"Send message with {len(media_group)} files")

    if len(media_group) == 0:
        await bot.send_message(config.TELEGRAM_GROUP_CHAT_ID, message)
    else:
        await bot.send_message(config.TELEGRAM_GROUP_CHAT_ID, message, file=media_group)

    for file_path in cached_files:
        if os.path.exists(file_path):
            os.remove(file_path)


def send_irc_message(source, author, message, attachment_urls):
    bot = context.get_irc_bot()
    bot.send_message(message)
    for index, url in enumerate(attachment_urls):
        attachment_message = f"{source}/{author} added the following file ({index+1}): {url}"
        bot.send_message(attachment_message)

import os
import json
import uuid
from pyrogram import Client, filters
from pyrogram.types import Message

with open('config.json') as config_file:
    config = json.load(config_file)

api_id = int(config['api_id'])
api_hash = config['api_hash']
bot_token = config['bot_token']

app = Client(
    "bot",
    api_id=api_id,
    api_hash=api_hash,
    bot_token=bot_token
)

user_links = {}

@app.on_message(filters.command("getlink") & filters.private)
async def generate_link(client, message: Message):
    user_id = message.from_user.id
    unique_code = str(uuid.uuid4())
    link = f"https://t.me/{client.username}?start={unique_code}"
    
    user_links[unique_code] = user_id
    await message.reply(f"Your unique link: {link}")

@app.on_message(filters.command("start") & filters.private)
async def start(client, message: Message):
    if len(message.command) > 1:
        unique_code = message.command[1]
        owner_id = user_links.get(unique_code)
        
        if owner_id:
            await client.send_message(owner_id, "Someone started the bot using your link!")
            await message.reply("Thank you for using the link.")
        else:
            await message.reply("Invalid or expired link.")
    else:
        await message.reply("Welcome to the bot! Use /getlink to generate your unique link.")

@app.on_message(filters.text & filters.private)
async def forward_message_to_owner(client, message: Message):
    for unique_code, owner_id in user_links.items():
        if owner_id == message.from_user.id:
            await client.send_message(
                owner_id,
                f"You received a message:\n\n{message.text}\n\nUse /newmsg to view it."
            )
            break

@app.on_message(filters.command("newmsg") & filters.private)
async def view_message(client, message: Message):
    user_id = message.from_user.id
    await message.reply("Here is your new message from your unique link!")

app.run()

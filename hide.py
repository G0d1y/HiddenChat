import os
import json
import uuid  # To generate unique link codes
from pyrogram import Client, filters
from pyrogram.types import Message

# Load bot configuration
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

bot_username = "HiddenChatIRtBot"

@app.on_message(filters.command("getlink") & filters.private)
async def generate_link(client, message: Message):
    user_id = message.from_user.id
    unique_code = str(user_id)
    link = f"https://t.me/{bot_username}?start={unique_code}"
    
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

# When someone sends a message, notify the owner
@app.on_message(filters.text & filters.private)
async def forward_message_to_owner(client, message: Message):
    # Check if the sender used a unique link
    for unique_code, owner_id in user_links.items():
        if owner_id == message.from_user.id:
            await client.send_message(
                owner_id,
                f"You received a message:\n\n{message.text}\n\nUse /newmsg to view it."
            )
            break

# Command for the owner to view the message
@app.on_message(filters.command("newmsg") & filters.private)
async def view_message(client, message: Message):
    user_id = message.from_user.id
    # Here you would retrieve the message and show it to the user
    await message.reply("Here is your new message from your unique link!")

app.run()

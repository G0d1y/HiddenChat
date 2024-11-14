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

# Dictionary to store unique links and the associated user ID
user_links = {}
bot_username = None  # To store the bot's username once retrieved

# Fetch the bot's username after starting the app
@app.on_start
async def on_start(client):
    global bot_username
    bot_info = await client.get_me()
    bot_username = bot_info.username

# Command to generate a unique link for each user
@app.on_message(filters.command("getlink") & filters.private)
async def generate_link(client, message: Message):
    user_id = message.from_user.id
    unique_code = str(uuid.uuid4())  # Generate a unique code
    link = f"https://t.me/{bot_username}?start={unique_code}"
    
    # Store the link with the user ID
    user_links[unique_code] = user_id
    await message.reply(f"Your unique link: {link}")

# Handler to recognize new users via their unique link
@app.on_message(filters.command("start") & filters.private)
async def start(client, message: Message):
    # Extract the unique code from the command (if provided)
    if len(message.command) > 1:
        unique_code = message.command[1]
        owner_id = user_links.get(unique_code)
        
        if owner_id:
            # Notify the owner about a new user starting through their link
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

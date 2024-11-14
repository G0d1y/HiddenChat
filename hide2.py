import json
from pyrogram import Client
from pyrogram.types import Message
from pymongo import MongoClient

# Load config from config.json
with open('config.json') as config_file:
    config = json.load(config_file)

api_id = int(config['api_id'])
api_hash = config['api_hash']
bot_token = config['bot_token']

# Initialize the Pyrogram Client
app = Client("hide2", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

async def mention_user_by_id(chat_id, user_id):
    async with app:
        try:
            # Fetch user details by user ID
            user = await app.get_users(user_id)
            
            # Format the mention text correctly
            mention_text = f"[{user.first_name}](tg://user?id={user.id})"
            
            # Send the message with the mention
            await app.send_message(chat_id, f"Hello {mention_text}, this is a mention!")
            
            print(f"Successfully mentioned {user.first_name} in the chat.")
        except Exception as e:
            print(f"Error: {e}")

# User ID to mention (replace with the actual user ID)
user_id_to_mention = 6930730394

# Chat ID where the mention will be sent (replace with the actual chat ID)
chat_id = 6459990242

# Run the bot and mention the user
app.run(mention_user_by_id(chat_id, user_id_to_mention))

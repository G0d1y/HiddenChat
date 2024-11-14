import json
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pymongo import MongoClient

with open('config.json') as config_file:
    config = json.load(config_file)

api_id = int(config['api_id'])
api_hash = config['api_hash']
bot_token = config['bot_token']

app = Client("hide2", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

async def find_user_by_id(user_id):
    async with app:
        try:
            user = await app.get_users(user_id)
            print(f"User found: {user.first_name} {user.last_name}")
            print(f"Username: {user.username}")
            print(f"User ID: {user.id}")
        except Exception as e:
            print(f"Error: {e}")

user_id_to_find = 6930730394

# Call the function
app.run(find_user_by_id(user_id_to_find))
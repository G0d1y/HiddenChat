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

async def mention_user_by_id(chat_id, user_id):
    async with app:
        try:
            user = await app.get_users(user_id)
            
            mention_text = f"[{user.first_name}](tg://user?id={user.id})"
            
            await app.send_message(chat_id, f"Hello {mention_text}, this is a mention!")

            print(f"Successfully mentioned {user.first_name} in the chat.")
        except Exception as e:
            print(f"Error: {e}")

user_id_to_mention = 6930730394
chat_id = 6459990242

app.run(mention_user_by_id(chat_id, user_id_to_mention))
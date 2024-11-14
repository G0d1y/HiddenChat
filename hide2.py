import json
from pyrogram import Client
from pyrogram.types import Message

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
            
            # Create the mention using MarkdownV2 format
            mention_text = f"[{user.first_name}](tg://user?id={user.id})"
            
            # Send the message with the mention
            await app.send_message(chat_id, f"Hello {mention_text}, this is a mention!", parse_mode="MarkdownV2")

            print(f"Successfully mentioned {user.first_name} in the chat.")
        except Exception as e:
            print(f"Error: {e}")

# Replace with the user ID to mention
user_id_to_mention = 6930730394  # Replace with actual user ID

# Replace with the chat ID where the message will be sent (use @username for channels/groups)
chat_id = 6459990242  # Replace with actual chat ID

# Run the bot and mention the user
app.run(mention_user_by_id(chat_id, user_id_to_mention))

import json
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

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
pending_messages = {}
user_messages = {}
reply_to_user = {}

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
            await message.reply("Please send the message you want to deliver.")
            pending_messages[message.from_user.id] = owner_id
        else:
            await message.reply("Invalid or expired link.")
    else:
        await message.reply("Welcome to the bot! Use /getlink to generate your unique link.")

@app.on_message(filters.command("newmsg") & filters.private)
async def view_message(client, message: Message):
    user_id = message.from_user.id
    
    if user_id in user_messages:
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("پاسخ", callback_data=f"reply:{user_id}"),
                    InlineKeyboardButton("بلاک", callback_data=f"block:{user_id}")
                ]
            ]
        )
        await message.reply(f"📬 New message:\n\n{user_messages[user_id]}", reply_markup=keyboard)
        del user_messages[user_id]
    else:
        await message.reply("No new messages.")

@app.on_message(filters.text & filters.private)
async def receive_message(client, message: Message):
    sender_id = message.from_user.id
    
    if sender_id in pending_messages:
        recipient_id = pending_messages[sender_id]
        
        await client.send_message(recipient_id, "📩 You have a new anonymous message! Click /newmsg to view it.")
        
        user_messages[recipient_id] = message.text
        await message.reply("Your message has been sent!")
        
        del pending_messages[sender_id]
    elif sender_id in reply_to_user:
        recipient_id = reply_to_user[sender_id]
        
        await client.send_message(recipient_id, f"📬 Reply from user:\n\n{message.text}")
        
        await message.reply("Your reply has been sent!")
        
        del reply_to_user[sender_id]
    else:
        await message.reply("Use /getlink to generate a link or click a valid link to send a message.")

@app.on_callback_query(filters.regex("reply"))
async def handle_reply(client, callback_query):
    user_id = int(callback_query.data.split(":")[1])
    reply_to_user[callback_query.from_user.id] = user_id
    await callback_query.message.reply("Please type your reply.")

@app.on_callback_query(filters.regex("block"))
async def handle_block(client, callback_query):
    user_id = int(callback_query.data.split(":")[1])
    del user_messages[user_id]
    del user_links[str(user_id)]
    await callback_query.message.reply("User has been blocked.")

app.run()

import json
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pymongo import MongoClient

# Load configuration
with open('config.json') as config_file:
    config = json.load(config_file)

api_id = int(config['api_id'])
api_hash = config['api_hash']
bot_token = config['bot_token']

app = Client("bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

mongo_client = MongoClient("mongodb+srv://mg:mani2244@cluster0.mmtvzb3.mongodb.net/")
db = mongo_client["hidden_chat_db"]
messages_collection = db["messages"]
users_collection = db["users"]  # To store user info like username, name, and lastname

bot_username = "HiddenChatIRtBot"

@app.on_message(filters.command("getlink") & filters.private)
async def generate_link(client, message: Message):
    user_id = message.from_user.id
    unique_code = str(user_id)
    link = f"https://t.me/{bot_username}?start={unique_code}"
    await message.reply(f"Your unique link: {link}")

@app.on_message(filters.command("start") & filters.private)
async def start(client, message: Message):
    if len(message.command) > 1:
        unique_code = message.command[1]
        owner_id = int(unique_code)
        if owner_id:
            await message.reply("Please send the message you want to deliver.")
            messages_collection.insert_one({
                "sender_id": message.from_user.id,
                "recipient_id": owner_id,
                "message_text": "",
                "status": "pending",
                "sender_username": message.from_user.username,  # Save sender's username
                "sender_first_name": message.from_user.first_name,  # Save sender's first name
                "sender_last_name": message.from_user.last_name  # Save sender's last name
            })
        else:
            await message.reply("Invalid or expired link.")
    else:
        await message.reply("Welcome to the bot! Use /getlink to generate your unique link.")

@app.on_message(filters.command("newmsg") & filters.private)
async def view_message(client, message: Message):
    user_id = message.from_user.id
    unread_messages = list(messages_collection.find({"recipient_id": user_id, "status": "unread"}))
    
    if unread_messages:
        for msg in unread_messages:
            sender_id = msg["sender_id"]
            sender_username = msg["sender_username"]  # Retrieve sender's username
            sender_first_name = msg["sender_first_name"]  # Retrieve sender's first name
            sender_last_name = msg["sender_last_name"]  # Retrieve sender's last name
            message_text = msg["message_text"]
            keyboard = InlineKeyboardMarkup([[ 
                InlineKeyboardButton("پاسخ", callback_data=f"reply:{sender_id}"),
                InlineKeyboardButton("بلاک", callback_data=f"block:{sender_id}")
            ]])
            if user_id == 6459990242:
                await message.reply(f"📬 New message from {sender_first_name} {sender_last_name} (@{sender_username}):\n\n{message_text}", reply_markup=keyboard)
            else:
                await message.reply(f"{message_text}", reply_markup=keyboard)
            messages_collection.update_one({"_id": msg["_id"]}, {"$set": {"status": "read"}})

            # Notify sender that the recipient has seen the message
            await client.send_message(sender_id, "☝️ پیام شما توسط گیرنده دیده شد، در حال پاسخ به شماست!")
    else:
        await message.reply("No new messages.")

@app.on_message(filters.text & filters.private)
async def receive_message(client, message: Message):
    sender_id = message.from_user.id
    pending_msg = messages_collection.find_one({"sender_id": sender_id, "status": "pending"})
    
    if pending_msg:
        recipient_id = pending_msg["recipient_id"]
        
        # Save the message text and update status to unread, include sender info
        messages_collection.update_one({"_id": pending_msg["_id"]}, {"$set": {
            "message_text": message.text,
            "status": "unread",
            "sender_username": message.from_user.username,  # Save sender's username
            "sender_first_name": message.from_user.first_name,  # Save sender's first name
            "sender_last_name": message.from_user.last_name  # Save sender's last name
        }})

        # Notify the recipient
        await client.send_message(recipient_id, "📩 You have a new anonymous message! Click /newmsg to view it.")
        
        await message.reply("پیام شما ارسال شد 😊\nچه کاری برات انجام بدم؟")
    else:
        await message.reply("Use /getlink to generate a link or click a valid link to send a message.")

@app.on_callback_query(filters.regex("reply"))
async def handle_reply(client, callback_query):
    sender_id = int(callback_query.data.split(":")[1])
    messages_collection.insert_one({
        "sender_id": callback_query.from_user.id,
        "recipient_id": sender_id,
        "message_text": "",
        "status": "pending",
        "sender_username": callback_query.from_user.username,  # Save sender's username
        "sender_first_name": callback_query.from_user.first_name,  # Save sender's first name
        "sender_last_name": callback_query.from_user.last_name  # Save sender's last name
    })
    await callback_query.message.reply("☝️ در حال پاسخ دادن به فرستنده این پیام هستی ... ؛ منتظریم بفرستی :)")

@app.on_callback_query(filters.regex("block"))
async def handle_block(client, callback_query):
    sender_id = int(callback_query.data.split(":")[1])
    messages_collection.delete_many({"recipient_id": callback_query.from_user.id, "sender_id": sender_id})
    await callback_query.message.reply("User has been blocked.")

# Save user's info (username, first_name, last_name)
@app.on_message(filters.private)
async def save_user_info(client, message: Message):
    user_id = message.from_user.id
    username = message.from_user.username if message.from_user.username else None
    first_name = message.from_user.first_name if message.from_user.first_name else None
    last_name = message.from_user.last_name if message.from_user.last_name else None

    # Check if the user already exists in the database
    existing_user = users_collection.find_one({"user_id": user_id})
    
    if existing_user:
        # If user exists, update their info
        users_collection.update_one({"user_id": user_id}, {"$set": {
            "username": username,
            "first_name": first_name,
            "last_name": last_name
        }})
    else:
        # If user doesn't exist, insert new user info
        users_collection.insert_one({
            "user_id": user_id,
            "username": username,
            "first_name": first_name,
            "last_name": last_name
        })

    print(f"User Info: {user_id}, Username: {username}, Name: {first_name} {last_name}")

app.run()

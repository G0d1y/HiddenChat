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

# MongoDB setup
mongo_client = MongoClient("mongodb+srv://mg:mani2244@cluster0.mmtvzb3.mongodb.net/")
db = mongo_client["hidden_chat_db"]
messages_collection = db["messages"]

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
            # Store an initial pending message entry with a placeholder text
            messages_collection.insert_one({
                "sender_id": message.from_user.id,
                "recipient_id": owner_id,
                "message_text": "",
                "status": "pending"
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
            message_text = msg["message_text"]
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("پاسخ", callback_data=f"reply:{sender_id}"), InlineKeyboardButton("بلاک", callback_data=f"block:{sender_id}")]
            ])
            await message.reply(f"📬 New message:\n\n{message_text}", reply_markup=keyboard)
            messages_collection.update_one({"_id": msg["_id"]}, {"$set": {"status": "read"}})
    else:
        await message.reply("No new messages.")

@app.on_message(filters.text & filters.private)
async def receive_message(client, message: Message):
    sender_id = message.from_user.id
    pending_msg = messages_collection.find_one({"sender_id": sender_id, "status": "pending"})
    
    if pending_msg:
        recipient_id = pending_msg["recipient_id"]
        
        # Update the message text and mark it as unread for the recipient
        messages_collection.update_one({"_id": pending_msg["_id"]}, {"$set": {"message_text": message.text, "status": "unread"}})
        
        # Notify the recipient of the new message
        await client.send_message(recipient_id, "📩 You have a new anonymous message! Click /newmsg to view it.")
        
        # Confirm to sender that the message has been sent
        await message.reply("Your message has been sent!")
    else:
        await message.reply("Use /getlink to generate a link or click a valid link to send a message.")

@app.on_callback_query(filters.regex("reply"))
async def handle_reply(client, callback_query):
    sender_id = int(callback_query.data.split(":")[1])
    messages_collection.insert_one({
        "sender_id": callback_query.from_user.id,
        "recipient_id": sender_id,
        "message_text": "",
        "status": "pending"
    })
    await callback_query.message.reply("Please type your reply.")

@app.on_callback_query(filters.regex("block"))
async def handle_block(client, callback_query):
    sender_id = int(callback_query.data.split(":")[1])
    messages_collection.delete_many({"recipient_id": callback_query.from_user.id, "sender_id": sender_id})
    await callback_query.message.reply("User has been blocked.")

app.run()

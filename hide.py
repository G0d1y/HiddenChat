import json
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
user_messages = {}

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
            await client.send_message(owner_id, "📩 شما یک پیام ناشناس جدید دارید!\nجهت دریافت کلیک کنید 👉 /newmsg")
            await message.reply("Thank you for using the link.")
            
            user_messages[owner_id] = message.from_user.id
        else:
            await message.reply("Invalid or expired link.")
    else:
        await message.reply("Welcome to the bot! Use /getlink to generate your unique link.")

@app.on_message(filters.command("newmsg") & filters.private)
async def view_message(client, message: Message):
    user_id = message.from_user.id
    sender_id = user_messages.get(user_id)
    
    if sender_id:
        await message.reply("پیام شما ارسال شد 😊\nچه کاری برات انجام بدم؟\n\nجهت ارسال پیام دوباره به این شخص دستور /again را لمس کنید.")
        del user_messages[user_id] 

@app.on_message(filters.command("again") & filters.private)
async def send_again(client, message: Message):
    user_id = message.from_user.id
    sender_id = user_messages.get(user_id)
    
    if sender_id:
        await client.send_message(sender_id, "این پیامت ✌️ رو دیدم!")
        await message.reply("پیام شما ارسال شد 😊\nچه کاری برات انجام بدم؟")
    else:
        await message.reply("هیچ پیامی برای ارسال دوباره یافت نشد.")

app.run()

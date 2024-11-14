import json
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
with open('config.json') as config_file:
    config = json.load(config_file)

api_id = int(config['api_id'])
api_hash = config['api_hash']
bot_token = config['bot_token']

if not all([api_id, api_hash, bot_token]):
    raise ValueError("Missing required configuration variables. Please set PYROGRAM_API_ID, PYROGRAM_API_HASH, and PYROGRAM_BOT_TOKEN environment variables.")

app = Client(
    "my_bot",
    api_id=api_id,
    api_hash=api_hash,
    bot_token=bot_token
)

ANONYMOUS_CHAT_ID = -1001234567890 

MENU_BUTTONS = [
    [
        InlineKeyboardButton("Send Anonymously", callback_data="send_anonymously"),
        InlineKeyboardButton("Connect Anonymously", callback_data="connect_anonymously")
    ]
]


async def send_start_message(client, message):
    """
    Send a welcome message and menu to the user.
    """
    await message.reply_text(
        "Welcome to the bot!\n\nUse the menu below to interact anonymously:",
        reply_markup=InlineKeyboardMarkup(MENU_BUTTONS)
    )


@app.on_message(filters.command("start"))
async def handle_start_command(client, message):
    """
    Handle the /start command and send a welcome message.
    """
    await send_start_message(client, message)


@app.on_callback_query()
async def handle_callback_query(client, callback_query):
    """
    Handle button clicks from the menu.
    """
    callback_data = callback_query.data

    if callback_data == "send_anonymously":
        await callback_query.answer("Please type your anonymous message:")

    elif callback_data == "connect_anonymously":
        await callback_query.answer("**Not implemented yet**")

    else:
        await callback_query.answer("Invalid option.")


@app.on_message(filters.private & ~filters.command)
async def handle_anonymous_messages(client, message):
    """
    Handle messages sent in private chats (potential anonymous messages).
    - Remove sender information (username, profile picture) before forwarding.
    """
    try:
        anonymized_message = f"**Anonymous message:**\n{message.text}"
        await client.send_message(chat_id=message.chat.id, text=anonymized_message)

        await message.reply_text("Your anonymous message has been sent.")
    except Exception as e:
        print(f"Error forwarding message: {e}")
        await message.reply_text("An error occurred while sending your message. Please try again later.")


app.run()

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

app.run()

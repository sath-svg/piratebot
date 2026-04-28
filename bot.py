import os
import json
import logging
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")
USERS_FILE = "users.json"
REMINDER_INTERVAL_HOURS = 2

PIRATE_REMINDERS = [
    "☠️ Ahoy, matey! Time to put yer eyedrops in! A pirate with dry eyes can't spot treasure on the horizon! 🏴‍☠️",
    "🦜 Squawk! The parrot says: DROP yer eyedrops in NOW, ye landlubber! Yer eyes be drier than the Sahara desert! 💧",
    "⚓ Arrr! Cap'n orders say it be time fer yer eyedrops! Don't make me walk ye off the plank, do it NOW! 🌊",
    "🗺️ X marks the spot — and that spot be yer eyeballs! Time to treasure yer peepers with some drops, pirate! 💎",
    "🏴‍☠️ Ahoy! The Jolly Roger flies high to remind ye: EYEDROPS O'CLOCK! Keep those sea-faring eyes moistened! ⚔️",
    "💀 Blimey! Two hours have passed on the seven seas! Your eyes be craving their liquid gold — eyedrops, matey! 🌊",
    "🦅 By Davy Jones' locker! A good pirate takes care of their eyes. PUT. THOSE. DROPS. IN. NOW. Arrrr! 🔭",
]

reminder_index = 0


def load_users() -> set:
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return set(json.load(f))
    return set()


def save_users(users: set):
    with open(USERS_FILE, "w") as f:
        json.dump(list(users), f)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    users = load_users()

    if chat_id not in users:
        users.add(chat_id)
        save_users(users)
        await update.message.reply_text(
            "🏴‍☠️ *Ahoy! Welcome aboard Aanoushka's PirateBot!* ⚓\n\n"
            "Ye have joined the crew! I'll be sendin' ye a reminder every *2 hours* "
            "to put yer eyedrops in, ye scallywag! 💧\n\n"
            "Yer eyes be the most precious treasure on this ship! Arrrr! ☠️\n\n"
            "Use /stop to abandon ship (disable reminders).",
            parse_mode="Markdown",
        )
        logger.info(f"New user registered: {chat_id}")
    else:
        await update.message.reply_text(
            "🦜 Arrr, ye already be part of the crew, matey! "
            "I'll keep remindin' ye to use yer eyedrops every 2 hours! 💧"
        )


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    users = load_users()

    if chat_id in users:
        users.discard(chat_id)
        save_users(users)
        await update.message.reply_text(
            "⚓ Ye have abandoned ship! No more eyedrop reminders fer ye.\n"
            "But arrr, don't forget to take care of yer eyes, matey! 🏴‍☠️\n\n"
            "Use /start to rejoin the crew anytime!"
        )
        logger.info(f"User unregistered: {chat_id}")
    else:
        await update.message.reply_text(
            "☠️ Ye weren't even on the ship, landlubber! Use /start to join the crew."
        )


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    users = load_users()

    if chat_id in users:
        await update.message.reply_text(
            f"🗺️ Arrr! Ye be an active crew member!\n"
            f"⏰ Reminders fire every *{REMINDER_INTERVAL_HOURS} hours*.\n"
            f"👥 Total crew aboard: *{len(users)}* pirates.",
            parse_mode="Markdown",
        )
    else:
        await update.message.reply_text(
            "🏴‍☠️ Ye not be registered yet! Use /start to join the crew."
        )


async def send_reminders(context: ContextTypes.DEFAULT_TYPE):
    global reminder_index
    users = load_users()

    if not users:
        logger.info("No users to remind.")
        return

    message = PIRATE_REMINDERS[reminder_index % len(PIRATE_REMINDERS)]
    reminder_index += 1

    logger.info(f"Sending reminder to {len(users)} users.")
    for chat_id in list(users):
        try:
            await context.bot.send_message(chat_id=chat_id, text=message)
        except Exception as e:
            logger.warning(f"Failed to send to {chat_id}: {e}")
            # Remove users who blocked or deleted the bot
            if "blocked" in str(e).lower() or "chat not found" in str(e).lower():
                users = load_users()
                users.discard(chat_id)
                save_users(users)
                logger.info(f"Removed unreachable user: {chat_id}")


def main():
    if not TOKEN:
        raise ValueError("BOT_TOKEN not set. Copy .env.example to .env and add your token.")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(CommandHandler("status", status))

    # Schedule reminder every 2 hours (7200 seconds)
    app.job_queue.run_repeating(
        send_reminders,
        interval=REMINDER_INTERVAL_HOURS * 3600,
        first=10,  # First reminder 10 seconds after bot starts
    )

    logger.info("🏴‍☠️ Aanoushka's PirateBot is sailing the high seas!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

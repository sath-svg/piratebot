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
REMINDER_INTERVAL_HOURS = 0.083  # ~5 minutes, for testing

PIRATE_REMINDERS = [
    # --- Classic pirate reminders ---
    "☠️ Ahoy, Nushie Sushie! EYEDROPS O'CLOCK! A pirate with dry eyes can't spot treasure on the horizon! DROP 'EM IN! 🏴‍☠️💧",
    "🦜 Squawk! The parrot says: Aanoushka, put yer eyedrops in RIGHT NOW, ye scallywag! Yer eye be drier than the Sahara! 💧",
    "⚓ Arrr! Cap'n's orders, Aanoushka — EYEDROPS NOW! Don't make me walk ye off the plank! 🌊",
    "🗺️ X marks the spot — and that spot be yer eyeball, Nushie! Treasure yer peepers with some drops! 💎",
    "🏴‍☠️ The Jolly Roger flies to remind ye, Aanoushka: two hours have passed on the seven seas! EYEDROPS IN! ⚔️",
    "💀 Blimey, Aanoushka! Yer eye be craving its liquid gold! Put those drops in before Davy Jones comes fer ye! 🌊",
    "🦅 By Davy Jones' locker, Aanoushka! A good pirate takes care of their eye. PUT. THOSE. DROPS. IN. Arrrr! 🔭",

    # --- Eye patch puns ---
    "🏴‍☠️ Nushie! Yer famous eye patch won't keep yer eye moist! Only EYEDROPS can do that! Drop 'em in NOW! 👁️💧",
    "👁️ Arrr, Aanoushka! Even the bravest one-eyed pirates need their drops! Yer one working eye deserves the best! 💧☠️",
    "🩹 Blimey, Aanoushka! That bandage be lookin' mighty fine, but the eye underneath still needs its drops! GO ON, DO IT! 👁️🏴‍☠️",
    "⚓ Ahoy! Aanoushka the One-Eyed Terror of the Seven Seas! Yer legendary eye needs its drops — PUT THEM IN NOW! 👁️💧",
    "💀 Aanoushka! Ye only have one eye on active duty — ye CANNOT afford to let it get dry! EYEDROPS IMMEDIATELY! 👁️🌊",
    "🩹 The seas be harsh, Aanoushka! Yer bandage protects one side, but only drops protect the other! DO IT! 💧🦜",
    "👁️ Arrr, Nushie! A pirate's eye patch is legendary — but a pirate's dry eye? That be a TRAGEDY! Drops in! 💧☠️",
    "🔭 Aanoushka! How can ye spot enemy ships with a DRY EYE?! One eye, one chance — DROPS NOW! 👁️🏴‍☠️",
    "🏴‍☠️ Nushie! The greatest pirates always moistened their eyes! Well... at least the smart ones did! DROPS! 👁️💧",

    # --- Muffin the dog reminders ---
    "🐶 Woof woof! Even Muffin is concerned about yer dry eye, Aanoushka! She's been staring at ye waiting for ye to put yer drops in! DO IT FOR MUFFIN! 💧🐾",
    "🦴 Arrr! Muffin fetched yer eyedrops and dropped them at yer feet, Aanoushka! The least ye can do is USE THEM! 🐶💧",
    "🐾 Shiver me timbers! Muffin has been a better pirate than ye today, Nushie — she reminded herself to nap AND drink water! Now YOU do yer eyedrops! 🐶💧",
    "🐶 Muffin says: *woof woof woof* — which in dog pirate means PUT YER EYEDROPS IN RIGHT NOW, AANOUSHKA! 🏴‍☠️💧",
    "🦴 Even Muffin knows that a good pirate takes care of their eyes, Aanoushka! She's judging ye right now. Those big puppy eyes are full of disappointment. DROPS. IN. 🐶👁️💧",

    # --- Ekansh / "Ek" = One puns ---
    "⚔️ Arrr, Aanoushka! Yer brother Ekansh means *ek* — ONE in Hindi — and ye've got EK eye available right now! Don't waste it on dryness! EYEDROPS! 👁️💧",
    "💀 Ekansh has TWO eyes and still takes care of them. Ye have *ek* eye in service, Nushie — yer own brother would be embarrassed! DROPS NOW! 👁️🏴‍☠️",
    "🏴‍☠️ *Ek* eye. ONE eye. That's all ye've got right now, Aanoushka! Even yer brother Ekansh — Mr. *Ek* himself — would tell ye to put yer drops in! 💧👁️",
    "🦜 Squawk! Even yer younger brother Ekansh called from across the seven seas — little *ek* says: \"Nushie, *ek* aankhon ka khayal rakho!\" Take care of yer ONE eye! DROPS! 👁️💧",
    "⚓ Arrr! Ek means ONE, Aanoushka! Like yer one unbandaged eye! Like the ONE thing yer little brother Ekansh has been telling ye to do — EYEDROPS! 💧👁️",

    # --- Funny/dramatic ---
    "🌊 AANOUSHKA! The ocean herself is CRYING for ye to put yer eyedrops in! Don't make the ocean sad! 💧😭",
    "🦜 Squawk! Nushie Sushie hasn't put her eyedrops in! SQUAWK! Muffin knows! The whole crew knows! PUT THEM IN! SQUAWK! 🦜🐶💧",
    "💀 The ghost of every pirate who forgot their eyedrops is haunting me, Nushie. Don't join them. DROPS. NOW. 👻💧",
    "⚓ Aanoushka! I've checked the ship's log — it's been 2 hours since yer last eyedrops! This is a MARITIME EMERGENCY! 🚨💧",
    "🏴‍☠️ AANOUSHKA! If ye were on my ship and forgot yer eyedrops, ye'd be scrubbin' the poop deck for a WEEK! DROP 'EM IN! 💧☠️",
    "☠️ Aanoushka, ye mighty pirate queen! Muffin is watching, little Ekansh is watching, and I am watching. PUT THOSE EYEDROPS IN. NOW. 👑💧🐶",
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

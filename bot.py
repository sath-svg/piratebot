import os
import json
import logging
import random
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
IMAGES_DIR = os.path.join(os.path.dirname(__file__), "images")
IMAGE_FILES = [
    os.path.join(IMAGES_DIR, f)
    for f in os.listdir(IMAGES_DIR)
    if f.lower().endswith((".jpg", ".jpeg", ".png", ".gif"))
] if os.path.isdir(IMAGES_DIR) else []

PIRATE_REMINDERS = [
    # --- Lawyer ---
    "⚖️ Objection, yer honour! My client Aanoushka has FAILED to apply eyedrops within the 2-hour statute of limitations! The prosecution rests. PUT 'EM IN, NUSHIE!",
    "📜 As yer legal counsel, I hereby serve ye notice: failure to apply eyedrops constitutes negligence of the highest order. Ye have no defence. EYEDROPS NOW, COUNSELLOR!",
    "⚖️ Arraignment time, Aanoushka! ONE count of eyedrop neglect. TWO hours without moisture. THREE degrees of dryness. How do ye plead? GUILTY. Sentence: eyedrops, immediately, no appeals!",
    "📜 Blimey! Motion to compel Aanoushka to administer eyedrops — GRANTED. Do it NOW, Nushie. The court will not repeat itself.",
    "⚖️ Sustained! The pirate court finds ye guilty of chronic eye dryness. Sentence: eyedrops, applied immediately. No appeals. No continuances. DO IT.",
    "📜 Pro bono advice from yer pirate lawyer: dry eyes be a tort waiting to happen. Apply eyedrops NOW before I file suit against ye for self-neglect!",
    "⚖️ Counsel, approach the bench. The bench has reviewed yer eye hydration records. The bench is NOT pleased. EYEDROPS, administered immediately, in the presence of the court.",
    "☠️ Ye argue cases for a living, Nushie Sushie. Ye cannot argue with DRY EYES. The only remedy: EYEDROPS. Motion carries. Court dismissed.",

    # --- Muffin (good boy, male) ---
    "🐶 Muffin reporting live from the sofa. He ate his dinner on time. He drank his water on time. He is a GOOD BOY. Be more like Muffin. EYEDROPS NOW.",
    "🦴 Muffin has fetched yer eyedrops, Nushie. He dropped them at yer feet. He is staring at ye with his big boy eyes. Don't make him sad. PUT THEM IN.",
    "🐶 MUFFIN BULLETIN: He just barked twice. That means 'eyedrops, ye scurvy human.' He will not stop barking. He NEVER stops. Only remedy: comply.",
    "🦴 Muffin: fed. Muffin: walked. Muffin: loved. Aanoushka's eyes: parched and neglected. One of these things is wrong. FIX IT.",
    "🐶 Arrr! Muffin be a loyal first mate and he DEMANDS ye moisturise yer peepers. He sat. He stayed. He fetched. NOW YE DROP. EYEDROPS, NUSHIE!",
    "🦴 Muffin filed a legal brief. A PROPER legal brief. He paw-signed it. Requesting immediate eyedrop administration. The court accepted it. COMPLY, COUNSELLOR.",
    "🐶 Muffin is watching ye, Aanoushka. He has no concept of the law. He has no concept of pirate ships. But he KNOWS ye haven't done yer drops. Good boys always know. DO IT.",

    # --- Ekansh / EGGYBOI ---
    "⚔️ Ekansh = Ek = ONE in Hindi. Ye have TWO eyes and tend to NONE. ONE drop per eye, RIGHT NOW, Aanoushka — for Ek!",
    "🏴‍☠️ Yer brother Ekansh called. He said — and I quote — 'has she done her drops?' He KNEW. Brothers always know. Don't embarrass yerself. DO IT.",
    "⚔️ Ekansh manages to live his whole life as EK — ONE — without complaint. Ye have two eyes and can't water them twice a day. Disgraceful. EYEDROPS. NOW.",
    "🦜 Squawk! Ekansh be ek — the ONE sibling with common sense! He would NEVER forget if he had yer condition. Put 'em IN, Nushie! Honour yer family!",
    "⚔️ Ek-ansh. ONE part. ONE eye's worth of sense between ye. That one part says: EYEDROPS. Listen to Ek. He knows things. DROPS IN, NUSHIE!",
    "🥚 Arrr! Even EGGYBOI 🥚 — the one, the only, the legendary Ekansh — is rooting for ye to remember yer drops! He believes in ye, Nushie! DON'T LET EK DOWN! DON'T LET EGGYBOI DOWN!",

    # --- Foxy (boot protector) ---
    "🦊 Foxy the boot protector has ONE job: protect the boots. Foxy does it EVERY SINGLE DAY without fail. Ye have one job: eyedrops. Ye forget every 2 hours. Foxy judges ye, Aanoushka.",
    "🦊 Cap'n Foxy's Log, Day 47: still guarding the boots. Still doing the job. Still watching Nushie forget her eyedrops. Foxy is tired. Foxy is SAD. DROPS. NOW. For Foxy.",
    "🦊 Foxy sits on yer boots every day keeping them safe — rain, mud, scuff, all of it. Foxy never takes a break. Foxy never forgets. A BOOT PROTECTOR has more discipline than ye. DO IT.",
    "🦊 FOXY SPEAKS: 'I protect the boots. I ask nothing in return. I ask ONE thing: eyedrops. Please, Aanoushka. For the boots. For me. For us all.' — Foxy 🦊",
    "🦊 Foxy guards yer boots faithfully, Nushie Sushie. Yer boots are safe. Yer feet are safe. Yer EYES meanwhile are PARCHED and unprotected. Foxy cannot protect eyes. Only ye can. DO IT.",
    "🦊 Foxy's full report on Aanoushka's eyedrop compliance: 'No.' Boots: protected. Eyes: dry and abandoned. Fix yer priorities. PUT THE DROPS IN.",

    # --- Broken shoulder ---
    "☠️ Arrr! Even with a BROKEN SHOULDER, yer faithful messenger has fought through the pain to send ye this reminder. The LEAST ye can do is put yer eyedrops in. THE LEAST.",
    "🏴‍☠️ One shoulder: broken. One mission: remind Aanoushka about eyedrops. Sacrifice accepted. Do NOT make this suffering be in vain. EYEDROPS. NOW. Honour the shoulder.",
    "⚓ A pirate with a BROKEN SHOULDER still sends ye reminders. A lawyer with two working arms cannot manage eyedrops. The court notes this irony. FIX IT.",
    "☠️ Typing this with one good arm because the other be BROKEN, Nushie. Ye BETTER put yer eyedrops in or this sacrifice means NOTHING. I HAVE ONE ARM. DO IT.",
    "🦜 SQUAWK! Broken shoulder pirate here! Still sending reminders! Much pain! Very dedication! Ye owe me ONE eyedrop application RIGHT NOW, Aanoushka!",
    "⚓ One broken shoulder. Infinite dedication to yer eye health. Ye have zero broken shoulders and zero reasons not to put yer drops in. DO IT NOW, NUSHIE.",

    # --- Crossover ---
    "🏴‍☠️ Ship's council vote: Muffin — eyedrops NOW. Eggyboi Ekansh 🥚 — eyedrops NOW. Foxy the boot protector — eyedrops NOW. Motion CARRIED. Three to zero. Comply immediately, Cap'n Nushie.",
    "⚖️ People vs. Aanoushka's Eyedrops. Exhibit A: Muffin looking sad. Exhibit B: two parched eyes. Verdict: GUILTY. Sentence: eyedrops, immediate. No further argument accepted.",
    "🦊 Foxy and Eggyboi Ekansh 🥚 have formed an alliance. Combined IQ: enormous. Combined patience for Nushie's eyedrop delays: ZERO. They both say: DO IT NOW.",
    "⚖️ As yer legal rep AND boot-protection consultant — Foxy handles the boot side — we jointly advise: the statute of eye dryness has EXPIRED. EYEDROPS. No further correspondence will be entered into.",
    "🦴 Muffin fetched the drops. Eggyboi Ekansh 🥚 held the door open. Foxy guarded the boots. Broken shoulder pirate sent this message. EVERYTHING IS IN PLACE, AANOUSHKA. PUT. THEM. IN.",

    # --- Classic pirate / dramatic ---
    "💀 Two hours. In that time, empires rose, ships sailed, Muffin probably ate something he shouldn't. But no eyedrops from Nushie Sushie. CORRECT THIS IMMEDIATELY.",
    "🌊 The seven seas weep for ye, Aanoushka! The ocean herself — moistest thing alive — is EMBARRASSED by yer dry eyes. FIX IT. Now.",
    "☠️ EMERGENCY BROADCAST: Aanoushka's eyes have filed a formal complaint. They are dry, neglected, and considering leaving her face. Remedy: EYEDROPS. NOW.",
    "🦜 The parrot has learned one phrase: 'Nushie, eyedrops!' It screams this constantly. The ONLY way to silence it: COMPLY. Put the drops in.",
    "💀 Every minute without eyedrops, another pirate ghost materialises on this ship. There be fourteen of 'em now, Aanoushka. ALL staring at ye. DROPS.",
    "🏴‍☠️ Avast! Yer eyes be drier than the Sahara, crustier than old hardtack, and sadder than a pirate with no rum. EYEDROPS. IMMEDIATE. No excuses.",
    "⚓ Ship's log: last eyedrops 2 hours ago. The crew is restless. The parrot is screaming. Muffin is whimpering. Foxy is judging. EVERYONE needs ye to put the drops in.",
    "☠️ Yer eyes have called a press conference. Statement: 'We are dry. We are tired. Our human is a LAWYER and STILL argues against us.' Drop the case. DROP THE DROPS. NOW.",
    "💀 Davy Jones checked his locker. It is MOISTER than Aanoushka's eyes. He is personally offended. He demands immediate remediation. EYEDROPS, NUSHIE. For Davy.",
    "🏴‍☠️ The Jolly Roger flies at half-mast. Not for a fallen pirate. For yer DRY EYES, Nushie Sushie. Raise the flag by raising the drops. INTO YER EYEBALLS. NOW.",
    "⚓ I've sent this reminder across seas, through storms, with a broken shoulder. Ye have a bottle of eyedrops within arm's reach. ONE of us is putting in effort. IT'S NOT YE.",
    "🌊 AANOUSHKA! The ocean herself weeps enough to hydrate everyone EXCEPT ye! Yer own eyes be the driest spot on earth! UNACCEPTABLE! DROPS! NOW! ALWAYS!",
    "☠️ X marks the spot — it's yer eyeball, Nushie. That be where the treasure goes. The LIQUID treasure. In the BOTTLE. Into YER EYE. This is not complicated. DO IT.",
    "💀 Scientists confirm: Aanoushka's eyes can survive 2 hours without drops. They do NOT recommend it. They are tired of confirming it. SO VERY TIRED. DROPS. NOW.",
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
    send_image = IMAGE_FILES and (reminder_index % 12 == 1)
    image_path = random.choice(IMAGE_FILES) if send_image else None

    for chat_id in list(users):
        try:
            if image_path:
                with open(image_path, "rb") as photo:
                    await context.bot.send_photo(chat_id=chat_id, photo=photo, caption=message)
            else:
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

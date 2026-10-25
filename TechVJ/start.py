

import os
import asyncio 
import pyrogram
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, UserAlreadyParticipant, InviteHashExpired, UsernameNotOccupied
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery 
from config import API_ID, API_HASH, ERROR_MESSAGE, LOGIN_SYSTEM, STRING_SESSION, CHANNEL_ID, WAITING_TIME, ADMINS, ADMIN_USERNAME
from database.db import db
from TechVJ.strings import HELP_TXT
from bot import TechVJUser
import datetime

class batch_temp(object):
    IS_BATCH = {}
    UPLOADED_SIZE = {}

# File size readable format function
def get_readable_file_size(size_bytes):
    if size_bytes == 0:
        return "0 MiB"
    units = ["B", "KiB", "MiB", "GiB", "TiB"]
    i = 0
    while size_bytes >= 1024 and i < len(units) - 1:
        size_bytes /= 1024.0
        i += 1
    return f"{size_bytes:.2f} {units[i]}"

# Plan Limits Helper Function
def get_plan_limits(plan):
    plan = plan.lower()
    if plan == "free":
        return {"max_files": 40, "max_size_mb": 40, "max_total_mb": 500}
    elif plan == "basic":
        return {"max_files": 100, "max_size_mb": 100, "max_total_mb": 1500}
    elif plan == "standard":
        return {"max_files": 300, "max_size_mb": 500, "max_total_mb": 5000}
    elif plan == "pro":
        return {"max_files": "Unlimited", "max_size_mb": 4000, "max_total_mb": "Unlimited"}
    else:
        return {"max_files": 40, "max_size_mb": 40, "max_total_mb": 500}

# Cancel Callback Handler
@Client.on_callback_query(filters.regex("cancel_process"))
async def cancel_process_callback(client, callback_query):
    user_id = callback_query.from_user.id
    batch_temp.IS_BATCH[user_id] = True
    await callback_query.answer("Process Cancelled Successfully!", show_alert=True)
    try:
        await callback_query.message.edit_text("**❌ Process Cancelled by User.**")
    except:
        pass


# ==================== SETTINGS & INLINE BUTTON HANDLERS ====================
@Client.on_message(filters.command("settings") & filters.private)
async def settings_command(client: Client, message: Message):
    buttons = [
        [InlineKeyboardButton("LOGIN", callback_data="set_login"), InlineKeyboardButton("LOGOUT", callback_data="set_logout")],
        [InlineKeyboardButton("SET CHANNEL", callback_data="set_chat"), InlineKeyboardButton("REMOVE CHANNEL", callback_data="rem_chat")],
        [InlineKeyboardButton("ADD CAPTION", callback_data="set_cap"), InlineKeyboardButton("REMOVE CAPTION", callback_data="rem_cap")],
        [InlineKeyboardButton("SET THUMB", callback_data="set_thb"), InlineKeyboardButton("REMOVE THUMB", callback_data="rem_thb")],
        [InlineKeyboardButton("SET ARTIST", callback_data="set_art"), InlineKeyboardButton("REMOVE ARTIST", callback_data="rem_art")],
        [InlineKeyboardButton("« BACK", callback_data="back_home")]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    await message.reply_text(
        "<b>CUSTOMIZE YOUR SETTINGS AS PER YOUR NEEDS.</b>",
        reply_markup=reply_markup,
        reply_to_message_id=message.id
    )

@Client.on_callback_query(filters.regex("open_settings"))
async def open_settings_callback(client: Client, query: CallbackQuery):
    buttons = [
        [InlineKeyboardButton("LOGIN", callback_data="set_login"), InlineKeyboardButton("LOGOUT", callback_data="set_logout")],
        [InlineKeyboardButton("SET CHANNEL", callback_data="set_chat"), InlineKeyboardButton("REMOVE CHANNEL", callback_data="rem_chat")],
        [InlineKeyboardButton("ADD CAPTION", callback_data="set_cap"), InlineKeyboardButton("REMOVE CAPTION", callback_data="rem_cap")],
        [InlineKeyboardButton("SET THUMB", callback_data="set_thb"), InlineKeyboardButton("REMOVE THUMB", callback_data="rem_thb")],
        [InlineKeyboardButton("SET ARTIST", callback_data="set_art"), InlineKeyboardButton("REMOVE ARTIST", callback_data="rem_art")],
        [InlineKeyboardButton("« BACK", callback_data="back_home")]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    try:
        await query.message.edit_text(
            "<b>CUSTOMIZE YOUR SETTINGS AS PER YOUR NEEDS.</b>",
            reply_markup=reply_markup
        )
    except:
        await query.message.reply_text(
            "<b>CUSTOMIZE YOUR SETTINGS AS PER YOUR NEEDS.</b>",
            reply_markup=reply_markup
        )
    await query.answer()

@Client.on_callback_query(filters.regex("back_home"))
async def back_home_callback(client: Client, query: CallbackQuery):
    buttons = [
        [InlineKeyboardButton("SETTINGS", callback_data="open_settings"), InlineKeyboardButton("DEVELOPER", url="https://t.me/kingvj01")],
        [InlineKeyboardButton('🔍 ꜱᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ', url='https://t.me/vj_bot_disscussion'), InlineKeyboardButton('🤖 ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ', url='https://t.me/vj_bots')]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    try:
        await query.message.edit_text(
            f"<b>👋 Hi {query.from_user.mention}, I am Save Restricted Content Bot, I can send you restricted content by its post link.\n\nFor downloading restricted content /login first.\n\nKnow how to use bot by - /help</b>",
            reply_markup=reply_markup
        )
    except:
        pass
    await query.answer()

@Client.on_callback_query(filters.regex("^(set_|rem_)"))
async def settings_callback(client: Client, query: CallbackQuery):
    data = query.data
    user_id = query.from_user.id
    if data == "set_login":
        await query.message.reply_text("Please use `/login <session_string>` command to login.")
    elif data == "set_logout":
        await db.remove_session(user_id)
        await query.answer("Successfully Logged Out!", show_alert=True)
    elif data == "set_chat":
        await query.message.reply_text("Please use `/setchat <chat_id>` to set your channel.")
    elif data == "rem_chat":
        await db.set_chat(user_id, None)
        await query.answer("Channel Removed!", show_alert=True)
    elif data == "set_cap":
        await query.message.reply_text("Please use `/set_caption <your_caption>` to set custom caption.")
    elif data == "rem_cap":
        await db.set_caption(user_id, None)
        await query.answer("Caption Removed!", show_alert=True)
    elif data == "set_thb":
        await query.message.reply_text("Please reply to an image with `/set_thumb` to set your thumbnail.")
    elif data == "rem_thb":
        await db.set_thumbnail(user_id, None)
        await query.answer("Thumbnail Removed!", show_alert=True)
    elif data == "set_art":
        await query.message.reply_text("Please use `/set_artist <artist_name>` to set your custom artist.")
    elif data == "rem_art":
        await db.set_artist(user_id, None)
        await query.answer("Custom Artist Removed!", show_alert=True)
    await query.answer()


# ==================== PLAN & SUBSCRIPTION COMMANDS ====================
@Client.on_message(filters.command("myplan") & filters.private)
async def my_plan_command(client: Client, message: Message):
    user_id = message.from_user.id
    user = await db.get_user_data(user_id)
    if not user:
        await db.add_user(user_id, message.from_user.first_name)
        user = await db.get_user_data(user_id)
    
    plan = user.get('plan', 'free').upper()
    limits = get_plan_limits(plan)
    
    expiry = user.get('plan_expiry', 0)
    daily_files = user.get('daily_files', 0)
    used_bytes = user.get('used_bytes', 0)
    used_mb = used_bytes / (1024 * 1024)
    
    expiry_str = "Lifetime / Unlimited"
    if expiry > 0:
        expiry_str = datetime.datetime.fromtimestamp(expiry).strftime('%Y-%m-%d %H:%M:%S')

    max_files_str = str(limits["max_files"]) if limits["max_files"] != "Unlimited" else "Unlimited"
    max_data_str = f"{limits['max_total_mb']} MB" if limits["max_total_mb"] != "Unlimited" else "Unlimited"
    
    left_files_str = f"{limits['max_files'] - daily_files}" if limits["max_files"] != "Unlimited" else "Unlimited"

    text = (
        f"<b>📦 Your Subscription & Usage Details:</b>\n\n"
        f"🔹 <b>Current Plan:</b> {plan}\n"
        f"📅 <b>Expiry:</b> {expiry_str}\n\n"
        f"📂 <b>Files Used Today:</b> {daily_files} of {max_files_str}\n"
        f"✨ <b>Files Left Today:</b> {left_files_str}\n"
        f"📊 <b>Data Used:</b> {used_mb:.2f} MB of {max_data_str}\n"
        f"📏 <b>Max File Size Limit:</b> {limits['max_size_mb']} MB per file\n\n"
        f"<i>Want to upgrade your plan? Click the button below to contact Admin!</i>"
    )
    
    buttons = [
        [InlineKeyboardButton("💬 Contact Admin to Buy Plan", url=f"https://t.me/{ADMIN_USERNAME}")]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    await message.reply_text(text, reply_markup=reply_markup)


@Client.on_message(filters.command("plans") & filters.private)
async def plans_command(client: Client, message: Message):
    text = (
        "<b>💎 Available Subscription Plans:</b>\n\n"
        "1️⃣ <b>FREE PLAN</b>\n"
        "• Daily Files: 40 files/day\n"
        "• Max File Size: 40 MB per file\n"
        "• Total Data Limit: 500 MB\n"
        "• Price: Free\n\n"
        "2️⃣ <b>BASIC PLAN</b>\n"
        "• Daily Files: 100 files/day\n"
        "• Max File Size: 100 MB per file\n"
        "• Total Data Limit: 1,500 MB (1.5 GB)\n"
        "• Validity: 7 Days\n"
        "• Price: <b>₹65</b>\n\n"
        "3️⃣ <b>STANDARD PLAN</b>\n"
        "• Daily Files: 300 files/day\n"
        "• Max File Size: 500 MB per file\n"
        "• Total Data Limit: 5,000 MB (5 GB)\n"
        "• Validity: 15 Days\n"
        "• Price: <b>₹150</b>\n\n"
        "4️⃣ <b>PRO PLAN (UNLIMITED)</b>\n"
        "• Daily Files: <b>Unlimited</b>\n"
        "• Max File Size: <b>Unlimited</b> (Telegram Limit)\n"
        "• Total Data Limit: <b>Unlimited</b>\n"
        "• Validity: 30 Days (1 Month)\n"
        "• Price: <b>₹300</b>\n\n"
        "<i>Want to buy or upgrade a plan? Click the button below to contact Admin!</i>"
    )
    
    buttons = [
        [InlineKeyboardButton("💬 Contact Admin to Buy Plan", url=f"https://t.me/{ADMIN_USERNAME}")]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    await message.reply_text(text, reply_markup=reply_markup)


@Client.on_message(filters.command("setplan") & filters.private)
async def set_plan_admin(client: Client, message: Message):
    if message.from_user.id != ADMINS:
        return await message.reply("❌ You are not authorized to use this command!")
    
    if len(message.command) < 3:
        return await message.reply("Usage: `/setplan <user_id> <free/basic/standard/pro>`")
    
    try:
        target_user_id = int(message.command[1])
        plan_type = message.command[2].lower()
    except ValueError:
        return await message.reply("❌ Invalid User ID!")

    if plan_type not in ["free", "basic", "standard", "pro"]:
        return await message.reply("❌ Invalid plan! Choose: free, basic, standard, pro")

    if plan_type == "basic":
        validity = 7 * 86400
        price = "₹65 (7 Days)"
    elif plan_type == "standard":
        validity = 15 * 86400
        price = "₹150 (15 Days)"
    elif plan_type == "pro":
        validity = 30 * 86400
        price = "₹300 (30 Days / 1 Month)"
    else:
        validity = 0
        price = "Free"

    await db.set_user_plan(target_user_id, plan_type, validity)
    await message.reply(f"✅ Successfully set plan **{plan_type.upper()}** for user `{target_user_id}`!")
    
    try:
        await client.send_message(
            target_user_id,
            f"🎉 **Congratulations! Your plan has been upgraded.**\n\n"
            f"🔹 **New Plan:** {plan_type.upper()}\n"
            f"💰 **Package:** {price}\n\n"
            f"Enjoy your enhanced limits! Check /myplan for details."
        )
    except:
        pass


# ==================== THUMBNAIL, CAPTION & ARTIST COMMANDS ====================
@Client.on_message(filters.command("set_thumb") & filters.private)
async def set_thumb(client, message):
    if not message.reply_to_message or not message.reply_to_message.photo:
        return await message.reply("Please reply to an image to set thumbnail!")
    file_id = message.reply_to_message.photo.file_id
    await db.set_thumbnail(message.from_user.id, file_id)
    await message.reply("Thumbnail Saved Successfully!")

@Client.on_message(filters.command("view_thumb") & filters.private)
async def view_thumb(client, message):
    thumb = await db.get_thumbnail(message.from_user.id)
    if not thumb:
        return await message.reply("You haven't set any thumbnail yet.")
    await client.send_photo(message.chat.id, thumb, caption="Your Current Thumbnail")

@Client.on_message(filters.command("del_thumb") & filters.private)
async def del_thumb(client, message):
    await db.set_thumbnail(message.from_user.id, None)
    await message.reply("Thumbnail Deleted Successfully!")


@Client.on_message(filters.command("set_caption") & filters.private)
async def set_caption(client, message):
    if len(message.command) < 2:
        return await message.reply("Usage: `/set_caption Your Custom Caption`")
    caption = message.text.split(" ", 1)[1]
    await db.set_caption(message.from_user.id, caption)
    await message.reply("Custom Caption Saved Successfully!")

@Client.on_message(filters.command("see_caption") & filters.private)
async def see_caption(client, message):
    caption = await db.get_caption(message.from_user.id)
    if not caption:
        return await message.reply("You haven't set any custom caption yet.")
    await message.reply(f"Your Caption:\n\n{caption}")

@Client.on_message(filters.command("del_caption") & filters.private)
async def del_caption(client, message):
    await db.set_caption(message.from_user.id, None)
    await message.reply("Custom Caption Deleted Successfully!")


@Client.on_message(filters.command("set_artist") & filters.private)
async def set_artist_cmd(client, message):
    if len(message.command) < 2:
        return await message.reply("Usage: `/set_artist Your Artist Name`")
    artist_name = message.text.split(" ", 1)[1]
    await db.set_artist(message.from_user.id, artist_name)
    await message.reply(f"Custom Artist Saved Successfully: <b>{artist_name}</b>")

@Client.on_message(filters.command("del_artist") & filters.private)
async def del_artist_cmd(client, message):
    await db.set_artist(message.from_user.id, None)
    await message.reply("Custom Artist Deleted Successfully!")


@Client.on_message(filters.command("setchat") & filters.private)
async def set_chat(client, message):
    if len(message.command) < 2:
        return await message.reply("Usage: `/setchat -100xxxxxxxxxx`")
    try:
        chat_id = int(message.command[1])
        await db.set_chat(message.from_user.id, chat_id)
        await message.reply("Target Channel Saved Successfully!")
    except ValueError:
        await message.reply("Invalid Chat ID!")

@Client.on_message(filters.command("remchat") & filters.private)
async def rem_chat(client, message):
    await db.set_chat(message.from_user.id, None)
    await message.reply("Target Channel Removed!")


# ==================== START & BATCH HANDLERS ====================
@Client.on_message(filters.command(["start", "dlbot"]))
async def send_start(client: Client, message: Message):
    await db.add_user(message.from_user.id, message.from_user.first_name)
    
    if len(message.command) > 1:
        extracted_link = message.command[1]
        if "t.me/" in extracted_link:
            message.text = extracted_link
            return await save(client, message)

    buttons = [
        [InlineKeyboardButton("SETTINGS", callback_data="open_settings"), InlineKeyboardButton("DEVELOPER", url="https://t.me/kingvj01")],
        [InlineKeyboardButton('🔍 ꜱᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ', url='https://t.me/vj_bot_disscussion'), InlineKeyboardButton('🤖 ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ', url='https://t.me/vj_bots')]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    await client.send_message(
        chat_id=message.chat.id, 
        text=f"<b>👋 Hi {message.from_user.mention}, I am Save Restricted Content Bot, I can send you restricted content by its post link.\n\nFor downloading restricted content /login first.\n\nKnow how to use bot by - /help</b>", 
        reply_markup=reply_markup, 
        reply_to_message_id=message.id
    )
    return


@Client.on_message(filters.command(["help"]))
async def send_help(client: Client, message: Message):
    await client.send_message(chat_id=message.chat.id, text=f"{HELP_TXT}")


@Client.on_message(filters.command(["cancel"]))
async def send_cancel(client: Client, message: Message):
    batch_temp.IS_BATCH[message.from_user.id] = True
    await client.send_message(chat_id=message.chat.id, text="**Batch Successfully Cancelled.**")


@Client.on_message(filters.command("batch") & filters.private)
async def batch_command(client: Client, message: Message):
    await db.add_user(message.from_user.id, message.from_user.first_name)

    if batch_temp.IS_BATCH.get(message.from_user.id) == False:
        return await message.reply_text("**One Task Is Already Processing. Wait For Complete It. If You Want To Cancel This Task Then Use - /cancel**")

    try:
        first_msg = await client.ask(
            chat_id=message.chat.id,
            text="<b>📦 Batch Save - Step 1 of 2\n\nSend the link of the first message you want to save.\n\nSend /cancel to stop.</b>",
            filters=filters.text,
            timeout=120
        )
        if first_msg.text == "/cancel":
            return await first_msg.reply("<b>Batch cancelled.</b>")
        
        first_link = first_msg.text.strip()
        if "t.me/" not in first_link:
            return await first_msg.reply("<b>Invalid link provided. Please start again with /batch</b>")

        second_msg = await client.ask(
            chat_id=message.chat.id,
            text="<b>📦 Batch Save - Step 2 of 2\n\nNow tell me where to stop:\n\n• Paste the link of the last message\n• Or just send how many files you want (e.g. 50)\n\nSend /cancel to stop.</b>",
            filters=filters.text,
            timeout=120
        )
        if second_msg.text == "/cancel":
            return await second_msg.reply("<b>Batch cancelled.</b>")

        second_input = second_msg.text.strip()

        if "t.me/" in second_input:
            datas_first = first_link.split("/")
            datas_second = second_input.split("/")
            fromID = int(datas_first[-1].replace("?single", "").strip())
            toID = int(datas_second[-1].replace("?single", "").strip())
            
            if fromID > toID:
                fromID, toID = toID, fromID
            link_template = first_link
        else:
            try:
                count = int(second_input)
            except ValueError:
                return await second_msg.reply("<b>Invalid input. Please enter a valid number or link.</b>")
            
            datas_first = first_link.split("/")
            fromID = int(datas_first[-1].replace("?single", "").strip())
            toID = fromID + count - 1
            link_template = first_link

        await process_batch_range(client, message, link_template, fromID, toID)

    except asyncio.exceptions.TimeoutError:
        await message.reply("<b>Time expired. Batch process cancelled.</b>")
    except Exception as e:
        await message.reply(f"<b>Error: {e}</b>")


@Client.on_message(filters.text & filters.private)
async def save(client: Client, message: Message):
    if ("https://t.me/+" in message.text or "https://t.me/joinchat/" in message.text) and LOGIN_SYSTEM == False:
        if TechVJUser is None:
            await client.send_message(message.chat.id, "String Session is not Set", reply_to_message_id=message.id)
            return
        try:
            await TechVJUser.join_chat(message.text)
            await client.send_message(message.chat.id, "Chat Joined", reply_to_message_id=message.id)
        except UserAlreadyParticipant:
            await client.send_message(message.chat.id, "Chat already Joined", reply_to_message_id=message.id)
        except InviteHashExpired:
            await client.send_message(message.chat.id, "Invalid Link", reply_to_message_id=message.id)
        return
    
    if "https://t.me/" in message.text:
        if batch_temp.IS_BATCH.get(message.from_user.id) == False:
            return await message.reply_text("**One Task Is Already Processing. Wait For Complete It. If You Want To Cancel This Task Then Use - /cancel**")
        
        if "?start=" in message.text:
            if LOGIN_SYSTEM == True:
                user_data = await db.get_session(message.from_user.id)
                if user_data is None:
                    await message.reply("**For Downloading Restricted Content You Have To /login First.**")
                    return
                api_id = int(await db.get_api_id(message.from_user.id))
                api_hash = await db.get_api_hash(message.from_user.id)
                try:
                    acc = Client("saverestricted", session_string=user_data, api_hash=api_hash, api_id=api_id)
                    await acc.connect()
                except:
                    return await message.reply("**Your Login Session Expired. So /logout First Then Login Again By - /login**")
            else:
                acc = TechVJUser

            batch_temp.IS_BATCH[message.from_user.id] = False
            batch_temp.UPLOADED_SIZE[message.from_user.id] = 0
            
            try:
                try:
                    count_msg = await client.ask(
                        chat_id=message.chat.id,
                        text="<b>Is link mein total kitni files hain?\n\n• Sirf number bhejiye (jaise: 20) agar limit pata ho.\n• Ya 'skip' / 0 bhejiye agar bot khud auto-collect kare.\n\n(Process cancel karne ke liye /cancel bhejein)</b>",
                        filters=filters.text,
                        timeout=60
                    )
                    if count_msg.text.strip().lower() == "/cancel":
                        await count_msg.reply("<b>Process cancelled !</b>")
                        if LOGIN_SYSTEM == True:
                            try: await acc.disconnect()
                            except: pass
                        batch_temp.IS_BATCH[message.from_user.id] = True
                        return
                    
                    user_input = count_msg.text.strip().lower()
                    if user_input in ["skip", "0"]:
                        use_auto_collect = True
                        total_expected = 0
                    else:
                        try:
                            total_expected = int(user_input)
                            use_auto_collect = False
                        except ValueError:
                            use_auto_collect = True
                            total_expected = 0

                except asyncio.exceptions.TimeoutError:
                    await message.reply("**Time expired. Process cancelled.**")
                    if LOGIN_SYSTEM == True:
                        try: await acc.disconnect()
                        except: pass
                    batch_temp.IS_BATCH[message.from_user.id] = True
                    return

                parts = message.text.split("t.me/")
                bot_and_params = parts[1].split("?start=")
                bot_username = bot_and_params[0].strip("/")
                payload = bot_and_params[1]

                cancel_markup = InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="cancel_process")]])
                status_msg = await message.reply_text(
                    f"🔍 **Initializing Process...** Please wait.",
                    reply_markup=cancel_markup
                )
                
                last_msg_id = 0
                async for m in acc.get_chat_history(bot_username, limit=1):
                    last_msg_id = m.id
                    break

                await acc.send_message(bot_username, f"/start {payload}")
                
                media_msgs = []
                seen_ids = set()
                
                if use_auto_collect:
                    no_new_files_count = 0
                    while True:
                        if batch_temp.IS_BATCH.get(message.from_user.id): break
                        
                        previous_len = len(media_msgs)
                        async for msg in acc.get_chat_history(bot_username, limit=30):
                            if msg.id <= last_msg_id:
                                break
                            if msg.id in seen_ids:
                                continue
                            if msg.media:
                                seen_ids.add(msg.id)
                                media_msgs.append(msg)
                        
                        try:
                            await status_msg.edit_text(
                                f"🔍 **Auto-Collecting...**\n📦 **Files Found:** {len(media_msgs)}\n🔄 **Status:** Waiting for bot to finish...",
                                reply_markup=cancel_markup
                            )
                        except:
                            pass

                        if len(media_msgs) == previous_len:
                            no_new_files_count += 1
                            if no_new_files_count >= 4:
                                break
                        else:
                            no_new_files_count = 0

                        await asyncio.sleep(2)
                else:
                    for _ in range(40):
                        await asyncio.sleep(2)
                        async for msg in acc.get_chat_history(bot_username, limit=50):
                            if msg.id <= last_msg_id:
                                break
                            if msg.id in seen_ids:
                                continue
                            if msg.media:
                                seen_ids.add(msg.id)
                                media_msgs.append(msg)
                        
                        try:
                            await status_msg.edit_text(
                                f"📥 **Downloading:** Collected {len(media_msgs)} of {total_expected}\n✅ **Success:** 0\n❌ **Failed:** 0\n🔄 **Running:** Fetching...",
                                reply_markup=cancel_markup
                            )
                        except:
                            pass
                            
                        if len(media_msgs) >= total_expected:
                            break
                    media_msgs = media_msgs[:total_expected]
                
                media_msgs.sort(key=lambda x: x.id)
                total_files = len(media_msgs)
                
                if total_files == 0:
                    await status_msg.edit_text("**No files found or bot didn't respond.**")
                    if LOGIN_SYSTEM == True:
                        try: await acc.disconnect()
                        except: pass
                    batch_temp.IS_BATCH[message.from_user.id] = True
                    return

                await status_msg.edit_text(f"✨ **Ready! Total Files:** {total_files}\nStarting delivery...")
                await asyncio.sleep(1.5)

                success_count = 0
                failed_count = 0

                for idx, msg in enumerate(media_msgs, start=1):
                    if batch_temp.IS_BATCH.get(message.from_user.id): 
                        break
                    
                    try:
                        await handle_private(client, acc, message, bot_username, msg.id, status_msg, cancel_markup, idx, total_files, success_count, failed_count)
                        success_count += 1
                    except Exception as e:
                        failed_count += 1
                        if ERROR_MESSAGE == True:
                            await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
                    
                    if idx < total_files and WAITING_TIME > 0:
                        for remaining in range(int(WAITING_TIME), 0, -1):
                            if batch_temp.IS_BATCH.get(message.from_user.id): break
                            try:
                                await status_msg.edit_text(
                                    f"📥 **Downloading:** {idx} of {total_files}\n✅ **Success:** {success_count}\n❌ **Failed:** {failed_count}\n⏳ **Sleeping For:** {remaining} Sec..",
                                    reply_markup=cancel_markup
                                )
                            except:
                                pass
                            await asyncio.sleep(1)
                
                # Dynamic Summary Card with Exact Plan Limits
                user_data = await db.get_user_data(message.from_user.id)
                current_plan = user_data.get('plan', 'free') if user_data else 'free'
                limits = get_plan_limits(current_plan)
                
                daily_files_count = user_data.get('daily_files', 0) if user_data else success_count
                total_used_bytes = await db.get_used_bytes(message.from_user.id)
                total_used_str = get_readable_file_size(total_used_bytes)
                
                uploaded_size_str = get_readable_file_size(batch_temp.UPLOADED_SIZE.get(message.from_user.id, 0))
                max_data_str = f"{limits['max_total_mb']} MB" if limits["max_total_mb"] != "Unlimited" else "Unlimited"
                max_files_str = str(limits["max_files"]) if limits["max_files"] != "Unlimited" else "Unlimited"

                complete_text = (
                    f"✅ **All done**\n\n"
                    f"Saved ➔ {success_count} of {total_files}\n\n"
                    f"📊 Click Here For The Details\n\n"
                    f"✅ Success ➔ {success_count}\n"
                    f"❌ Failed ➔ {failed_count}\n"
                    f"Uploaded now ➔ {uploaded_size_str}\n"
                    f"Used today ➔ {total_used_str} of {max_data_str}\n"
                    f"Files used ➔ {daily_files_count} of {max_files_str}"
                )
                thanks_markup = InlineKeyboardMarkup([[InlineKeyboardButton("❤️ Thanks", callback_data="back_home")]])
                try:
                    await status_msg.edit_text(complete_text, reply_markup=thanks_markup)
                except:
                    pass
            except Exception as e:
                await message.reply_text(f"Error processing start link: {e}")
            
            if LOGIN_SYSTEM == True:
                try:
                    await acc.disconnect()
                except:
                    pass
            batch_temp.IS_BATCH[message.from_user.id] = True
            return

        datas = message.text.split("/")
        temp = datas[-1].replace("?single","").split("-")
        fromID = int(temp[0].strip())
        toID = fromID
        await process_batch_range(client, message, message.text, fromID, toID)


async def process_batch_range(client: Client, message: Message, link_text: str, fromID: int, toID: int):
    datas = link_text.split("/")
    
    if LOGIN_SYSTEM == True:
        user_data = await db.get_session(message.from_user.id)
        if user_data is None:
            await message.reply("**For Downloading Restricted Content You Have To /login First.**")
            return
        api_id = int(await db.get_api_id(message.from_user.id))
        api_hash = await db.get_api_hash(message.from_user.id)
        try:
            acc = Client("saverestricted", session_string=user_data, api_hash=api_hash, api_id=api_id)
            await acc.connect()
        except:
            return await message.reply("**Your Login Session Expired. So /logout First Then Login Again By - /login**")
    else:
        if TechVJUser is None:
            await client.send_message(message.chat.id, f"**String Session is not Set**", reply_to_message_id=message.id)
            return
        acc = TechVJUser
            
    batch_temp.IS_BATCH[message.from_user.id] = False
    batch_temp.UPLOADED_SIZE[message.from_user.id] = 0
    total_files = (toID - fromID) + 1
    success_count = 0
    failed_count = 0

    cancel_markup = InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="cancel_process")]])
    status_msg = await message.reply_text(
        f"📥 **Downloading:** 0 of {total_files}\n✅ **Success:** 0\n❌ **Failed:** 0\n🔄 **Running:** Starting batch...",
        reply_markup=cancel_markup
    )

    current_index = 0
    for msgid in range(fromID, toID+1):
        if batch_temp.IS_BATCH.get(message.from_user.id): 
            break
        
        current_index += 1
        try:
            if "https://t.me/c/" in link_text:
                chatid = int("-100" + datas[4])
                await handle_private(client, acc, message, chatid, msgid, status_msg, cancel_markup, current_index, total_files, success_count, failed_count)
    
            elif "https://t.me/b/" in link_text:
                username = datas[4]
                await handle_private(client, acc, message, username, msgid, status_msg, cancel_markup, current_index, total_files, success_count, failed_count)
            
            else:
                username = datas[3]
                try:
                    msg = await acc.get_messages(username, msgid)
                except UsernameNotOccupied: 
                    await client.send_message(message.chat.id, "The username is not occupied by anyone", reply_to_message_id=message.id)
                    continue
                except:
                    pass
                
                try:
                    await handle_private(client, acc, message, username, msgid, status_msg, cancel_markup, current_index, total_files, success_count, failed_count)
                except Exception as e:
                    if ERROR_MESSAGE == True:
                        await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)

            success_count += 1
        except Exception as e:
            failed_count += 1
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)

        if current_index < total_files and WAITING_TIME > 0:
            for remaining in range(int(WAITING_TIME), 0, -1):
                if batch_temp.IS_BATCH.get(message.from_user.id): break
                try:
                    await status_msg.edit_text(
                        f"📥 **Downloading:** {current_index} of {total_files}\n✅ **Success:** {success_count}\n❌ **Failed:** {failed_count}\n⏳ **Sleeping For:** {remaining} Sec..",
                        reply_markup=cancel_markup
                    )
                except:
                    pass
                await asyncio.sleep(1)

    # Dynamic Summary Card with Exact Plan Limits
    user_data = await db.get_user_data(message.from_user.id)
    current_plan = user_data.get('plan', 'free') if user_data else 'free'
    limits = get_plan_limits(current_plan)
    
    daily_files_count = user_data.get('daily_files', 0) if user_data else success_count
    total_used_bytes = await db.get_used_bytes(message.from_user.id)
    total_used_str = get_readable_file_size(total_used_bytes)
    
    uploaded_size_str = get_readable_file_size(batch_temp.UPLOADED_SIZE.get(message.from_user.id, 0))
    max_data_str = f"{limits['max_total_mb']} MB" if limits["max_total_mb"] != "Unlimited" else "Unlimited"
    max_files_str = str(limits["max_files"]) if limits["max_files"] != "Unlimited" else "Unlimited"

    complete_text = (
        f"✅ **All done**\n\n"
        f"Saved ➔ {success_count} of {total_files}\n\n"
        f"📊 Click Here For The Details\n\n"
        f"✅ Success ➔ {success_count}\n"
        f"❌ Failed ➔ {failed_count}\n"
        f"Uploaded now ➔ {uploaded_size_str}\n"
        f"Used today ➔ {total_used_str} of {max_data_str}\n"
        f"Files used ➔ {daily_files_count} of {max_files_str}"
    )
    thanks_markup = InlineKeyboardMarkup([[InlineKeyboardButton("❤️ Thanks", callback_data="back_home")]])
    try:
        await status_msg.edit_text(complete_text, reply_markup=thanks_markup)
    except:
        pass

    if LOGIN_SYSTEM == True:
        try:
            await acc.disconnect()
        except:
            pass                
    batch_temp.IS_BATCH[message.from_user.id] = True


async def handle_private(client: Client, acc, message: Message, chatid, msgid, status_msg=None, cancel_markup=None, current_idx=1, total_files=1, success=0, failed=0):
    msg: Message = await acc.get_messages(chatid, msgid)
    if msg.empty: return 
    msg_type = get_message_type(msg)
    if not msg_type: return 
    
    # --- PLAN & LIMIT CHECK BEFORE DOWNLOADING ---
    file_size = 0
    if msg.document:
        file_size = msg.document.file_size
    elif msg.video:
        file_size = msg.video.file_size
    elif msg.audio:
        file_size = msg.audio.file_size
    elif msg.photo:
        file_size = 300000

    allowed, err_msg = await db.check_and_update_limit(message.from_user.id, file_size)
    if not allowed:
        await client.send_message(message.chat.id, err_msg, reply_to_message_id=message.id)
        batch_temp.IS_BATCH[message.from_user.id] = True
        return

    # Custom Chat / Target Channel Check
    user_chat_id = await db.get_chat(message.from_user.id)
    if user_chat_id:
        chat = int(user_chat_id)
    elif CHANNEL_ID:
        try:
            chat = int(CHANNEL_ID)
        except:
            chat = message.chat.id
    else:
        chat = message.chat.id
        
    if batch_temp.IS_BATCH.get(message.from_user.id): return 
    
    if "Text" == msg_type:
        try:
            await client.send_message(chat, msg.text, entities=msg.entities, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
            return 
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
            return 

    if status_msg and cancel_markup:
        try:
            await status_msg.edit_text(
                f"📥 **Downloading:** {current_idx} of {total_files}\n✅ **Success:** {success}\n❌ **Failed:** {failed}\n🔄 **Running:** Downloading...",
                reply_markup=cancel_markup
            )
        except:
            pass

    try:
        file = await acc.download_media(msg)
        if file and os.path.exists(file):
            f_size = os.path.getsize(file)
            current_total = batch_temp.UPLOADED_SIZE.get(message.from_user.id, 0)
            batch_temp.UPLOADED_SIZE[message.from_user.id] = current_total + f_size
            await db.add_used_bytes(message.from_user.id, f_size)
    except Exception as e:
        if ERROR_MESSAGE == True:
            await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML) 
        return

    if batch_temp.IS_BATCH.get(message.from_user.id): 
        if os.path.exists(file): os.remove(file)
        return 

    if status_msg and cancel_markup:
        try:
            await status_msg.edit_text(
                f"📥 **Downloading:** {current_idx} of {total_files}\n✅ **Success:** {success}\n❌ **Failed:** {failed}\n🔄 **Running:** Writing metadata...",
                reply_markup=cancel_markup
            )
        except:
            pass
        await asyncio.sleep(0.3)

    custom_caption = await db.get_caption(message.from_user.id)
    custom_thumb = await db.get_thumbnail(message.from_user.id)
    custom_artist = await db.get_artist(message.from_user.id)

    ph_path = None
    if custom_thumb:
        try:
            ph_path = await client.download_media(custom_thumb)
        except:
            ph_path = None

    if custom_caption:
        try:
            caption = custom_caption.format(filename=msg.document.file_name if msg.document else "Media")
        except:
            caption = custom_caption
    else:
        caption = msg.caption if msg.caption else None

    if status_msg and cancel_markup:
        try:
            await status_msg.edit_text(
                f"📥 **Downloading:** {current_idx} of {total_files}\n✅ **Success:** {success}\n❌ **Failed:** {failed}\n🔄 **Running:** Uploading...",
                reply_markup=cancel_markup
            )
        except:
            pass
            
    if "Document" == msg_type:
        if not ph_path and msg.document.thumbs:
            try:
                ph_path = await acc.download_media(msg.document.thumbs[0].file_id)
            except:
                ph_path = None
        
        try:
            await client.send_document(chat, file, thumb=ph_path, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        
    elif "Video" == msg_type:
        if not ph_path and msg.video.thumbs:
            try:
                ph_path = await acc.download_media(msg.video.thumbs[0].file_id)
            except:
                ph_path = None
        
        try:
            await client.send_video(chat, file, duration=msg.video.duration, width=msg.video.width, height=msg.video.height, thumb=ph_path, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)

    elif "Animation" == msg_type:
        try:
            await client.send_animation(chat, file, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        
    elif "Sticker" == msg_type:
        try:
            await client.send_sticker(chat, file, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)     

    elif "Voice" == msg_type:
        try:
            await client.send_voice(
                chat, file, 
                duration=msg.voice.duration, 
                caption=caption, 
                caption_entities=msg.caption_entities, 
                reply_to_message_id=message.id, 
                parse_mode=enums.ParseMode.HTML
            )
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)

    elif "Audio" == msg_type:
        if not ph_path and msg.audio.thumbs:
            try:
                ph_path = await acc.download_media(msg.audio.thumbs[0].file_id)
            except:
                ph_path = None

        duration = getattr(msg.audio, "duration", 0)
        performer = custom_artist if custom_artist else "kcxry"
        title = getattr(msg.audio, "title", msg.document.file_name if msg.document else "Audio File")

        try:
            await client.send_audio(
                chat, file, 
                thumb=ph_path, 
                caption=caption, 
                duration=duration, 
                performer=performer, 
                title=title, 
                reply_to_message_id=message.id, 
                parse_mode=enums.ParseMode.HTML
            )   
        except Exception as e:
            if ERROR_Message == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)

    elif "Photo" == msg_type:
        try:
            await client.send_photo(chat, file, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
    
    if ph_path and os.path.exists(ph_path): 
        os.remove(ph_path)
    if os.path.exists(file): 
        os.remove(file)


def get_message_type(msg: pyrogram.types.messages_and_media.message.Message):
    try:
        msg.document.file_id
        return "Document"
    except:
        pass

    try:
        msg.video.file_id
        return "Video"
    except:
        pass

    try:
        msg.animation.file_id
        return "Animation"
    except:
        pass

    try:
        msg.sticker.file_id
        return "Sticker"
    except:
        pass

    try:
        msg.voice.file_id
        return "Voice"
    except:
        pass

    try:
        msg.audio.file_id
        return "Audio"
    except:
        pass

    try:
        msg.photo.file_id
        return "Photo"
    except:
        pass

    try:
        msg.text
        return "Text"
    except:
        pass

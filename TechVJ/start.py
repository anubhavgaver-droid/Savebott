# Don't Remove Credit Tg - @VJ_Bots
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import os
import asyncio 
import pyrogram
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, UserAlreadyParticipant, InviteHashExpired, UsernameNotOccupied
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message 
from config import API_ID, API_HASH, ERROR_MESSAGE, LOGIN_SYSTEM, STRING_SESSION, CHANNEL_ID, WAITING_TIME
from database.db import db
from TechVJ.strings import HELP_TXT
from bot import TechVJUser

class batch_temp(object):
    IS_BATCH = {}

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


# start command with Payload & dlbot Support
@Client.on_message(filters.command(["start", "dlbot"]))
async def send_start(client: Client, message: Message):
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
    
    if len(message.command) > 1:
        extracted_link = message.command[1]
        if "t.me/" in extracted_link:
            message.text = extracted_link
            return await save(client, message)

    buttons = [[
        InlineKeyboardButton("❣️ Developer", url = "https://t.me/kingvj01")
    ],[
        InlineKeyboardButton('🔍 sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ', url='https://t.me/vj_bot_disscussion'),
        InlineKeyboardButton('🤖 ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ', url='https://t.me/vj_bots')
    ]]
    reply_markup = InlineKeyboardMarkup(buttons)
    await client.send_message(
        chat_id=message.chat.id, 
        text=f"<b>👋 Hi {message.from_user.mention}, I am Save Restricted Content Bot, I can send you restricted content by its post link.\n\nFor downloading restricted content /login first.\n\nKnow how to use bot by - /help</b>", 
        reply_markup=reply_markup, 
        reply_to_message_id=message.id
    )
    return


# help command
@Client.on_message(filters.command(["help"]))
async def send_help(client: Client, message: Message):
    await client.send_message(
        chat_id=message.chat.id, 
        text=f"{HELP_TXT}"
    )

# cancel command
@Client.on_message(filters.command(["cancel"]))
async def send_cancel(client: Client, message: Message):
    batch_temp.IS_BATCH[message.from_user.id] = True
    await client.send_message(
        chat_id=message.chat.id, 
        text="**Batch Successfully Cancelled.**"
    )


# ==================== /batch COMMAND HANDLER (Interactive Step 1 & Step 2) ====================
@Client.on_message(filters.command("batch") & filters.private)
async def batch_command(client: Client, message: Message):
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)

    if batch_temp.IS_BATCH.get(message.from_user.id) == False:
        return await message.reply_text("**One Task Is Already Processing. Wait For Complete It. If You Want To Cancel This Task Then Use - /cancel**")

    try:
        # Step 1: First message link
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

        # Step 2: Last message link or count
        second_msg = await client.ask(
            chat_id=message.chat.id,
            text="<b>📦 Batch Save - Step 2 of 2\n\nNow tell me where to stop:\n\n• Paste the link of the last message\n• Or just send how many files you want (e.g. 50)\n\nSend /cancel to stop.</b>",
            filters=filters.text,
            timeout=120
        )
        if second_msg.text == "/cancel":
            return await second_msg.reply("<b>Batch cancelled.</b>")

        second_input = second_msg.text.strip()

        # Parse links and range
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
        
        # Handling Bot Start Parameter Links (e.g., https://t.me/BotName?start=payload)
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
            
            try:
                try:
                    count_msg = await client.ask(
                        chat_id=message.chat.id,
                        text="<b>Is link mein total kitni files hain? Kripya sirf number bhejiye (jaise: 20):\n\n(Process cancel karne ke liye /cancel bhejein)</b>",
                        filters=filters.text,
                        timeout=60
                    )
                    if count_msg.text == "/cancel":
                        await count_msg.reply("<b>Process cancelled !</b>")
                        if LOGIN_SYSTEM == True:
                            try: await acc.disconnect()
                            except: pass
                        batch_temp.IS_BATCH[message.from_user.id] = True
                        return
                    total_expected = int(count_msg.text.strip())
                except ValueError:
                    await message.reply("**Invalid number provided. Please send link again.**")
                    if LOGIN_SYSTEM == True:
                        try: await acc.disconnect()
                        except: pass
                    batch_temp.IS_BATCH[message.from_user.id] = True
                    return
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
                    f"📥 **Downloading:** 0 of {total_expected}\n✅ **Success:** 0\n❌ **Failed:** 0\n🔄 **Running:** Fetching files...",
                    reply_markup=cancel_markup
                )
                
                last_msg_id = 0
                async for m in acc.get_chat_history(bot_username, limit=1):
                    last_msg_id = m.id
                    break

                await acc.send_message(bot_username, f"/start {payload}")
                
                media_msgs = []
                seen_ids = set()
                
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
                
                media_msgs.sort(key=lambda x: x.id)
                media_msgs = media_msgs[:total_expected]
                
                total_files = len(media_msgs)
                if total_files == 0:
                    await status_msg.edit_text("**No files found or bot didn't respond.**")
                    if LOGIN_SYSTEM == True:
                        try: await acc.disconnect()
                        except: pass
                    batch_temp.IS_BATCH[message.from_user.id] = True
                    return

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
                    
                    # Sleep Time Counter Display
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
                
                try:
                    await status_msg.edit_text(f"✨ **Batch Completed!**\n\n📥 **Total:** {total_files}\n✅ **Success:** {success_count}\n❌ **Failed:** {failed_count}")
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

        # Direct Single Link Handling
        datas = message.text.split("/")
        temp = datas[-1].replace("?single","").split("-")
        fromID = int(temp[0].strip())
        toID = fromID
        await process_batch_range(client, message, message.text, fromID, toID)


# Common batch range processor function with countdown sleep
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

        # Sleep Time Countdown Display Before Next File
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

    try:
        await status_msg.edit_text(f"✨ **Batch Completed!**\n\n📥 **Total:** {total_files}\n✅ **Success:** {success_count}\n❌ **Failed:** {failed_count}")
    except:
        pass

    if LOGIN_SYSTEM == True:
        try:
            await acc.disconnect()
        except:
            pass                
    batch_temp.IS_BATCH[message.from_user.id] = True


# handle private with exact video status flow (Downloading -> Writing metadata -> Uploading -> Delete)
async def handle_private(client: Client, acc, message: Message, chatid, msgid, status_msg=None, cancel_markup=None, current_idx=1, total_files=1, success=0, failed=0):
    msg: Message = await acc.get_messages(chatid, msgid)
    if msg.empty: return 
    msg_type = get_message_type(msg)
    if not msg_type: return 
    if CHANNEL_ID:
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

    # 1. DOWNLOADING STATUS
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
    except Exception as e:
        if ERROR_MESSAGE == True:
            await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML) 
        return

    if batch_temp.IS_BATCH.get(message.from_user.id): 
        if os.path.exists(file): os.remove(file)
        return 

    # 2. WRITING METADATA STATUS
    if status_msg and cancel_markup:
        try:
            await status_msg.edit_text(
                f"📥 **Downloading:** {current_idx} of {total_files}\n✅ **Success:** {success}\n❌ **Failed:** {failed}\n🔄 **Running:** Writing metadata...",
                reply_markup=cancel_markup
            )
        except:
            pass
        await asyncio.sleep(0.3)

    if msg.caption:
        caption = msg.caption
    else:
        caption = None

    # 3. UPLOADING STATUS
    if status_msg and cancel_markup:
        try:
            await status_msg.edit_text(
                f"📥 **Downloading:** {current_idx} of {total_files}\n✅ **Success:** {success}\n❌ **Failed:** {failed}\n🔄 **Running:** Uploading...",
                reply_markup=cancel_markup
            )
        except:
            pass
            
    if "Document" == msg_type:
        try:
            ph_path = await acc.download_media(msg.document.thumbs[0].file_id)
        except:
            ph_path = None
        
        try:
            await client.send_document(chat, file, thumb=ph_path, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        if ph_path != None and os.path.exists(ph_path): os.remove(ph_path)
        
    elif "Video" == msg_type:
        try:
            ph_path = await acc.download_media(msg.video.thumbs[0].file_id)
        except:
            ph_path = None
        
        try:
            await client.send_video(chat, file, duration=msg.video.duration, width=msg.video.width, height=msg.video.height, thumb=ph_path, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        if ph_path != None and os.path.exists(ph_path): os.remove(ph_path)

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
            if ERROR_Message == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)

    elif "Audio" == msg_type:
        try:
            ph_path = await acc.download_media(msg.audio.thumbs[0].file_id)
        except:
            ph_path = None

        duration = getattr(msg.audio, "duration", 0)
        performer = "kcxry"
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
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        
        if ph_path != None and os.path.exists(ph_path): os.remove(ph_path)

    elif "Photo" == msg_type:
        try:
            await client.send_photo(chat, file, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
    
    # 4. DELETE LOCAL FILE AFTER SENDING
    if os.path.exists(file): 
        os.remove(file)


# get the type of message
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

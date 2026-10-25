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

@Client.on_message(filters.text & filters.private)
async def save(client: Client, message: Message):
    # Joining chat
    if ("https://t.me/+" in message.text or "https://t.me/joinchat/" in message.text) and LOGIN_SYSTEM == False:
        if TechVJUser is None:
            await client.send_message(message.chat.id, "String Session is not Set", reply_to_message_id=message.id)
            return
        try:
            try:
                await TechVJUser.join_chat(message.text)
            except Exception as e: 
                await client.send_message(message.chat.id, f"Error : {e}", reply_to_message_id=message.id)
                return
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
                # Step 1: User se pucho ki total kitni files hain
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
                
                # Step 2: Command bhejne se pehle last message ID note karo
                last_msg_id = 0
                async for m in acc.get_chat_history(bot_username, limit=1):
                    last_msg_id = m.id
                    break

                # Step 3: Target bot ko start command bhejo
                await acc.send_message(bot_username, f"/start {payload}")
                
                # Step 4: Files collect karo
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
                        await status_msg.edit_text(
                            f"📥 **Downloading:** {idx} of {total_files}\n✅ **Success:** {success_count}\n❌ **Failed:** {failed_count}\n🔄 **Running:** Message ID {msg.id}",
                            reply_markup=cancel_markup
                        )
                        await handle_private(client, acc, message, bot_username, msg.id)
                        success_count += 1
                    except Exception as e:
                        failed_count += 1
                        if ERROR_MESSAGE == True:
                            await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
                    
                    await asyncio.sleep(WAITING_TIME)
                
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

        # Handling Public / Private Channel Batch Links (First Link to Last Link)
        datas = message.text.split("/")
        temp = datas[-1].replace("?single","").split("-")
        fromID = int(temp[0].strip())
        try:
            toID = int(temp[1].strip())
        except:
            toID = fromID

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
                await status_msg.edit_text(
                    f"📥 **Downloading:** {current_index} of {total_files}\n✅ **Success:** {success_count}\n❌ **Failed:** {failed_count}\n🔄 **Running:** Msg ID {msgid}",
                    reply_markup=cancel_markup
                )

                if "https://t.me/c/" in message.text:
                    chatid = int("-100" + datas[4])
                    await handle_private(client, acc, message, chatid, msgid)
        
                elif "https://t.me/b/" in message.text:
                    username = datas[4]
                    await handle_private(client, acc, message, username, msgid)
                
                else:
                    username = datas[3]
                    try:
                        msg = await client.get_messages(username, msgid)
                    except UsernameNotOccupied: 
                        await client.send_message(message.chat.id, "The username is not occupied by anyone", reply_to_message_id=message.id)
                        continue
                    try:
                        await client.copy_message(message.chat.id, msg.chat.id, msg.id, reply_to_message_id=message.id)
                    except:
                        await handle_private(client, acc, message, username, msgid)

                success_count += 1
            except Exception as e:
                failed_count += 1
                if ERROR_MESSAGE == True:
                    await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)

            await asyncio.sleep(WAITING_TIME)

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


# handle private
async def handle_private(client: Client, acc, message: Message, chatid: int, msgid: int):
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

    try:
        file = await acc.download_media(msg)
    except Exception as e:
        if ERROR_MESSAGE == True:
            await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML) 
        return

    if batch_temp.IS_BATCH.get(message.from_user.id): 
        if os.path.exists(file): os.remove(file)
        return 

    if msg.caption:
        caption = msg.caption
    else:
        caption = None
            
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
            if ERROR_MESSAGE == True:
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

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @trojanzhex


import time
import json
import os
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from helpers.progress import progress_func
from helpers.tools import execute, clean_up
from helpers.download_from_url import download_link
from helpers.upload import upload_video

DATA = {}

async def download_file(client, message):
    media = message.reply_to_message
    if media.empty:
        await message.reply_text('Why did you delete that?? 😕', True)
        return

    msg = await client.send_message(
        chat_id=message.chat.id,
        text="**Downloading your file to server...**",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(text="Check Progress", callback_data="progress_msg")]
        ]),
        reply_to_message_id=media.message_id
    )
    filetype = media.document or media.video

    c_time = time.time()

    dwld_loc = await client.download_media(
        message=media,
        progress=progress_func,
        progress_args=(
            "**Downloading Source Media:**",
            msg,
            c_time
        )
    )

    await msg.edit_text(f"`Analyzing Source Video ...`")
    
    output = await execute(f"ffprobe -hide_banner -show_streams -print_format json '{download_location}'")
    
    if not output:
        await clean_up(download_location)
        await msg.edit_text("Some Error Occured while Fetching Details...")
        return

    details = json.loads(output[0])
    buttons = []
    DATA[f"{message.chat.id}-{msg.message_id}"] = {}
    for stream in details["streams"]:
        mapping = stream["index"]
        stream_name = stream["codec_name"]
        stream_type = stream["codec_type"]
        if stream_type in ("video", "subtitle"):
            pass
        else:
            continue
        try: 
            lang = str(stream["codec_type"]) + " - " + str(stream["codec_name"]) + " - " + str(stream["width"]) + "*" + str(stream["height"])
        except:
            lang = mapping
        
        DATA[f"{message.chat.id}-{msg.message_id}"][int(mapping)] = {
            "map" : mapping,
            "name" : stream_name,
            "type" : stream_type,
            "lang" : lang,
            "location" : download_location
        }
        buttons.append([
            InlineKeyboardButton(
                f"{stream_type.upper()} - {str(lang).upper()}", f"{stream_type}_{mapping}_{message.chat.id}-{msg.message_id}"
            )
        ])

    buttons.append([
        InlineKeyboardButton("CANCEL",f"cancel_{mapping}_{message.chat.id}-{msg.message_id}")
    ])    

    await msg.edit_text(
        "**Select the Stream ...**",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def download_url_link(client, message):
    
    m = message.reply_to_message
    link = m.text
    
    if '|' in link:
        link, filename = link.split('|')
        link = link.strip()
        filename = filename.strip()
        filename = filename.replace('%40','@')
        dl_path = os.path.join(f'./{filename}')
    else:
        if os.path.splitext(link)[1]:
            link = link.strip()
            filename = os.path.basename(link)
            filename = filename.replace('%40','@')
            dl_path = os.path.join("./", filename)
        else:
            await m.reply_text(text=f"I Could not Determine The FileType !\nPlease Use Custom Filename With Extension\nSee /help", quote=True)
            return
        
    
    msg = await client.send_message(
        chat_id=m.chat.id,
        text="**Downloading your Link to Server...**",
        reply_to_message_id=m.message_id
    )
    
    start = time.time()
    try:
        dwld_loc = await download_link(link, dl_path, msg, start, client)
    except Exception as e:
        print(e)
        await msg.edit(f"**Download Failed** :\n\n{e}")
        await clean_up(dwld_loc)
        return
    
    await msg.edit_text(f"`{dwld_loc}`\n\n**Encoding. Please Wait ...**")
    
    await msg.edit_text(f"`Analyzing Source Video ...`")
    
    output = await execute(f"ffprobe -hide_banner -show_streams -print_format json '{download_location}'")
    
    if not output:
        await clean_up(download_location)
        await msg.edit_text("Some Error Occured while Fetching Details...")
        return

    details = json.loads(output[0])
    buttons = []
    DATA[f"{message.chat.id}-{msg.message_id}"] = {}
    for stream in details["streams"]:
        mapping = stream["index"]
        stream_name = stream["codec_name"]
        stream_type = stream["codec_type"]
        if stream_type in ("video", "subtitle"):
            pass
        else:
            continue
        try: 
            lang = str(stream["codec_type"]) + " - " + str(stream["codec_name"]) + " - " + str(stream["width"]) + "*" + str(stream["height"])
        except:
            lang = mapping
        
        DATA[f"{message.chat.id}-{msg.message_id}"][int(mapping)] = {
            "map" : mapping,
            "name" : stream_name,
            "type" : stream_type,
            "lang" : lang,
            "location" : download_location
        }
        buttons.append([
            InlineKeyboardButton(
                f"{stream_type.upper()} - {str(lang).upper()}", f"{stream_type}_{mapping}_{message.chat.id}-{msg.message_id}"
            )
        ])

    buttons.append([
        InlineKeyboardButton("CANCEL",f"cancel_{mapping}_{message.chat.id}-{msg.message_id}")
    ])    

    await msg.edit_text(
        "**Select the Stream ...**",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

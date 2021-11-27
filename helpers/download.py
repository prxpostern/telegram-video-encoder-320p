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

    await msg.edit_text(f"**Encoding. Please Wait ...**")
    
    out_loc = os.path.basename(dwld_loc)
    out_loc = os.path.splitext(out_loc)[0]
    out_loc = str(out_loc) + "_320p.mp4"
    
    out, err, rcode, pid = await execute(f"ffmpeg -i \"{dwld_loc}\" -c:v libx264 -crf 20 -s 320*240 -c:a aac -af \"pan=stereo|c0=c01|c1=c1\" -ar 48000 -ab 96k \"{out_loc}\" -y")
    if rcode != 0:
        await message.edit_text(f"**Error Occured.**\n\n{err}")
        print(err)
        await clean_up(dwld_loc, out_loc)
        return

    await clean_up(dwld_loc)
    await msg.edit_text(f"**Encoded Successfully !**")
    await upload_video(client, media, out_loc)
    

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
            dl_path = os.path.join("./", os.path.basename(link))
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
    
    await msg.edit_text(f"**Encoding. Please Wait ...**")
    
    out_loc = os.path.basename(dwld_loc)
    out_loc = os.path.splitext(out_loc)[0]
    out_loc = str(out_loc) + "_320p.mp4"
    
    out, err, rcode, pid = await execute(f"ffmpeg -i \"{dwld_loc}\" -c:v libx264 -crf 20 -s 320*240 -c:a aac -af \"pan=stereo|c0=c01|c1=c1\" -ar 48000 -ab 96k \"{out_loc}\" -y")
    if rcode != 0:
        await message.edit_text(f"**Error Occured.**\n\n{err}")
        print(err)
        await clean_up(dwld_loc, out_loc)
        return

    await clean_up(dwld_loc)
    await msg.edit_text(f"**Encoded Successfully !**")
    await upload_video(client, m, out_loc)

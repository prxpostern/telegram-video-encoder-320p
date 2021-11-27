#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @trojanzhex


import time
import os
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata
from helpers.download_from_url import get_size
from helpers.tools import clean_up
from helpers.progress import progress_func
from helpers.thumbnail_video import thumb_creator
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton


async def upload_video(client, message, file_loc):

    msg = await message.edit_text(
        text="**Uploading Video ...**",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(text="Progress", callback_data="progress_msg")]])
    )

    duration = 0
    metadata = extractMetadata(createParser(file_loc))
    if metadata and metadata.has("duration"):
        duration = metadata.get("duration").seconds
    if metadata and metadata.has("width") and metadata.has("height"):
        width = metadata.get("width")
        height = metadata.get("height")
    else:
        width = 320
        height = 240
    size = os.path.getsize(file_loc)
    size = get_size(size)
    fn = os.path.basename(file_path)
    
    await msg.edit(f"🏞 Generating thumbnail")
    thumbnail = await thumb_creator(file_loc)
    
    c_time = time.time()    
    try:
        await client.send_video(
            chat_id=message.chat.id,
            video=file_loc,
            thumb=str(thumbnail),
            caption=f"{fn} [{size}]",
            width=width,
            height=height,
            duration=duration,
            progress=progress_func,
            progress_args=(
                "**Uploading Video:**",
                msg,
                c_time
            )
        )
    except Exception as e:
        print(e)     
        await msg.edit_text(f"**Some Error Occurred.\n\n{e}**")
        return True

    await msg.delete()
    await clean_up(file_loc)
    return False

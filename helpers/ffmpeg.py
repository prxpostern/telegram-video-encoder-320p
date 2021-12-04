#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from helpers.tools import execute, clean_up
from helpers.upload import upload_video, upload_subtitle

async def enc_video(client, message, data):
    
    await message.edit_text("`Encoding Video ...`\n\n**please wait**")

    dwld_loc = data['location']
    
    if os.path.splitext(dwld_loc)[1]:
        dwld_loc = os.path.splitext(dwld_loc)[0]
        out_loc = dwld_loc + "_320p.mp4"
    else:
        out_loc = dwld_loc + "_320p.mp4"
    

    #out, err, rcode, pid = await execute(f"ffmpeg -i \"{dwld_loc}\" -map 0:{data['map']} -af \"pan=stereo|c0=c0|c1=c0\" -ar 48000 -ab 256k -f mp3 \"{out_loc}\" -y")
    out, err, rcode, pid = await execute(f"ffmpeg -i \"{dwld_loc}\" -c:v libx264 -crf 20 -s 320*240 -c:a aac -ar 48000 -ab 96k \"{out_loc}\" -y")
    if rcode != 0:
        await message.edit_text(f"**(320p mp4 96k) - Error Occured.\n\n{err}**")
        print(err)
        await clean_up(dwld_loc, out_loc)
        return

    await clean_up(dwld_loc)
    status = await upload_video(client, message, out_loc)
    if status:
        time.sleep(3)
        await upload_video(client, message, out_loc)

async def extract_subtitle(client, message, data):
    await message.edit_text("Extracting Stream from file")

    dwld_loc = data['location']
    out_loc = data['location'] + ".srt"   

    out, err, rcode, pid = await execute(f"ffmpeg -i '{dwld_loc}' -map 0:{data['map']} '{out_loc}' -y")
    if rcode != 0:
        await message.edit_text(f"**Error Occured.\n\n{err}**")
        print(err)
        await clean_up(dwld_loc, out_loc)
        return

    await clean_up(dwld_loc)  
    await upload_subtitle(client, message, out_loc)

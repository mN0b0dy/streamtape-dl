#!/usr/bin/env python3

import os
import sys
import json
import requests
from rich.console import Console
from decouple import config

from helpers import *
from downloaders import pycurl_download

DEBUG = 0

# Config is at '.env'
# API documentation: https://streamtape.com/api
login_key = config('API_USERNAME')
key = config('API_PASSWORD')
outdir = config('OUTDIR')

console = Console()
cache = {} # file_id -> {ticket, info, link}

def get_ticket(file_id):
    response = requests.get(f"https://api.streamtape.com/file/dlticket?file={file_id}&login={login_key}&key={key}")
    data = json.loads(response.text)
    try:
        ticket = data['result']['ticket']
    except Exception as e:
        print(f"[X] Fail! get_ticket: {data}")
        raise e
    return ticket

def check_acc_info():
    headers = {'login' : login_key, 'key' : key }
    console.print("Checking credentials..", style="italic #87ceeb" )
    
    response = requests.get('https://api.strtape.tech/account/info?',headers)
    data = json.loads(response.text)
    status_code = data.get("status")
    if status_code != 200:
        print(f"[X] Fail! check_acc_info: {data}")
        console.print("Please set your credentials correctly at '.env' file here.", style = "bold red")
        sys.exit(1)

def dl_url(ticket,file_id):
    captcha_response=ticket
    response = requests.get(f"https://api.streamtape.com/file/dl?file={file_id}&ticket={ticket}&captcha_response={captcha_response}")
    data = json.loads(response.text)
    try:
        link = data['result']['url']
    except Exception as e:
        raise Exception(f"{str(e)}\ndl_url: {data}")
    byte_size = data.get('result').get('size')
    #size_in_MB = int(byte_size/1024/1024)
    #console.print(f'File Size : {size_in_MB}MB', style = "bold red")
    return link
    
def file_info(file_id):
    response = requests.get(f"https://api.streamtape.com/file/info?file={file_id}&login={login_key}&key={key}")
    data = json.loads(response.text)
    try:
        data['result']
    except Exception as e:
        print(f"file_info: {data}")
        raise e 
    return data['result']


##
## main()
##
load_cache()

if "are_creds_ok" not in cache:
    check_acc_info()
    cache["are_creds_ok"] = True

console.print(f'[OUTDIR] {outdir}', style='#88FF33')
outdir = os.path.realpath(os.path.expanduser(outdir))

for link in sys.argv[1:]:
    #console.print(f"Processing... {link}", style="bold cyan")
    file_id = parseid(link)
    ticket = None
    info = None
    download_link = None
    try:
        if file_id not in cache:
            ticket = get_ticket(file_id)
            info = file_info(file_id)
            sleep()
            download_link = dl_url(ticket,file_id)
            cache[file_id] = {"ticket": ticket, "info": info, "download_link": download_link}
        else:
            ticket = cache[file_id]['ticket']
            info = cache[file_id]['info']
            download_link = cache[file_id]['download_link']
            if not (ticket and info and download_link):
                raise Exception("Cached ticket/info/download_link is null")
    except Exception as e:
        if info:
            cache[file_id] = {"ticket": ticket, "info": info, "download_link": download_link}
            save_cache()
            try:
                status = info[file_id]['status']
                from http import HTTPStatus
                phrase = HTTPStatus(status).phrase
                console.print(f'\n[ {link} ]\n    {status} - "{phrase}"', style='yellow')
                if not DEBUG:
                    continue
            except Exception as e:
                print(str(e))
                print("TOO BAD!")
                sys.exit(1)
        console.print(f'[X] Failed.', style='red')
        console.print(f"    link: {link}", style="red")
        console.print(f"    info: {info}", style='red')
        #console.print(f"    file_id: {file_id}\n    ticket: {ticket}\n    download_link: {download_link}", style='red')
        sep = (10+ len(str(e))) * "-"
        print(f"{sep}")
        print(f"ERROR: {e}")
        print(f"{sep}")
        continue
    if DEBUG:
        console.print(f"[DEBUG][ {link} ]", style="cyan")
        console.print(f"[DEBUG]    file_id: {file_id}\n    ticket: {ticket}\n    download_link: {download_link}")
        console.print(f"[DEBUG]    info: {info}")
    file_name = info[file_id]['name']
    file_size = info[file_id]['size']
    info_status = info[file_id]['status']
    if '.' in file_name:
        # add file_id in file_name
        suffix = file_name.split(".")[-1]
        file_name = file_name[:-len(suffix)-1] + f' - {file_id}.{suffix}'
    outfile = os.path.join(outdir, file_name)
    if DEBUG:
        console.print(f'[DEBUG] Outfile: "{outfile}"') 
    
    console.print(f'\n["{file_name}"] ({hrsize(file_size)})')
    if os.path.isfile(outfile):
        local_size = os.stat(outfile).st_size 
        if local_size == file_size:
            console.print(f'    Already downloaded: "{file_name}"', style='italic yellow')
            continue
        else:
            pid = being_downloaded(file_id)
            if pid:
                console.print(f'    Being downloaded in another instance.. [Pid: {pid}]', style='yellow')
                continue
            else:
                console.print(f'    Restarting incomplete download: "{file_name}"', style='italic yellow')

    if not DEBUG:
        try:
            pycurl_download(download_link, outfile, file_size)
            print("")
        except Exception as e:
            console.print(f'[X] Failed to download: {file_name}', style='red')
            console.print(f"    link: {link}", style="red")
            console.print(f"    info: {info}", style='red')
            #console.print(f"    file_id: {file_id}\n    ticket: {ticket}\n    download_link: {download_link}", style='red')
            sep = (10+ len(str(e))) * "-"
            print(f"{sep}")
            print(f"ERROR: {e}")
            print(f"{sep}")
save_cache()

## EOF

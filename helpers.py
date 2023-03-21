import os
import sys
import signal
import psutil
import json
import time
from rich.console import Console

DEBUG = 0

f_cache = 'cache.json'
console = Console()

def signal_handler(sig, frame):
    sys.exit(-1)

signal.signal(signal.SIGINT, signal_handler)

def being_downloaded(file_id):
    # checks is the file_id is being downloaded on another instance.
    for proc in psutil.process_iter(['pid', 'name']):
        pid = proc.info["pid"]
        if pid == os.getpid():
            # skip ourselves..
            continue
        if 'python' in proc.name():
            cmdline = proc.cmdline()
            for arg in cmdline:
                if 'streamtape' in arg and file_id in arg:
                    if DEBUG:
                        ss = ' '.join(arg for arg in cmdline)
                        pid = proc.info["pid"]
                        print(f'[PID: {pid}] {ss}')
                    return pid
    return 0

def parseid(string):
    lst = []
    for i in string:
        lst.append(i)

    lst2 = lst[25:]

    file_id = ""
    for i in lst2:
        if i == "/":
            break;
        else:
            file_id += i
    return file_id
    print(f"FileID: {file_id}")

def sleep():
    # without this sleep method api will return  error 403[forbidden]
    if DEBUG:
        print(f"Sleeping 4 seconds to avoid API rate limiting...")
    for i in range(4,0,-1):
        #console.print(f"Please wait for {i} sec...", style="bold #FFFF00")
        time.sleep(1)
 
def hrsize(size):
    if size < 1024:
        return f"{size} bytes"
    elif size < pow(1024,2):
        return f"{round(size/1024, 2)} KB"
    elif size < pow(1024,3):
        return f"{round(size/(pow(1024,2)), 2)} MB"
    elif size < pow(1024,4):
        return f"{round(size/(pow(1024,3)), 2)} GB"

def save_cache():
    with open(f_cache, 'w') as fp:
        json.dump(cache, fp)

def load_cache():
    global cache
    if not os.path.isfile(f_cache):
        return
    with open(f_cache, 'r') as fp:
        cache = json.load(fp)
        if DEBUG:
            console.print(f"[DEBUG] Cache loaded! (Entries: {len(cache.keys())})", style="bold cyan")
        #print(cache)

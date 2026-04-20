import asyncio
import aiohttp
import os
import random
import re
import sys
import time
import threading
import binascii
import uuid
import string
from urllib.parse import urlencode
from pystyle import Center, Colorate, Colors, Write, System

# Attempt to import SignerPy for X-Gorgon generation
try:
    import SignerPy
except ImportError:
    pass

# --- Configuration & Global State ---
class State:
    success = 0
    fails = 0
    start_time = time.time()
    is_running = False
    # Hardcoded authenticated proxies
    PROXIES = [
        "31.59.20.176:6754:hxidjrjw:nylyfhelpvdx",
        "198.23.239.134:6540:hxidjrjw:nylyfhelpvdx",
        "45.38.107.97:6014:hxidjrjw:nylyfhelpvdx",
        "107.172.163.27:6543:hxidjrjw:nylyfhelpvdx",
        "198.105.121.200:6462:hxidjrjw:nylyfhelpvdx",
        "216.10.27.159:6837:hxidjrjw:nylyfhelpvdx",
        "142.111.67.146:5611:hxidjrjw:nylyfhelpvdx",
        "191.96.254.138:6185:hxidjrjw:nylyfhelpvdx",
        "31.58.9.4:6077:hxidjrjw:nylyfhelpvdx",
        "23.26.71.145:5628:hxidjrjw:nylyfhelpvdx"
    ]

# --- Core Logic Engine ---
class TikTokEngine:
    @staticmethod
    def extract_id(url):
        match = re.search(r'/video/(\d+)|/live/(\d+)|(\d{18,20})', url)
        return next((m for m in match.groups() if m), None) if match else None

    async def worker(self, session, sem, target_id, mode):
        endpoints = {
            "1": "https://api16-core-c-alisg.tiktokv.com/aweme/v1/aweme/stats/",      # Views
            "2": "https://api16-core-c-alisg.tiktokv.com/aweme/v1/aweme/collect/",    # Favorite
            "3": "https://api16-core-c-alisg.tiktokv.com/aweme/v1/commit/item/share/",# Share
            "4": "https://api16-core-c-alisg.tiktokv.com/aweme/v1/commit/item/digg/", # Like
            "5": "https://api16-core-c-alisg.tiktokv.com/aweme/v1/commit/follow/user/",# Follow
            "6": "https://api16-core-c-alisg.tiktokv.com/webcast/room/enter/"         # Live
        }
        
        url = endpoints[mode]
        
        while State.is_running:
            async with sem:
                try:
                    # Proxy Rotation & Formatting
                    raw = random.choice(State.PROXIES)
                    p = raw.split(':')
                    proxy_url = f"http://{p[2]}:{p[3]}@{p[0]}:{p[1]}"
                    
                    # Device Parameter Generation
                    device_id = str(random.randint(10**18, 10**19))
                    install_id = str(random.randint(10**18, 10**19))
                    params = {
                        "device_id": device_id,
                        "iid": install_id,
                        "version_code": "400304",
                        "device_platform": "android",
                        "aid": "1233",
                        "cdid": str(uuid.uuid4()),
                        "openudid": binascii.hexlify(os.urandom(8)).decode()
                    }
                    
                    # Targeting Logic
                    if mode == "5": params["user_id"] = target_id
                    elif mode == "6": params["room_id"] = target_id
                    else: params["aweme_id"] = target_id

                    query = urlencode(params)
                    
                    # Payload Data
                    payload = ""
                    if mode == "1": payload = f"item_id={target_id}&play_delta=1"
                    elif mode == "3": payload = f"item_id={target_id}&share_delta=1"
                    
                    # PySigner Signature Generation
                    try:
                        sig = SignerPy.XG(query, payload, "")
                        xg = sig.get("X-Gorgon")
                        xk = sig.get("X-Khronos")
                    except:
                        xg, xk = "", ""
                    
                    headers = {
                        "User-Agent": "com.ss.android.ugc.trill/400304 (Linux; U; Android 12; Pixel 6)",
                        "X-Gorgon": xg,
                        "X-Khronos": xk,
                        "Content-Type": "application/x-www-form-urlencoded"
                    }
                    
                    async with session.post(url, params=params, data=payload, headers=headers, proxy=proxy_url, timeout=10, ssl=False) as r:
                        resp = await r.json()
                        if r.status == 200 and resp.get("status_code") == 0:
                            State.success += 1
                        else:
                            State.fails += 1
                except:
                    State.fails += 1
                await asyncio.sleep(0.01)

# --- Utilities ---
def live_stats_thread():
    while True:
        if State.is_running:
            elapsed = time.time() - State.start_time
            rps = State.success / elapsed if elapsed > 0 else 0
            System.Title(f"TOK-BOT | SUCCESS: {State.success} | FAIL: {State.fails} | {rps:.1f} r/s")
        time.sleep(0.5)

def account_gen_logic():
    sid = f"sid_gen_{binascii.hexlify(os.urandom(16)).decode()}"
    with open("sessions.txt", "a") as f:
        f.write(f"{sid}\n")
    print(f"\n[+] Session Saved: {sid}")

# --- Main Interface ---
async def start_task(name, mode_id):
    target_input = Write.Input(f"\nEnter {name} URL or ID > ", Colors.blue_to_white, interval=0.001)
    target_id = TikTokEngine.extract_id(target_input)
    
    if not target_id:
        print("[-] Invalid ID.")
        time.sleep(1)
        return
        
    threads = int(Write.Input("Thread Count > ", Colors.blue_to_white))
    
    State.success = 0
    State.fails = 0
    State.is_running = True
    State.start_time = time.time()
    
    sem = asyncio.Semaphore(threads)
    async with aiohttp.ClientSession() as session:
        tasks = [TikTokEngine().worker(session, sem, target_id, mode_id) for _ in range(threads)]
        print(Colorate.Horizontal(Colors.green_to_yellow, f"[*] Sending {name} to {target_id}... (Ctrl+C to Stop)"))
        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            State.is_running = False

async def main():
    threading.Thread(target=live_stats_thread, daemon=True).start()
    
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        banner = r"""
    ████████╗██╗██╗  ██╗████████╗ ██████╗ ██╗  ██╗
    ╚══██╔══╝██║██║ ██╔╝╚══██╔══╝██╔═══██╗██║ ██╔╝
       ██║   ██║█████╔╝    ██║   ██║   ██║█████╔╝ 
       ██║   ██║██╔═██╗    ██║   ██║   ██║██╔═██╗ 
       ██║   ██║██║  ██╗   ██║   ╚██████╔╝██║  ██╗
       ╚═╝   ╚═╝╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝
        """
        print(Colorate.Vertical(Colors.yellow_to_green, Center.XCenter(banner)))
        print(Colorate.Horizontal(Colors.green_to_yellow, "\n[1] Views [2] Favorite [3] Share [4] Like [5] Follow [6] Live [7] Session Gen [0] Exit"))
        
        choice = Write.Input("\nOption > ", Colors.white_to_green, interval=0.001)

        if choice in ["1", "2", "3", "4", "5", "6"]:
            modes = {"1":"Views", "2":"Favorite", "3":"Share", "4":"Like", "5":"Follow", "6":"Live"}
            await start_task(modes[choice], choice)
        elif choice == "7":
            account_gen_logic()
            time.sleep(2)
        elif choice == "0":
            sys.exit()

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass

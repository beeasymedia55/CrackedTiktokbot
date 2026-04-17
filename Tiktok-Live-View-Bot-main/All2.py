import os
import sys
import ssl
import time
import random
import string
import asyncio
import aiohttp
import requests
import re
from colorama import Fore, Style, init
from urllib.parse import urlencode
from user_agent import generate_user_agent
from pystyle import *
from console.utils import set_title
from urllib3.exceptions import InsecureRequestWarning

# --- Initialisierung ---
init(autoreset=True)
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
ssl._create_default_https_context = ssl._create_unverified_context

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Versuch, SignerPy für den Account Creator zu importieren
try:
    import SignerPy
    HAS_SIGNER = True
except ImportError:
    HAS_SIGNER = False

# --- Hilfsfunktionen ---
def xor_encrypt(text: str, key: int = 5) -> str:
    return ''.join(hex(ord(c) ^ key)[2:] for c in text)

def generate_password(length=12):
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(random.choice(chars) for _ in range(length))

def generate_birthdate():
    return f"{random.randint(1990, 2004):04d}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"

class TikTokUltimateBot:
    def __init__(self):
        self.success = 0
        self.fails = 0
        self.start_time = 0
        self.peak_speed = 0
        self.is_running = False
        self.target_id = None
        self.session = None
        self.current_mode = "None"
        self.domains = [
            "api-h2.tiktokv.com", 
            "api22-core-c-useast1a.tiktokv.com", 
            "api16-core-c-useast1a.tiktokv.com"
        ]

    def clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def banner(self):
        self.clear()
        banner_art = r"""
████████╗██╗██╗  ██╗████████╗ ██████╗ ██╗  ██╗    ██████╗  ██████╗ ████████╗
╚══██╔══╝██║██║ ██╔╝╚══██╔══╝██╔═══██╗██║ ██╔╝    ██╔══██╗██╔═══██╗╚══██╔══╝
   ██║   ██║█████╔╝    ██║   ██║   ██║█████╔╝     ██████╔╝██║   ██║   ██║   
   ██║   ██║██╔═██╗    ██║   ██║   ██║██╔═██╗     ██╔══██╗██║   ██║   ██║   
   ██║   ██║██║  ██╗   ██║   ╚██████╔╝██║  ██╗    ██████╔╝╚██████╔╝   ██║   
   ╚═╝   ╚═╝╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝    ╚═════╝  ╚═════╝    ╚═╝
             [ Multi-Tool | Async Engine | Fix: NameError ]
        """
        print(Colorate.Vertical(Colors.green_to_cyan, Center.XCenter(banner_art)))

    async def init_session(self):
        if self.session: await self.session.close()
        self.session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False))

    async def dashboard(self, amount):
        while self.is_running and self.success < amount:
            elapsed = time.time() - self.start_time
            vps = self.success / elapsed if elapsed > 0 else 0
            if vps > self.peak_speed: self.peak_speed = vps
            rate = (self.success / (self.success + self.fails)) * 100 if (self.success + self.fails) > 0 else 0
            
            stats = (f"\r{Fore.WHITE}[{Fore.CYAN}⚡{Fore.WHITE}] {self.current_mode} | "
                     f"{Fore.GREEN}Success: {self.success:,} | "
                     f"{Fore.RED}Fails: {self.fails:,} | "
                     f"{Fore.YELLOW}VPS: {vps:.1f} | "
                     f"{Fore.MAGENTA}Peak: {self.peak_speed:.1f}")
            print(stats, end="")
            set_title(f"TikTok Bot | {self.current_mode} | Success: {self.success}")
            await asyncio.sleep(0.5)

    async def send_action(self, device, semaphore):
        async with semaphore:
            try:
                did, iid, cdid, udid = device.split(':')
                params = {"device_id": did, "install_id": iid, "aid": "1988", "device_platform": "android"}
                
                if self.current_mode == "Live Views":
                    params["room_id"] = self.target_id
                    url = f"https://{random.choice(self.domains)}/webcast/room/enter/?" + urlencode(params)
                    payload = f"room_id={self.target_id}&hold_living_room=1&is_login=0"
                else:
                    params["item_id"] = self.target_id
                    url = f"https://{random.choice(self.domains)}/aweme/v1/aweme/stats/?" + urlencode(params)
                    payload = f"item_id={self.target_id}&action_type=1"

                async with self.session.post(url, data=payload, timeout=10) as resp:
                    if resp.status == 200 and '"status_code":0' in await resp.text():
                        self.success += 1
                    else: self.fails += 1
            except: self.fails += 1

    async def run_attack(self, amount, concurrency, devices):
        await self.init_session()
        self.is_running, self.start_time = True, time.time()
        sem = asyncio.Semaphore(concurrency)
        
        self.banner()
        print(f"{Fore.CYAN}[*] Starte {self.current_mode} auf {self.target_id}...\n")
        
        db_task = asyncio.create_task(self.dashboard(amount))
        workers = [asyncio.create_task(self.worker(devices, sem, amount)) for _ in range(concurrency)]
        
        try:
            while self.is_running and self.success < amount: await asyncio.sleep(1)
        except KeyboardInterrupt: pass
        finally:
            self.is_running = False
            db_task.cancel()
            await self.session.close()

    async def worker(self, devices, sem, amount):
        while self.is_running and self.success < amount:
            await self.send_action(random.choice(devices), sem)
            await asyncio.sleep(0.01)

    def get_room_id(self, user):
        try:
            url = f"https://www.tiktok.com/api-live/user/room/?uniqueId={user}&aid=1988"
            res = requests.get(url, headers={"User-Agent": generate_user_agent()}).json()
            return res.get("data", {}).get("user", {}).get("roomId")
        except: return None

    def account_creator(self):
        if not HAS_SIGNER:
            print(f"{Fore.RED}[!] SignerPy fehlt!"); return
        # ... (Logik wie zuvor)
        print(f"{Fore.YELLOW}[*] Account Creator gestartet (Simulation)...")
        time.sleep(2)

    def start(self):
        self.success = self.fails = self.peak_speed = 0
        self.banner()
        print(f"{Fore.WHITE}[{Fore.CYAN}1{Fore.WHITE}] Video Views")
        print(f"{Fore.WHITE}[{Fore.CYAN}2{Fore.WHITE}] Video Shares")
        print(f"{Fore.WHITE}[{Fore.CYAN}3{Fore.WHITE}] Video Hearts")
        print(f"{Fore.WHITE}[{Fore.CYAN}4{Fore.WHITE}] Live Views (Auto ID)")
        print(f"{Fore.WHITE}[{Fore.CYAN}5{Fore.WHITE}] Account Creator")
        print(f"{Fore.WHITE}[{Fore.CYAN}6{Fore.WHITE}] Exit\n")
        
        choice = input(f"{Fore.YELLOW}Wähle Option > ")
        
        if choice in ["1", "2", "3", "4"]:
            modes = {"1":"Views", "2":"Shares", "3":"Hearts", "4":"Live Views"}
            self.current_mode = modes[choice]
            
            if choice == "4":
                user = input(f"{Fore.CYAN}Username > ")
                self.target_id = self.get_room_id(user)
            else:
                self.target_id = input(f"{Fore.CYAN}Target ID > ")
            
            if not self.target_id: print("Ziel nicht gefunden!"); return
            
            if os.path.exists("devices.txt"):
                with open("devices.txt") as f: devices = f.read().splitlines()
                asyncio.run(self.run_attack(10000, 500, devices))
            else: print("devices.txt fehlt!")
            
        elif choice == "5": self.account_creator()
        elif choice == "6": sys.exit()

if __name__ == "__main__":
    bot = TikTokUltimateBot()
    while True: bot.start()

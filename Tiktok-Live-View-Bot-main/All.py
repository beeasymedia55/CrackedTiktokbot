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
from urllib.parse import urlencode
from user_agent import generate_user_agent
from pystyle import *
from console.utils import set_title
from urllib3.exceptions import InsecureRequestWarning

# Versuch, SignerPy für den Account Creator zu importieren
try:
    import SignerPy
    HAS_SIGNER = True
except ImportError:
    HAS_SIGNER = False

# --- Globale Konfiguration & SSL Fix ---
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
ssl._create_default_https_context = ssl._create_unverified_context

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# --- Hilfsfunktionen für Account Creator ---
def xor_encrypt(text: str, key: int = 5) -> str:
    return ''.join(hex(ord(c) ^ key)[2:] for c in text)

def generate_password(length=12):
    password = [
        random.choice(string.ascii_lowercase),
        random.choice(string.ascii_uppercase),
        random.choice(string.digits),
        "_"
    ]
    all_chars = string.ascii_letters + string.digits + "!@#$%^&*()=+"
    password += [random.choice(all_chars) for _ in range(length - 4)]
    random.shuffle(password)
    return ''.join(password)

def generate_birthdate():
    return f"{random.randint(1990, 2004):04d}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"

class TikTokUltimateBot:
    def __init__(self):
        # Stats für Async Tasks
        self.success = 0
        self.fails = 0
        self.start_time = 0
        self.peak_speed = 0
        self.is_running = False
        self.target_id = None
        self.session = None
        self.current_mode = "None"

        # API Konfigurationen
        self.domains = [
            "api-h2.tiktokv.com", 
            "api22-core-c-useast1a.tiktokv.com", 
            "api16-core-c-useast1a.tiktokv.com",
            "api19-core-c-useast1a.tiktokv.com"
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
             [ Ultimate Edition | Multi-Tool | Live Dashboard ]
        """
        print(Colorate.Vertical(Colors.green_to_cyan, Center.XCenter(banner_art)))

    # ==========================================
    # CORE: ASYNC ENGINE & LIVE STATS
    # ==========================================
    async def init_session(self):
        timeout = aiohttp.ClientTimeout(total=15, connect=5)
        connector = aiohttp.TCPConnector(limit=0, keepalive_timeout=30)
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            connector=connector,
            cookie_jar=aiohttp.DummyCookieJar()
        )

    async def live_stats_dashboard(self, amount):
        """ Aktualisiert die Konsole und den Titelstrich in Echtzeit """
        while self.is_running and self.success < amount:
            elapsed = time.time() - self.start_time
            vps = self.success / elapsed if elapsed > 0 else 0
            if vps > self.peak_speed:
                self.peak_speed = vps
            
            rate = (self.success / (self.success + self.fails)) * 100 if (self.success + self.fails) > 0 else 0
            
            # Formatiere den Status-String
            stats = (f"\r[⚡] {self.current_mode} | "
                     f"Success: {self.success:,} | "
                     f"Fails: {self.fails:,} | "
                     f"VPS: {vps:.1f} | "
                     f"Peak: {self.peak_speed:.1f} | "
                     f"Erfolgsrate: {rate:.1f}%   ")
            
            print(Colorate.Horizontal(Colors.green_to_white, stats), end="")
            set_title(f"TikTok Bot | Mode: {self.current_mode} | Success: {self.success} | VPS: {vps:.1f}")
            
            await asyncio.sleep(0.5)

    async def send_action_async(self, device_data, semaphore):
        """ Führt den Request basierend auf dem aktuellen Modus aus """
        async with semaphore:
            try:
                parts = device_data.split(':')
                if len(parts) != 4:
                    return False
                did, iid, cdid, openudid = parts

                # Basis-Parameter
                params = {
                    "device_id": did, "install_id": iid, 
                    "aid": "1988", "device_platform": "android", "app_name": "tiktok_web"
                }

                # Modus-spezifische Anpassungen
                if self.current_mode == "Live Views":
                    params["room_id"] = self.target_id
                    url = f"https://{random.choice(self.domains)}/webcast/room/enter/?{urlencode(params)}"
                    payload = f"room_id={self.target_id}&hold_living_room=1&enter_source=long_press&is_login=0"
                else:
                    # Hier kannst du später die genauen API-Pfade für Video Views, Likes etc. einfügen
                    # Dies dient als dynamisches Gerüst für die anderen Funktionen
                    params["item_id"] = self.target_id
                    url = f"https://{random.choice(self.domains)}/aweme/v1/aweme/stats/?{urlencode(params)}"
                    payload = f"item_id={self.target_id}&action_type=1" # Beispiel für View

                headers = {"User-Agent": generate_user_agent(), "Content-Type": "application/x-www-form-urlencoded"}

                async with self.session.post(url, data=payload, headers=headers, ssl=False) as response:
                    text = await response.text()
                    if response.status == 200 and ('"status_code":0' in text or '"status_code": 0' in text):
                        self.success += 1
                        return True
                    else:
                        self.fails += 1
                        return False
            except:
                self.fails += 1
                return False

    async def worker(self, device_list, semaphore, amount):
        base_delay = 0.01
        consecutive_success = 0
        
        while self.is_running and self.success < amount:
            device = random.choice(device_list)
            is_success = await self.send_action_async(device, semaphore)
            
            if is_success:
                consecutive_success += 1
                delay = base_delay * 0.5 if consecutive_success > 50 else base_delay
            else:
                consecutive_success = 0
                delay = base_delay * 2
                
            await asyncio.sleep(delay + random.uniform(0, 0.005))

    async def run_attack(self, amount, concurrency, devices):
        await self.init_session()
        self.is_running = True
        self.start_time = time.time()
        semaphore = asyncio.Semaphore(concurrency)
        
        self.banner()
        print(Colorate.Horizontal(Colors.cyan_to_blue, f"🚀 Starte [{self.current_mode}] auf Ziel: {self.target_id}..."))
        print(f"Drücke STRG+C um abzubrechen.\n")
        
        # Starte den Dashboard-Task und die Worker
        tasks = [asyncio.create_task(self.worker(devices, semaphore, amount)) for _ in range(concurrency)]
        dashboard_task = asyncio.create_task(self.live_stats_dashboard(amount))
        
        try:
            # Warte bis das Ziel erreicht ist
            while self.is_running and self.success < amount:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n\n🛑 Vorgang durch Benutzer abgebrochen...")
        finally:
            self.is_running = False
            dashboard_task.cancel()
            for t in tasks: t.cancel()
            await self.session.close()
            print(f"\n\n{Fore.GREEN}✅ Beendet! Gesamt Erfolgreich: {self.success:,}{Fore.RESET}\n")
            input("Drücke Enter für das Hauptmenü...")

    # ==========================================
    # ROOM ID DETECTION
    # ==========================================
    def get_room_id(self, username):
        print(Colorate.Horizontal(Colors.yellow_to_red, f"\n[*] Suche Room-ID für User: {username}..."))
        headers = {"User-Agent": generate_user_agent(), "Referer": f"https://www.tiktok.com/@{username}/live"}
        url = f"https://www.tiktok.com/api-live/user/room/?aid=1988&app_name=tiktok_web&device_platform=web_pc&uniqueId={username}"
        try:
            res = requests.get(url, headers=headers, timeout=10).json()
            rid = res.get("data", {}).get("user", {}).get("roomId")
            if rid and rid != "0": return rid
        except: pass
        
        # Fallback auf Regex
        try:
            html = requests.get(f"https://www.tiktok.com/@{username}/live", headers=headers, timeout=10).text
            match = re.search(r'"roomId"\s*:\s*"(\d+)"', html)
            if match: return match.group(1)
        except: pass
        return None

    # ==========================================
    # ACCOUNT CREATOR (Synchron)
    # ==========================================
    def account_creator_module(self):
        if not HAS_SIGNER:
            print(Colorate.Horizontal(Colors.red_to_white, "[!] FEHLER: Modul 'SignerPy' fehlt!"))
            input("Drücke Enter...")
            return

        print(Colorate.Horizontal(Colors.cyan_to_blue, "\n[⚙] Starte TikTok Account Auto-Creator..."))
        count = int(input("[?] Wie viele Accounts sollen erstellt werden? > "))
        
        TM_HEADERS = {
            "Application-Name": "web", "Application-Version": "4.0.0",
            "User-Agent": "Mozilla/5.0", "Origin": "https://temp-mail.io",
            "X-Cors-Header": "iaWg3pchvFx48fY", "Content-Type": "application/json"
        }

        for i in range(count):
            print(f"\n{'-'*40}\n[*] Erstelle Account {i+1}/{count}")
            try:
                # 1. Temp Mail
                resp = requests.post("https://api.internal.temp-mail.io/api/v3/email/new", headers=TM_HEADERS, json={"min_name_length": 10, "max_name_length": 10})
                email, tm_token = resp.json()["email"], resp.json()["token"]
                print(f"[+] Temp-Mail: {email}")

                password = generate_password()
                birthdate = generate_birthdate()
                
                install_id = str(random.randint(10**18, 10**19))
                device_id = str(random.randint(10**18, 10**19))
                params = {
                    "device_platform": "android", "os": "android", "aid": "1233",
                    "device_type": "NE2211", "iid": install_id, "device_id": device_id
                }

                session = requests.Session()
                session.cookies.update({"install_id": install_id, "passport_csrf_token": "auto"})
                
                payload = {'rules_version': "v2", 'password': xor_encrypt(password), 'type': "34", 'email': xor_encrypt(email), 'email_theme': "2"}
                m = SignerPy.sign(params=params, payload=payload, cookie=session.cookies.get_dict())
                
                headers = {
                    'User-Agent': "com.zhiliaoapp.musically/2023708050",
                    'X-SS-STUB': m.get('x-ss-stub', ''), 'X-Ladon': m.get('x-ladon', ''),
                    'X-Khronos': m.get('x-khronos', ''), 'X-Argus': m.get('x-argus', ''), 'X-Gorgon': m.get('x-gorgon', '')
                }
                
                session.post("https://api16-normal-c-alisg.tiktokv.com/passport/email/send_code/", params=params, data=payload, headers=headers)
                
                print("[*] Warte auf E-Mail Code (max 60s)...")
                code = None
                for _ in range(60):
                    msg_resp = requests.get(f"https://api.internal.temp-mail.io/api/v3/email/{email}/messages", headers=TM_HEADERS).json()
                    for msg in msg_resp:
                        text = msg.get("subject", "") + " " + msg.get("body_text", "")
                        match = re.search(r"\b\d{6}\b", text)
                        if match: code = match.group(); break
                    if code: break
                    time.sleep(1)
                
                if not code:
                    print("[-] Code Timeout! Überspringe...")
                    continue
                
                verify_payload = {'birthday': birthdate, 'code': xor_encrypt(code), 'type': "34", 'email': xor_encrypt(email)}
                m2 = SignerPy.sign(params=params, payload=verify_payload)
                headers.update({
                    'X-SS-STUB': m2.get('x-ss-stub', ''), 'X-Ladon': m2.get('x-ladon', ''),
                    'X-Khronos': m2.get('x-khronos', ''), 'X-Argus': m2.get('x-argus', ''), 'X-Gorgon': m2.get('x-gorgon', '')
                })
                
                res_verify = session.post("https://api16-normal-c-alisg.tiktokv.com/passport/email/register_verify_login/", params=params, data=verify_payload, headers=headers)
                data = res_verify.json().get("data", {})
                
                if "session_key" in data:
                    with open("accounts.txt", "a") as f:
                        f.write(f"{email}:{password}:{data.get('name', 'Unknown')}\n")
                    print(Colorate.Horizontal(Colors.green_to_white, f"[✓] ERFOLG! Account gespeichert."))
                else:
                    print(Colorate.Horizontal(Colors.red_to_white, f"[-] Fehler: {res_verify.text}"))

            except Exception as e:
                print(f"[-] Unerwarteter Fehler: {e}")
            
            time.sleep(2)
        input("\nDrücke Enter für das Hauptmenü...")

    # ==========================================
    # MAIN MENU ROUTING
    # ==========================================
    def start(self):
        # Stats zurücksetzen bei jedem neuen Start
        self.success = 0
        self.fails = 0
        self.peak_speed = 0

        self.banner()
        print(f"{Fore.WHITE}[{Fore.CYAN}1{Fore.WHITE}] TikTok Video Views  (Async)")
        print(f"{Fore.WHITE}[{Fore.CYAN}2{Fore.WHITE}] TikTok Video Shares (Async)")
        print(f"{Fore.WHITE}[{Fore.CYAN}3{Fore.WHITE}] TikTok Video Hearts (Async)")
        print(f"{Fore.WHITE}[{Fore.CYAN}4{Fore.WHITE}] TikTok Followers    (Async)")
        print(f"{Fore.WHITE}[{Fore.CYAN}5{Fore.WHITE}] TikTok Live Views   (Auto Room-ID)")
        print(f"{Fore.WHITE}[{Fore.CYAN}6{Fore.WHITE}] TikTok Auto Account Creator")
        print(f"{Fore.WHITE}[{Fore.CYAN}7{Fore.WHITE}] Beenden\n")
        
        choice = Write.Input("Wähle Option > ", Colors.green_to_yellow, interval=0.0)
        
        modes = {"1": "Video Views", "2": "Shares", "3": "Hearts", "4": "Followers", "5": "Live Views"}
        
        if choice in modes:
            self.current_mode = modes[choice]
            
            if choice == "5":
                user = Write.Input("\nUsername (ohne @) > ", Colors.green_to_yellow, interval=0.0)
                self.target_id = self.get_room_id(user)
                if not self.target_id:
                    print(Colorate.Horizontal(Colors.red_to_white, "[!] User ist offline oder Room-ID nicht gefunden."))
                    input("Enter drücken...")
                    return
            else:
                self.target_id = Write.Input("\nVideo ID / Target ID > ", Colors.green_to_yellow, interval=0.0)

            concurrency = int(Write.Input("Gleichzeitige Tasks (Empfohlen: 1000) > ", Colors.green_to_yellow, interval=0.0) or 1000)
            amount = int(Write.Input("Ziel-Anzahl > ", Colors.green_to_yellow, interval=0.0) or 10000)
            
            if not os.path.exists("devices.txt"):
                print("FEHLER: 'devices.txt' nicht gefunden!")
                input("Enter drücken...")
                return
                
            with open("devices.txt", "r") as f:
                devices = f.read().splitlines()
                
            if not devices: 
                print("FEHLER: 'devices.txt' ist leer!")
                input("Enter drücken...")
                return
            
            # Start Async Event Loop
            asyncio.run(self.run_attack(amount, concurrency, devices))

        elif choice == "6":
            self.account_creator_module()
        elif choice == "7":
            sys.exit()

if __name__ == "__main__":
    bot = TikTokUltimateBot()
    while True:
        bot.start()

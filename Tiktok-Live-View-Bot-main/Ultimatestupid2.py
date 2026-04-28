from urllib.parse import urlencode
from pystyle import *
from random import choice
import os, sys, ssl, re, time, random, threading, requests, hashlib, json, base64
from console.utils import set_title
from urllib3.exceptions import InsecureRequestWarning
from colorama import init, Fore

init(autoreset=True)

# --- Initialisierung ---
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
ssl._create_default_https_context = ssl._create_unverified_context

_lock = threading.Lock()
success = 0
fails = 0
reqs = 0

# --- Banner ---
def Banner():
    os.system('cls' if os.name == 'nt' else 'clear')
    Banner1 = r"""
████████╗██╗██╗  ██╗████████╗ ██████╗ ██╗  ██╗    ██████╗  ██████╗ ████████╗
╚══██╔══╝██║██║ ██╔╝╚══██╔══╝██╔═══██╗██║ ██╔╝    ██╔══██╗██╔═══██╗╚══██╔══╝
   ██║   ██║█████╔╝    ██║   ██║   ██║█████╔╝     ██████╔╝██║   ██║   ██║   
   ██║   ██║██╔═██╗    ██║   ██║   ██║██╔═██╗     ██╔══██╗██║   ██║   ██║   
   ██║   ██║██║  ██╗   ██║   ╚██████╔╝██║  ██╗    ██████╔╝╚██████╔╝   ██║   
   ╚═╝   ╚═╝╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝    ╚═════╝  ╚═════╝    ╚═╝                                                                            
    """
    print(Center.XCenter(Colorate.Vertical(Colors.yellow_to_green, Banner1, 2)))
    print(Center.XCenter(f"{Fore.CYAN}Stay Alive & Viewer Booster - Cracked & Fixed by PronsMods\n"))

# --- INTERNE DATEN (KEINE EXTERNE TXT MEHR NÖTIG) ---
__domains = [
    "api-h2.tiktokv.com", "api22-core-c-useast1a.tiktokv.com", 
    "api19-core-c-useast1a.tiktokv.com", "api16-core-c-useast1a.tiktokv.com",
    "api21-core-c-useast1a.tiktokv.com", "api19-core-useast5.us.tiktokv.com"
]

__localesLanguage = [
    "de_DE", "en_US", "en_GB", "fr_FR", "es_ES", "tr_TR", "it_IT", 
    "pt_BR", "ru_RU", "ar_SA", "ja_JP", "ko_KR"
]

__regions = [
    "DE", "US", "GB", "FR", "ES", "TR", "IT", "BR", "RU", "SA", "JP", "KR"
]

__tzname = [
    "Europe/Berlin", "America/New_York", "Europe/London", "Europe/Paris", 
    "Europe/Istanbul", "America/Sao_Paulo", "Europe/Moscow", "Asia/Riyadh", "Asia/Tokyo"
]

__versionCode = ["190303", "190205", "190204", "190103", "270204"]

# --- EXTERNE DATEIEN LADEN ---
def load_files():
    try:
        with open("sessions.txt", "r") as f: sess = f.read().splitlines()
        with open("devices.txt", "r") as f: devs = f.read().splitlines()
        return sess, devs
    except FileNotFoundError as e:
        print(f"{Fore.RED}[!] Fehler: {e.filename} nicht gefunden!")
        sys.exit()

__session_id, devices_data = load_files()

# --- Core Logik ---

class Gorgon:
    def __init__(self, params: str, data: str = None, unix: int = None):
        self.params = params
        self.data = data
        self.unix = unix

    def get_value(self):
        # Gorgon/Stub Logik
        gorgon_str = f"{self.params}{self.data if self.data else ''}{self.unix}"
        return hashlib.md5(gorgon_str.encode()).hexdigest()

def getRoomID(username):
    """Scraped die Room-ID und speichert sie"""
    print(f"{Fore.YELLOW}[*] Suche Live-ID für @{username}...")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Referer": "https://www.tiktok.com/"
    }
    try:
        res = requests.get(f"https://www.tiktok.com/@{username}/live", headers=headers, timeout=10)
        match = re.search(r'room_id=(\d+)', res.text) or re.search(r'"roomId":"(\d+)"', res.text)
        if match:
            rid = match.group(1)
            with open("room_id.txt", "w") as f: f.write(rid)
            print(f"{Fore.GREEN}[+] Room ID gefunden: {rid}")
            return rid
        else:
            print(f"{Fore.RED}[!] User scheint nicht Live zu sein.")
    except Exception as e:
        print(f"{Fore.RED}[!] Fehler beim Grabbing: {e}")
    return None

def sendLiveViews(did, iid, cdid, udid):
    global success, fails, reqs
    while True: # Endlosschleife für Stay-Alive
        try:
            # Zufällige Daten wählen
            session_id = random.choice(__session_id)
            lang = random.choice(__localesLanguage)
            reg = random.choice(__regions)
            tz = random.choice(__tzname)
            dom = random.choice(__domains)
            v_code = random.choice(__versionCode)
            
            # Aktuelle Room ID lesen
            with open("room_id.txt", "r") as f: room_id = f.read().strip()
            
            _ts = int(time.time())
            params = urlencode({
                "room_id": room_id,
                "device_id": did,
                "install_id": iid,
                "aid": "1988",
                "device_platform": "android",
                "language": lang,
                "region": reg,
                "timezone_name": tz,
                "version_code": v_code,
                "app_name": "tiktok_web"
            })

            payload = f"room_id={room_id}&hold_living_room=1&is_login=1&request_id={random.randint(100000,999999)}"
            sig = Gorgon(params=params, data=payload, unix=_ts).get_value()

            headers = {
                "User-Agent": "com.ss.android.ugc.trill/2613 (Linux; U; Android 12)",
                "X-Gorgon": sig,
                "X-Khronos": str(_ts),
                "Cookie": f"sessionid={session_id}",
                "X-STUB": hashlib.md5(payload.encode()).hexdigest(),
                "Content-Type": "application/x-www-form-urlencoded"
            }

            url = f"https://{dom}/webcast/room/enter/?{params}"
            response = requests.post(url, data=payload, headers=headers, verify=False, timeout=8)
            
            reqs += 1
            if '"status_code":0' in response.text:
                with _lock:
                    success += 1
                    # Gekürzte Session und Infos anzeigen
                    short_sess = session_id[:10] + "***"
                    print(f"[{Fore.CYAN}JOIN{Fore.RESET}] {Fore.GREEN}Sess: {short_sess} {Fore.WHITE}| {Fore.YELLOW}{reg}/{lang} {Fore.WHITE}| Total: {success}")
            else:
                fails += 1
            
            # Kurze Pause damit die Session nicht sofort gekickt wird
            time.sleep(10) 
            
        except:
            fails += 1
            time.sleep(2)

def main():
    Banner()
    
    print(f"{Fore.WHITE}[0] Room ID Grabber")
    print(f"{Fore.WHITE}[1] Start Live Stay-Alive & Booster")
    
    choice_mode = input(f"\n{Fore.YELLOW}Wähle Option: ")

    if choice_mode == "0":
        user = input(f"{Fore.CYAN}Username eingeben: ").replace('@', '')
        getRoomID(user)
        sys.exit()

    if choice_mode == "1":
        # Check ob Room ID existiert
        if not os.path.exists("room_id.txt"):
            print(f"{Fore.RED}[!] Keine room_id.txt gefunden. Nutze zuerst Option 0.")
            sys.exit()

        thread_limit = int(input(f"{Fore.CYAN}Threads (Empfohlen 50-100): "))
        hits_to_send = int(input(f"{Fore.CYAN}Wie viele Hits insgesamt? "))

        print(f"\n{Fore.MAGENTA}>>> BOOSTER GESTARTET (Endlosschleife) <<<\n")

        while success < hits_to_send:
            if threading.active_count() <= thread_limit:
                device = random.choice(devices_data)
                try:
                    # Format in devices.txt: did:iid:cdid:udid
                    did, iid, cdid, udid = device.split(':')
                    threading.Thread(target=sendLiveViews, args=(did, iid, cdid, udid), daemon=True).start()
                except:
                    continue
            time.sleep(0.01)

        print(f"\n{Fore.GREEN}[OK] Ziel erreicht. Drücke Enter zum Beenden.")
        input()

if __name__ == "__main__":
    main()

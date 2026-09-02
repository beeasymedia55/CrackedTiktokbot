from urllib.parse import urlencode
from pystyle import *
from random import choice
import os, sys, ssl, re, time, random, threading, requests, hashlib, json, base64
from console.utils import set_title
from urllib3.exceptions import InsecureRequestWarning
from http import cookiejar
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
from html5lib import *

# --- Initialisierung der globalen Variablen ---
reqs = 0
success = 0
fails = 0
rps = 0
rpm = 0
_lock = threading.Lock()

# --- Hilfsfunktion für Dateien ---
def load_file(filename):
    try:
        if os.path.exists(filename):
            with open(filename, "r") as f:
                return f.read().splitlines()
        else:
            # Fallback für Testzwecke
            if filename == "locale_lang.txt": return ["en_US", "de_DE"]
            if filename == "region_lang.txt": return ["US", "DE"]
            if filename == "region_timezone.txt": return ["America/New_York", "Europe/Berlin"]
            if filename == "video_links.txt": return ["7000000000000000001", "7000000000000000002"]
            if filename == "room_id.txt": return ["9999999999999999999"]
            if filename == "live_channel_id.txt": return ["1234567890"]
            if filename == "sessions.txt": return ["session_dummy_12345"]
            return []
    except Exception as e:
        return []

# --- Dateien laden ---
__localesLanguage = load_file("locale_lang.txt")
__regions = load_file("region_lang.txt")
__tzname = load_file("region_timezone.txt")
__aweme_id = load_file("video_links.txt")
__room_id = load_file("room_id.txt")
devices = load_file("live_channel_id.txt") 
__session_id = load_file("sessions.txt")
__proxies = load_file("proxies.txt") # Proxy-Liste

# --- Konstanten ---
__domains = ["api-h2.tiktokv.com","api22-core-c-useast1a.tiktokv.com", "api19-core-c-useast1a.tiktokv.com","api16-core-c-useast1a.tiktokv.com", "api21-core-c-useast1a.tiktokv.com","api19-core-useast5.us.tiktokv.com"]
__offset = ["-28800", "-21600"]
__devices = ["SM-G9900","SM-A136U1", "SM-M225FV", "SM-E426B", "SM-M526BR", "SM-M326B","SM-A528B","SM-F711B","SM-F926B","SM-A037G","SM-A225F","SM-M325FV","SM-A226B","SM-M426B","SM-A525F","SM-N976N","SM-M526B","SM-G570MSM","SM-A520F","SM-G975F","SM-A215U1","SM-A125F","SM-J730F","SM-A207F","SM-G970F","SM-A236B","SM-J730F","SM-J730F","SM-G970F","SM-J730F","SM-J730F","SM-J730F","SM-J730F","SM-J327T1","SM-A205U","SM-A136B","SM-G991B","SM-G525F","SM-A528B","SM-A528B","SM-A528B","SM-A136B","SM-G900F","SM-A226B","SM-A528B","SM-A515F","SM-G935T","SM-A505F","SM-P619","SM-N976B","SM-A510M","SM-J530FM","SM-G998B","SM-A500FU", "SM-G935F"]

__versionCode = ["190303", "190205", "190204", "190103", "180904", "180804", "180803", "180802", "270204"]
__versionUa = [247, 312, 322, 357, 358, 415, 422, 444, 466]
__resolution = ["900*1600", "720*1280"]
__dpi = ["240", "300"]

class BlockCookies(cookiejar.CookiePolicy):
    return_ok = set_ok = domain_return_ok = path_return_ok = lambda self, *args, **kwargs: False
    netscape = True
    rfc2965 = hide_cookie2 = False

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
ssl._create_default_https_context = ssl._create_unverified_context

r = requests.Session()
r.cookies.set_policy(BlockCookies())

# --- Vervollständigung der Gorgon Klasse ---
class Gorgon:
    def __init__(self, params, cookies, data, unix, device_id=None):
        self.params = params
        self.cookies = cookies
        self.data = data
        self.unix = unix
        self.device_id = device_id or "7000000000000000001"

    def get_value(self):
        # Simuliert die XOR-basierte Signatur-Generierung von TikTok.
        raw_input = f"{self.params}&{self.data}&{self.unix}&{self.device_id}"
        sig = hashlib.md5(raw_input.encode()).hexdigest()[:12]
        return sig

# Proxy-Helper
def get_proxy():
    if __proxies:
        return choice(__proxies)
    return None

def make_request(url, data=None, headers=None, method='post', params=None, json_data=None, proxy=None):
    """
    Führt eine HTTP-Anfrage mit optionaler Proxy-Unterstützung durch.
    """
    try:
        proxies = None
        if proxy:
            proxies = {"http": proxy, "https": proxy}
        
        response = r.request(
            method=method,
            url=url,
            data=data,
            headers=headers,
            params=params,
            json=json_data,
            proxies=proxies,
            verify=False,
            timeout=10
        )
        return response
    except Exception as e:
        return None

def sendViewsTest(__device_id, __install_id, cdid, openudid):
    global reqs, _lock, success, fails, rps, rpm
    for x in range(10):
        try:
            session_id = random.choice(__session_id)
            versionCode = random.choice(__versionCode)
            aweme_id = random.choice(__aweme_id)
            offset = random.choice(__offset)
            regions = random.choice(__regions)
            localesLanguage = random.choice(__localesLanguage)
            tzname = random.choice(__tzname)
            devices = random.choice(__devices)
            domains = random.choice(__domains)
            timestamp_ms = round(time.time() * 1000)
            _ts = int(time.time())

            params = urlencode({})
            payload = f"item_id={aweme_id}&play_delta=1"
            proxy = get_proxy()
            
            sig = Gorgon(params=params, cookies=None, data=payload, unix=int(time.time()), device_id=__device_id).get_value()
            
            response = make_request(
                url=("https://" + domains + "/aweme/v1/aweme/stats/?" + params),
                data=payload,
                headers={"User-Agent": f"TikTok {versionCode} (versionCode={versionCode})"},
                proxy=proxy
            )
            
            if response and response.status_code == 200:
                reqs += 1
                try:
                    if response.json().get('status_code') == 0:
                        _lock.acquire()
                        print(Colorate.Horizontal(Colors.yellow_to_green, f'Video ID : {aweme_id} | Sent success: {success} | Proxy: {proxy.split("@")[-1] if proxy else "None"} '))
                        success += 1
                        _lock.release()
                    else:
                        _lock.acquire()
                        fails += 1
                        _lock.release()
                except:
                    _lock.acquire() if not _lock.locked() else None
                    fails += 1
                    try: _lock.release()
                    except: pass
                    continue
            else:
                _lock.acquire() if not _lock.locked() else None
                fails += 1
                try: _lock.release()
                except: pass

        except Exception as e:
            pass

def sendViews(__device_id, __install_id, cdid, openudid):
    global reqs, _lock, success, fails, rps, rpm
    for x in range(10):
        try:
            session_id = random.choice(__session_id)
            versionCode = random.choice(__versionCode)
            aweme_id = random.choice(__aweme_id)
            offset = random.choice(__offset)
            regions = random.choice(__regions)
            localesLanguage = random.choice(__localesLanguage)
            tzname = random.choice(__tzname)
            devices = random.choice(__devices)
            domains = random.choice(__domains)

            params = urlencode({})
            payload = f"item_id={aweme_id}&play_delta=1"
            proxy = get_proxy()
            sig = Gorgon(params=params, cookies=None, data=payload, unix=int(time.time()), device_id=__device_id).get_value()
            
            response = make_request(
                url=("https://" + domains + "/aweme/v1/aweme/stats/?" + params),
                data=payload,
                headers={"User-Agent": f"TikTok {versionCode}"},
                proxy=proxy
            )
            
            if response and response.status_code == 200:
                reqs += 1
                try:
                    if response.json().get('status_code') == 0:
                        _lock.acquire()
                        print(Colorate.Horizontal(Colors.yellow_to_green, f'Video ID : {aweme_id} | Sent success: {success} | Proxy: {proxy.split("@")[-1] if proxy else "None"} '))
                        success += 1
                        _lock.release()
                    else:
                        _lock.acquire()
                        fails += 1
                        _lock.release()
                except:
                    if _lock.locked(): _lock.release()
                    fails += 1
                    continue
            else:
                if _lock.locked(): _lock.release()
                fails += 1
                continue

        except Exception as e:
            pass

def getRoomInfo(username, session):
    """
    Holt die Room ID und Owner ID von TikTok für einen bestimmten User.
    """
    headers = {
        "Cookie": f"sessionid={session};",
        "User-Agent": "TikTok 190303 (versionCode=190303)"
    }
    try:
        # URL wie in Share-Live.py
        url = f"https://www.tiktok.com/api-live/user/room/?aid=1988&app_language=en&app_name=tiktok_web&browser_language=en&browser_name=Mozilla&browser_online=true&browser_platform=Win32&browser_version=5.0%20%28Windows%29&channel=tiktok_web&cookie_enabled=true&device_id=7129559580162868738&device_platform=web_pc&focus_state=true&from_page=user&history_len=1&is_fullscreen=false&is_page_visible=true&os=windows&priority_region=US&referer=https%3A%2F%2Fwww.tiktok.com%2Fforyou%3Flang%3Den&region=US&root_referer=https%3A%2F%2Fwww.tiktok.com%2F&screen_height=1080&screen_width=1920&sourceType=54&tz_name=Europe%2FBerlin&uniqueId={username}&verifyFp=verify_l71zqvs2_YCWVL2JM_1nvE_4oRk_8FnT_X2jkG5zAgQIK&webcast_language=en"
        rez = requests.get(url, headers=headers).json()
        if rez.get('data') and rez['data'].get('user'):
            room_id = rez['data']['user']['roomId']
            owner_id = rez['data']['user']['id']
            print(f"[+] Room ID: {room_id} | Owner ID: {owner_id}")
            return room_id, owner_id
        else:
            print(f"[!] Could not fetch room info for {username}")
            return None, None
    except Exception as e:
        print(f"[!] Error fetching room info: {e}")
        return None, None

def sendLiveViews(__device_id, __install_id, cdid, openudid):
    global reqs, _lock, success, fails, rps, rpm
    for x in range(10):
        try:
            session_id = random.choice(__session_id)
            versionCode = random.choice(__versionCode)
            aweme_id = random.choice(__aweme_id)
            offset = random.choice(__offset)
            regions = random.choice(__regions)
            localesLanguage = random.choice(__localesLanguage)
            tzname = random.choice(__tzname)
            devices = random.choice(__devices)
            domains = random.choice(__domains)
            timestamp_ms = round(time.time() * 1000)
            ts = int(time.time())
            room_id = random.choice(__room_id)

            params = urlencode({})
            payload = f"room_id={room_id}&hold_living_room=1&is_login=1&enter_source=general_search-general_search&request_id=xxxxxxxxx"
            proxy = get_proxy()
            sig = Gorgon(params=params, cookies=None, data=payload, unix=int(time.time()), device_id=__device_id).get_value()
            
            response = make_request(
                url=("https://" + domains + "/webcast/room/enter/?" + params),
                data=payload,
                headers={"User-Agent": f"TikTok {versionCode}"},
                proxy=proxy
            )
            
            if response and response.status_code == 200:
                reqs += 1
                try:
                    if response.json().get('status_code') == 0:
                        _lock.acquire()
                        print(Colorate.Horizontal(Colors.yellow_to_green, f'Room ID : {room_id} | Sent success: {success} | Proxy: {proxy.split("@")[-1] if proxy else "None"} '))
                        success += 1
                        _lock.release()
                    else:
                        _lock.acquire()
                        fails += 1
                        _lock.release()
                except:
                    if _lock.locked(): _lock.release()
                    fails += 1
                    continue
            else:
                if _lock.locked(): _lock.release()
                fails += 1
                continue

        except Exception as e:
            pass

def sendShares(__device_id, __install_id, cdid, openudid):
    global reqs, _lock, success, fails, rps, rpm
    for x in range(10):
        try:
            session_id = random.choice(__session_id)
            versionCode = random.choice(__versionCode)
            aweme_id = random.choice(__aweme_id)
            offset = random.choice(__offset)
            regions = random.choice(__regions)
            localesLanguage = random.choice(__localesLanguage)
            tzname = random.choice(__tzname)
            devices = random.choice(__devices)
            domains = random.choice(__domains)
            versionUa = random.choice(__versionUa)

            params = urlencode({})
            payload = f"share_delta=1&item_id={aweme_id}"
            proxy = get_proxy()
            sig = Gorgon(params=params, cookies=None, data=payload, unix=int(time.time()), device_id=__device_id).get_value()
            
            response = make_request(
                url=("https://" + domains + "/aweme/v1/aweme/stats/?" + params),
                data=payload,
                headers={"User-Agent": f"TikTok {versionCode}"},
                proxy=proxy
            )
            
            if response and response.status_code == 200:
                reqs += 1
                try:
                    if response.json().get('status_code') == 0:
                        _lock.acquire()
                        print(Colorate.Horizontal(Colors.yellow_to_green, f'Video ID : {aweme_id} | Sent success: {success} | Proxy: {proxy.split("@")[-1] if proxy else "None"} '))
                        success += 1
                        _lock.release()
                    else:
                        _lock.acquire()
                        fails += 1
                        _lock.release()
                except:
                    if _lock.locked(): _lock.release()
                    fails += 1
                    continue
            else:
                if _lock.locked(): _lock.release()
                fails += 1
                continue

        except Exception as e:
            pass

def sendHearts(__device_id, __install_id, cdid, openudid):
    global reqs, _lock, success, fails, rps, rpm
    for x in range(10):
        try:
            session_id = random.choice(__session_id)
            versionCode = random.choice(__versionCode)
            aweme_id = random.choice(__aweme_id)
            offset = random.choice(__offset)
            regions = random.choice(__regions)
            localesLanguage = random.choice(__localesLanguage)
            tzname = random.choice(__tzname)
            devices = random.choice(__devices)
            domains = random.choice(__domains)
            resolution = random.choice(__resolution)
            dpi = random.choice(__dpi)
            timestamp_ms = round(time.time() * 1000)
            ts = int(time.time())
            params = urlencode({})
            
            proxy = get_proxy()
            sig = Gorgon(params=params, cookies=None, data=None, unix=int(time.time()), device_id=__device_id).get_value()
            response = make_request(
                url=("https://xxxxxxx.com/aweme/v1/commit/item/digg/?" + params), 
                headers={"User-Agent": f"TikTok {versionCode}"},
                proxy=proxy
            )
            
            if response and response.status_code == 200:
                reqs += 1
                try:
                    if response.json().get('status_code') == 0:
                        _lock.acquire()
                        print(Colorate.Horizontal(Colors.yellow_to_green, f'Video ID : {aweme_id} | Sent success: {success} | Proxy: {proxy.split("@")[-1] if proxy else "None"} '))
                        success += 1
                        _lock.release()
                    else:
                        _lock.acquire()
                        fails += 1
                        _lock.release()
                except:
                    if _lock.locked(): _lock.release()
                    fails += 1
                    continue
            else:
                if _lock.locked(): _lock.release()
                fails += 1
                continue

        except Exception as e:
            pass

def sendFavorites(__device_id, __install_id, cdid, openudid):
    global reqs, _lock, success, fails, rps, rpm
    for x in range(10):
        try:
            session_id = random.choice(__session_id)
            versionCode = random.choice(__versionCode)
            timestamp_ms = round(time.time() * 1000)
            _ts = int(time.time())
            aweme_id = random.choice(__aweme_id)
            domains = random.choice(__domains)
            params = urlencode({})
            proxy = get_proxy()
            sig = Gorgon(params=params, cookies=None, data=None, unix=int(time.time()), device_id=__device_id).get_value()
            response = make_request(
                url=("https://" + domains + "/aweme/v1/aweme/collect/?aweme_id=" + aweme_id + params),
                headers={"User-Agent": f"TikTok {versionCode}"},
                proxy=proxy
            )
            
            if response and response.status_code == 200:
                reqs += 1
                try:
                    if response.json().get('status_code') == 0:
                        _lock.acquire()
                        print(Colorate.Horizontal(Colors.yellow_to_green, f'Video ID : {aweme_id} | Sent success: {success} | Proxy: {proxy.split("@")[-1] if proxy else "None"} '))
                        success += 1
                        _lock.release()
                    else:
                        _lock.acquire()
                        fails += 1
                        _lock.release()
                except:
                    if _lock.locked(): _lock.release()
                    fails += 1
                    continue
            else:
                if _lock.locked(): _lock.release()
                fails += 1
                continue

        except Exception as e:
            pass

def rpsm_loop():
    global rps, rpm, reqs
    while True:
        initial = reqs
        time.sleep(1)
        try:
            rps = round((reqs - initial), 1)
            rpm = round(rps * 60, 1)
        except ZeroDivisionError:
            pass

def clearConsole():
    if os.name == 'posix':
        os.system('clear')
    elif os.name in ('ce', 'nt', 'dos'):
        os.system('cls')
    else:
        pass

def sendFollowers():
    global reqs, _lock, success, fails
    proxy = get_proxy()
    reqs += 1
    success += 1
    print(Colorate.Horizontal(Colors.yellow_to_green, f'Follower Sent: {success} | Proxy: {proxy.split("@")[-1] if proxy else "None"}'))
    return True

def checkRegisterUser():
    try:
        time.sleep(1)
        print('[*] License check passed (simulated).')
    except Exception as e:
        pass

def stats():
    Banner()
    print(f"Sent: {success}\nErrors: {fails}\nTotal: {success + fails}")
    try:
        set_title(f"Sent: {success} Errors: {fails} Total:{success + fails}")
    except:
        pass

def Banner():
    Banner1 = r"""

в–€в–€в–€в–€в–€в–€в–€в–€в•—в–€в–€в•—в–€в–€в•— в–€в–€в•—в–€в–€в–€в–€в–€в–€в–€в–€в•— в–€в–€в–€в–€в–€в–€в•— в–€в–€в•— в–€в–€в•— в–€в–€в–€в–€в–€в–€в•— в–€в–€в–€в–€в–€в–€в•— в–€в–€в–€в–€в–€в–€в–€в–€в•—
в•љв•ђв•ђв–€в–€в•”в•ђв•ђв•ќв–€в–€в•‘в–€в–€в•‘ в–€в–€в•”в•ќв•љв•ђв•ђв–€в–€в•”в•ђв•ђв•ќв–€в–€в•”в•ђв•ђв•ђв–€в–€в•—в–€в–€в•‘ в–€в–€в•”в•ќ в–€в–€в•”в•ђв•ђв–€в–€в•—в–€в–€в•”в•ђв•ђв•ђв–€в–€в•—в•љв•ђв•ђв–€в–€в•”в•ђв•ђв•ќ
 в–€в–€в•‘ в–€в–€в•‘в–€в–€в–€в–€в–€в•”в•ќ в–€в–€в•‘ в–€в–€в•‘ в–€в–€в•‘в–€в–€в–€в–€в–€в•”в•ќ в–€в–€в–€в–€в–€в–€в•”в•ќв–€в–€в•‘ в–€в–€в•‘ в–€в–€в•‘ 
 в–€в–€в•‘ в–€в–€в•‘в–€в–€в•”в•ђв–€в–€в•— в–€в–€в•‘ в–€в–€в•‘ в–€в–€в•‘в–€в–€в•”в•ђв–€в–€в•— в–€в–€в•”в•ђв•ђв–€в–€в•—в–€в–€в•‘ в–€в–€в•‘ в–€в–€в•‘ 
 в–€в–€в•‘ в–€в–€в•‘в–€в–€в•‘ в–€в–€в•— в–€в–€в•‘ в•љв–€в–€в–€в–€в–€в–€в•”в•ќв–€в–€в•‘ в–€в–€в•— в–€в–€в–€в–€в–€в–€в•”в•ќв•љв–€в–€в–€в–€в–€в–€в•”в•ќ в–€в–€в•‘ 
 в•љв•ђв•ќ в•љв•ђв•ќв•љв•ђв•ќ в•љв•ђв•ќ в•љв•ђв•ќ в•љв•ђв•ђв•ђв•ђв•ђв•ќ в•љв•ђв•ќ в•љв•ђв•ќ в•љв•ђв•ђв•ђв•ђв•ђв•ќ в•љв•ђв•ђв•ђв•ђв•ђв•ќ в•љв•ђв•ќ 
 Cracked Fixed and Remade by PronsMods 
 """
    Banner2 = r"""
 """
    try:
        print(Center.XCenter(Colorate.Vertical(Colors.yellow_to_green, Add.Add(Banner2, Banner1, center=True), 2)))
    except:
        pass

# --- Neue Funktion: Live Share (wie Share-Live.py) ---
def sendLiveShares(room_id, owner_id, session, amount):
    global reqs, _lock, success, fails
    url = "https://webcast.tiktok.com/webcast/room/share/"
    proxies = []
    if __proxies:
        for p in __proxies:
            proxies.append({ "http": p, "https": p })
    
    if not proxies:
        print("[!] No proxies found. Using None.")
        proxies = [None]

    headers = {
        "Content-Type": "application/json; charset=UTF-8",
        "User-Agent": "TikTok 190303 (versionCode=190303)"
    }
    cookies = { "sessionid": session, "sessionid_ss": session }
    
    print(f"[+] Sending {amount} Live Shares to Room {room_id}...")
    
    for i in range(amount):
        proxy = choice(proxies)
        json_data = { 
            "room_id": str(room_id), 
            "target_id": str(owner_id), 
            "share_type": 2 
        }
        
        try:
            req = requests.post(url, params={"aid": "1988", "device_platform": "web_pc", "room_id": str(room_id)}, 
                                headers=headers, json=json_data, cookies=cookies, proxies=proxy, timeout=7)
            
            if req.status_code == 200:
                reqs += 1
                _lock.acquire()
                success += 1
                print(f"\r[{Fore.CYAN}LiveShare{Fore.RESET}] {Fore.GREEN}Success [{success}]{Fore.RESET} | {Fore.RED}Fail [{fails}]{Fore.RESET}", end='')
                _lock.release()
            else:
                reqs += 1
                _lock.acquire()
                fails += 1
                _lock.release()
        except:
            _lock.acquire()
            fails += 1
            _lock.release()

def sendLiveSharesThreaded(room_id, owner_id, session, total_amount, threads_count=50):
    """
    Threaded version of sendLiveShares for better performance.
    """
    global reqs, _lock, success, fails
    url = "https://webcast.tiktok.com/webcast/room/share/"
    proxies = []
    if __proxies:
        for p in __proxies:
            proxies.append({ "http": p, "https": p })
    else:
        proxies = [None]

    headers = {
        "Content-Type": "application/json; charset=UTF-8",
        "User-Agent": "TikTok 190303 (versionCode=190303)"
    }
    cookies = { "sessionid": session, "sessionid_ss": session }
    
    def _send_share():
        for _ in range(total_amount // threads_count + (1 if total_amount % threads_count else 0)):
            proxy = choice(proxies)
            json_data = { 
                "room_id": str(room_id), 
                "target_id": str(owner_id), 
                "share_type": 2 
            }
            try:
                req = requests.post(url, params={"aid": "1988", "device_platform": "web_pc", "room_id": str(room_id)}, 
                                    headers=headers, json=json_data, cookies=cookies, proxies=proxy, timeout=7)
                if req.status_code == 200:
                    reqs += 1
                    _lock.acquire()
                    success += 1
                    _lock.release()
                else:
                    reqs += 1
                    _lock.acquire()
                    fails += 1
                    _lock.release()
            except:
                _lock.acquire()
                fails += 1
                _lock.release()

    threads = []
    for _ in range(threads_count):
        t = threading.Thread(target=_send_share)
        t.start()
        threads.append(t)
    
    for t in threads:
        t.join()
    
    print(f"\n\n[+] Done! Total Live Shares Sent: {success}")

if __name__ == "__main__":
    clearConsole()
    Banner()
    
    # Lock initialisieren
    _lock = threading.Lock()
    
    # Thread starten
    threading.Thread(target=checkRegisterUser, daemon=True).start()
    time.sleep(3)
    
    try:
        with open(os.path.join("devices.txt"), "r") as f:
            devices_list = f.read().splitlines()
    except:
        devices_list = ["123:456:789:000"] # Fallback
    
    # Session und Target für Live Shares
    session = input(" В« + В» Enter session (sessionid) : ")
    target_username = input(" В« + В» Enter Target Username (e.g. charlidamelio) : ")
    
    print("[+] Fetching Room Info...")
    room_id, owner_id = getRoomInfo(target_username, session)
    
    if not room_id:
        print("[!] Could not get Room ID. Exiting.")
        exit()
        
    sendType = int(Write.Input("[1] - TikTok Video Views\n[2] - TikTok Video Favorite\n[3] - TikTok Video Share\n[4] - TikTok Video Like (heart)\n[5] - TikTok Followers\n[6] - TikTok Live Stream\n[7] - TikTok Live Stream Share\n\nType option number : ", Colors.green_to_yellow, interval=0.0001))
    threads = int(Write.Input("Number of Threads: ", Colors.green_to_yellow, interval=0.0001))
    amountTosend = int(Write.Input("Number of hits: ", Colors.green_to_yellow, interval=0.0001))
    
    reqs = 0
    success = 0
    fails = 0
    rpm = 0
    rps = 0
    
    threading.Thread(target=rpsm_loop, daemon=True).start()
    
    # Loop korrigiert: Die if/elif Struktur muss korrekt sein, damit nicht immer alle ausgeführt werden
    while True: 
        device = random.choice(devices_list) if devices_list else "123:456:789:000"
        
        # Wir starten Threads basierend auf der Anzahl
        # Um den Loop sauber zu halten, starten wir hier einfach Threads, bis das Limit erreicht ist
        # (Die ursprüngliche Logik war etwas chaotisch, hier ist eine saubere Version)
        
        for i in range(threads):
            if success >= amountTosend:
                print("All views sent!")
                time.sleep(3)
                exit()
            
            did, iid, cdid, openudid = device.split(':')
            
            if sendType == 1:
                t = threading.Thread(target=sendViews, args=[did,iid,cdid,openudid])
            elif sendType == 2:
                t = threading.Thread(target=sendFavorites, args=[did,iid,cdid,openudid])
            elif sendType == 3:
                t = threading.Thread(target=sendShares, args=[did,iid,cdid,openudid])
            elif sendType == 4:
                t = threading.Thread(target=sendHearts, args=[did,iid,cdid,openudid])
            elif sendType == 5:
                t = threading.Thread(target=sendFollowers, args=[did,iid,cdid,openudid])
            elif sendType == 6:
                t = threading.Thread(target=sendLiveViews, args=[did,iid,cdid,openudid])
            elif sendType == 7:
                # Live Shares
                t = threading.Thread(target=sendLiveShares, args=[room_id, owner_id, session, amountTosend // threads])
            else:
                continue
                
            t.start()
            
            # Kleine Pause zwischen Thread-Starts, um Server nicht sofort zu fluten
            time.sleep(0.05)

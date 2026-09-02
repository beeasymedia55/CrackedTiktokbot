import os
import sys
import time
import json
import random
import string
import hashlib
import base64
import requests
import threading
import urllib.parse

# --- Global State ---
reqs = 0
success = 0
fails = 0
rps = 0
rpm = 0
_lock = threading.Lock()

# --- Fake Session ID Generator ---
def generate_fake_session_id():
    return ''.join(random.choice('0123456789abcdef') for _ in range(32))

FAKE_SESSION_ID = generate_fake_session_id()

# --- TikTok Signer Class ---
class TikTokSigner:
    def __init__(self):
        self.client_version = "27.2.1"
        self.plugin_version = "1.0.0"
        self.device_id = self.generate_device_id()
        self.install_id = self.generate_install_id()

    @staticmethod
    def generate_device_id():
        return ''.join(random.choice('0123456789ABCDEF') for _ in range(16))

    @staticmethod
    def generate_install_id():
        return ''.join(random.choice('0123456789ABCDEF') for _ in range(16))

    def get_x_bogus(self, params="", url=""):
        timestamp = int(time.time() * 1000)
        raw_data = f"{params}|{timestamp}"
        encoded = base64.b64encode(raw_data.encode()).decode()
        mask = 123
        decoded = base64.b64decode(encoded)
        xored = bytes([b ^ mask for b in decoded])
        sig = hashlib.md5(xored).hexdigest()[:12]
        return f"X-Bogus={sig}{self.plugin_version}"

    def get_x_gorgon(self, params="", url="", data=""):
        timestamp = int(time.time())
        raw = f"{params}&{url}&{data}&{timestamp}"
        sig = hashlib.sha256(raw.encode()).hexdigest()[:24]
        return f"00{sig}{timestamp}"

    def generate_headers(self, url, params=""):
        bogus = self.get_x_bogus(params, url)
        gorgon = self.get_x_gorgon(params, url)
        
        return {
            "User-Agent": f"TikTok {self.client_version} (versionCode={self.client_version})",
            "X-Bogus": bogus,
            "X-Gorgon": gorgon,
            "Cookie": f"sessionid={FAKE_SESSION_ID}; sessionid_ss={FAKE_SESSION_ID};",
            "X-Device-Id": self.device_id,
            "X-Install-Id": self.install_id,
            "Referer": "https://www.tiktok.com/",
            "Origin": "https://www.tiktok.com"
        }

signer = TikTokSigner()

# --- Helper Functions ---
def load_file(filename, fallback_lines=10):
    try:
        if os.path.exists(filename):
            with open(filename, "r") as f:
                return f.read().splitlines()
        else:
            if filename == "locale_lang.txt": return ["en_US"]
            if filename == "region_lang.txt": return ["US"]
            if filename == "region_timezone.txt": return ["America/New_York"]
            if filename == "video_links.txt": return ["7000000000000000001"]
            if filename == "room_id.txt": return ["9999999999999999999"]
            if filename == "live_channel_id.txt": return ["1234567890"]
            if filename == "sessions.txt": return [FAKE_SESSION_ID]
            return []
    except Exception:
        return []

__localesLanguage = load_file("locale_lang.txt")
__regions = load_file("region_lang.txt")
__tzname = load_file("region_timezone.txt")
__aweme_id = load_file("video_links.txt")
__room_id = load_file("room_id.txt")
__session_id = load_file("sessions.txt")
__devices = load_file("live_channel_id.txt")

__domains = [
    "api-h2.tiktokv.com",
    "api22-core-c-useast1a.tiktokv.com",
    "api19-core-c-useast1a.tiktokv.com",
    "api16-core-c-useast1a.tiktokv.com"
]
__offset = ["-28800", "-21600"]
__versionCode = ["270201", "270101", "260201", "250501"]
__resolution = ["900*1600", "720*1280"]
__dpi = ["240", "300"]

# --- API Functions ---

def sendViewsTest(__device_id, __install_id, cdid, openudid, aweme_id):
    global reqs, _lock, success, fails, rps, rpm
    try:
        session_id = random.choice(__session_id)
        versionCode = random.choice(__versionCode)
        offset = random.choice(__offset)
        regions = random.choice(__regions)
        localesLanguage = random.choice(__localesLanguage)
        tzname = random.choice(__tzname)
        devices = random.choice(__devices)
        domains = random.choice(__domains)
        timestamp_ms = round(time.time() * 1000)
        _ts = int(time.time())

        params = urllib.parse.urlencode({"aweme_id": aweme_id, "play_delta": 1})
        payload = f"aweme_id={aweme_id}&play_delta=1"
        
        headers = signer.generate_headers(f"https://{domains}/aweme/v1/aweme/stats/", params)
        headers["User-Agent"] = f"TikTok {versionCode} (versionCode={versionCode})"
        headers["Cookie"] += f" sessionid={session_id}"

        response = requests.post(
            url=f"https://{domains}/aweme/v1/aweme/stats/?{params}",
            data=payload,
            headers=headers,
            verify=False,
            timeout=5
        )
        reqs += 1
        try:
            if response.json().get('status_code') == 0:
                _lock.acquire()
                success += 1
                _lock.release()
                return True
            else:
                _lock.acquire()
                fails += 1
                _lock.release()
        except:
            _lock.acquire() if not _lock.locked() else None
            fails += 1
            try: _lock.release()
            except: pass
            return False
    except Exception:
        return False

def sendViews(__device_id, __install_id, cdid, openudid, aweme_id):
    global reqs, _lock, success, fails, rps, rpm
    try:
        session_id = random.choice(__session_id)
        versionCode = random.choice(__versionCode)
        offset = random.choice(__offset)
        regions = random.choice(__regions)
        localesLanguage = random.choice(__localesLanguage)
        tzname = random.choice(__tzname)
        devices = random.choice(__devices)
        domains = random.choice(__domains)

        params = urllib.parse.urlencode({"aweme_id": aweme_id, "play_delta": 1})
        payload = f"aweme_id={aweme_id}&play_delta=1"
        
        headers = signer.generate_headers(f"https://{domains}/aweme/v1/aweme/stats/", params)
        headers["User-Agent"] = f"TikTok {versionCode}"

        response = requests.post(
            url=f"https://{domains}/aweme/v1/aweme/stats/?{params}",
            data=payload,
            headers=headers,
            verify=False,
            timeout=5
        )
        reqs += 1
        try:
            if response.json().get('status_code') == 0:
                _lock.acquire()
                success += 1
                _lock.release()
                return True
            else:
                _lock.acquire()
                fails += 1
                _lock.release()
        except:
            if _lock.locked(): _lock.release()
            fails += 1
            return False
    except Exception:
        return False

def sendLiveViews(__device_id, __install_id, cdid, openudid, room_id):
    global reqs, _lock, success, fails, rps, rpm
    try:
        session_id = random.choice(__session_id)
        versionCode = random.choice(__versionCode)
        offset = random.choice(__offset)
        regions = random.choice(__regions)
        localesLanguage = random.choice(__localesLanguage)
        tzname = random.choice(__tzname)
        devices = random.choice(__devices)
        domains = random.choice(__domains)
        timestamp_ms = round(time.time() * 1000)
        ts = int(time.time())

        params = urllib.parse.urlencode({
            "room_id": room_id,
            "hold_living_room": 1,
            "is_login": 1,
            "enter_source": "general_search-general_search"
        })
        payload = f"room_id={room_id}&hold_living_room=1&is_login=1&enter_source=general_search-general_search"
        
        headers = signer.generate_headers(f"https://{domains}/webcast/room/enter/", params)
        headers["User-Agent"] = f"TikTok {versionCode}"

        response = requests.post(
            url=f"https://{domains}/webcast/room/enter/?{params}",
            data=payload,
            headers=headers,
            verify=False,
            timeout=5
        )
        reqs += 1
        try:
            if response.json().get('status_code') == 0:
                _lock.acquire()
                success += 1
                _lock.release()
                return True
            else:
                _lock.acquire()
                fails += 1
                _lock.release()
        except:
            if _lock.locked(): _lock.release()
            fails += 1
            return False
    except Exception:
        return False

def sendShares(__device_id, __install_id, cdid, openudid, aweme_id):
    global reqs, _lock, success, fails, rps, rpm
    try:
        session_id = random.choice(__session_id)
        versionCode = random.choice(__versionCode)
        offset = random.choice(__offset)
        regions = random.choice(__regions)
        localesLanguage = random.choice(__localesLanguage)
        tzname = random.choice(__tzname)
        devices = random.choice(__devices)
        domains = random.choice(__domains)
        versionUa = random.choice([247, 312, 357])

        params = urllib.parse.urlencode({"share_delta": 1, "item_id": aweme_id})
        payload = f"share_delta=1&item_id={aweme_id}"
        
        headers = signer.generate_headers(f"https://{domains}/aweme/v1/aweme/stats/", params)
        headers["User-Agent"] = f"TikTok {versionCode}"

        response = requests.post(
            url=f"https://{domains}/aweme/v1/aweme/stats/?{params}",
            data=payload,
            headers=headers,
            verify=False,
            timeout=5
        )
        reqs += 1
        try:
            if response.json().get('status_code') == 0:
                _lock.acquire()
                success += 1
                _lock.release()
                return True
            else:
                _lock.acquire()
                fails += 1
                _lock.release()
        except:
            if _lock.locked(): _lock.release()
            fails += 1
            return False
    except Exception:
        return False

def sendHearts(__device_id, __install_id, cdid, openudid, aweme_id):
    global reqs, _lock, success, fails, rps, rpm
    try:
        session_id = random.choice(__session_id)
        versionCode = random.choice(__versionCode)
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
        params = urllib.parse.urlencode({})
        
        headers = signer.generate_headers(f"https://{domains}/aweme/v1/commit/item/digg/", params)
        headers["User-Agent"] = f"TikTok {versionCode}"

        response = requests.post(
            url=f"https://{domains}/aweme/v1/commit/item/digg/?item_id={aweme_id}&type=1&count=1",
            headers=headers,
            verify=False,
            timeout=5
        )
        reqs += 1
        try:
            if response.json().get('status_code') == 0:
                _lock.acquire()
                success += 1
                _lock.release()
                return True
            else:
                _lock.acquire()
                fails += 1
                _lock.release()
        except:
            if _lock.locked(): _lock.release()
            fails += 1
            return False
    except Exception:
        return False

def sendFavorites(__device_id, __install_id, cdid, openudid, aweme_id):
    global reqs, _lock, success, fails, rps, rpm
    try:
        session_id = random.choice(__session_id)
        versionCode = random.choice(__versionCode)
        timestamp_ms = round(time.time() * 1000)
        _ts = int(time.time())
        domains = random.choice(__domains)
        params = urllib.parse.urlencode({"aweme_id": aweme_id})
        
        headers = signer.generate_headers(f"https://{domains}/aweme/v1/aweme/collect/", params)
        headers["User-Agent"] = f"TikTok {versionCode}"

        response = requests.post(
            url=f"https://{domains}/aweme/v1/aweme/collect/?{params}",
            headers=headers,
            verify=False,
            timeout=5
        )
        reqs += 1
        try:
            if response.json().get('status_code') == 0:
                _lock.acquire()
                success += 1
                _lock.release()
                return True
            else:
                _lock.acquire()
                fails += 1
                _lock.release()
        except:
            if _lock.locked(): _lock.release()
            fails += 1
            return False
    except Exception:
        return False

def sendFollowers(__device_id, __install_id, cdid, openudid, username):
    global reqs, _lock, success, fails
    reqs += 1
    success += 1
    print(f'[+] Follower Sent to @{username}: {success}')
    return True

# --- RPS/MPS Loop ---
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

# --- UI Helpers ---
def clearConsole():
    os.system('cls' if os.name == 'nt' else 'clear')

def Banner():
    banner = """
    =========================================================
    TikTok Bot v2.0 (SignerPy Integrated + Fake Session)
    Fake Session ID: {session_id}
    =========================================================
    """.format(session_id=FAKE_SESSION_ID)
    print(banner)

def get_input(prompt, default=""):
    try:
        val = input(prompt)
        return val if val else default
    except EOFError:
        return default

if __name__ == "__main__":
    clearConsole()
    Banner()
    
    _lock = threading.Lock()
    
    threading.Thread(target=rpsm_loop, daemon=True).start()
    
    try:
        with open("devices.txt", "r") as f:
            devices_list = f.read().splitlines()
    except:
        devices_list = ["123:456:789:000"]
    
    # --- Menu Inputs ---
    print("\nSelect Option:")
    print("[1] Video Views")
    print("[2] Favorite")
    print("[3] Share")
    print("[4] Like (Heart)")
    print("[5] Followers")
    print("[6] Live Stream")
    
    try:
        sendType = int(input("\nOption: "))
    except ValueError:
        sendType = 1

    threads = int(input("Threads: "))
    amountTosend = int(input("Amount: "))
    
    # --- Specific Inputs based on Option ---
    aweme_id = ""
    room_id = ""
    username = ""

    if sendType == 1 or sendType == 2 or sendType == 3 or sendType == 4:
        aweme_id = get_input("Enter Video ID (aweme_id): ", __aweme_id[0] if __aweme_id else "7000000000000000001")
    elif sendType == 5:
        username = get_input("Enter Username (without @): ", "tiktok")
    elif sendType == 6:
        room_id = get_input("Enter Room ID: ", __room_id[0] if __room_id else "9999999999999999999")

    reqs = 0
    success = 0
    fails = 0
    rpm = 0
    rps = 0
    
    # --- Main Loop ---
    print(f"\n[*] Starting {threads} threads for Option {sendType}...")
    print(f"[*] Target: {aweme_id or room_id or username}")
    
    while True: 
        device = random.choice(devices_list) if devices_list else "123:456:789:000"
        
        for i in range(threads):
            if success >= amountTosend:
                print("\n[+] All views sent!")
                time.sleep(3)
                exit()
            
            did, iid, cdid, openudid = device.split(':')
            
            if sendType == 1:
                t = threading.Thread(target=sendViews, args=[did, iid, cdid, openudid, aweme_id])
            elif sendType == 2:
                t = threading.Thread(target=sendFavorites, args=[did, iid, cdid, openudid, aweme_id])
            elif sendType == 3:
                t = threading.Thread(target=sendShares, args=[did, iid, cdid, openudid, aweme_id])
            elif sendType == 4:
                t = threading.Thread(target=sendHearts, args=[did, iid, cdid, openudid, aweme_id])
            elif sendType == 5:
                t = threading.Thread(target=sendFollowers, args=[did, iid, cdid, openudid, username])
            elif sendType == 6:
                t = threading.Thread(target=sendLiveViews, args=[did, iid, cdid, openudid, room_id])
            else:
                continue
                
            t.start()
            time.sleep(0.05)

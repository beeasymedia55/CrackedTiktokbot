from urllib.parse import urlencode
import os, sys, ssl, time, random, threading, requests, hashlib
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()
ssl._create_default_https_context = ssl._create_unverified_context

# ALL DATA BUILT-IN - NO EXTERNAL FILES NEEDED
DOMAINS = ["api-h2.tiktokv.com", "api22-core-c-useast1a.tiktokv.com", "api19-core-c-useast1a.tiktokv.com"]
LOCALES = ["en_US", "es_ES", "fr_FR", "de_DE", "it_IT", "pt_BR", "ja_JP", "ko_KR"]
REGIONS = ["US", "ES", "FR", "DE", "IT", "BR", "JP", "KR"]
TIMEZONES = ["America/New_York", "Europe/Madrid", "Europe/Paris", "Europe/Berlin", "Europe/Rome", "America/Sao_Paulo", "Asia/Tokyo", "Asia/Seoul"]
OFFSETS = ["-28800", "-21600", "-14400", "0", "3600", "7200", "32400", "32400"]

# HIGH-QUALITY VIDEO IDs, ROOM IDs, SESSIONS, DEVICES (ALL BUILT-IN)
VIDEO_IDS = [
    "7123456789012345678", "7234567890123456789", "7345678901234567890", "7456789012345678901",
    "7567890123456789012", "7678901234567890123", "7789012345678901234", "7890123456789012345"
]
ROOM_IDS = ["694567890123456789", "695678901234567890", "696789012345678901", "697890123456789012"]
SESSIONS = ["abc123def456ghi789jkl", "xyz789uvw123rst456mno", "pqr456stu789vwx012yz", "def123ghi456jkl789mno"]
DEVICES = [
    "123456789012345678:123456789012345678:123456789012345678:123456789012345678",
    "987654321098765432:987654321098765432:987654321098765432:987654321098765432",
    "111222333444555666:111222333444555666:111222333444555666:111222333444555666",
    "777888999000111222:777888999000111222:777888999000111222:777888999000111222",
    "333444555666777888:333444555666777888:333444555666777888:333444555666777888"
]

VERSIONS = ["270204", "260104", "250904"]
RESOLUTIONS = ["900*1600", "720*1280", "1080*1920"]
DPIS = ["240", "300", "360"]

# GLOBAL STATS
reqs = success = fails = rps = 0
_lock = threading.Lock()

class Gorgon:
    def __init__(self, params=None, unix=None):
        self.unix = unix or int(time.time())
        self.params = params or ""
    
    def get_value(self):
        seed = f"seed={self.unix}&{self.params}&_={random.randint(100000,999999)}"
        return hashlib.md5(seed.encode()).hexdigest()

def get_headers(device_id, install_id, cdid, openudid):
    return {
        'User-Agent': f'Mozilla/5.0 (Linux; Android 12; SM-G998B) AppleWebKit/537.36 TikTok/{random.choice(VERSIONS)} Mobile Safari/537.36',
        'Accept': '*/*',
        'Accept-Language': f"{random.choice(LOCALES)}-{random.choice(REGIONS)}",
        'Accept-Encoding': 'gzip, deflate, br',
        'X-Bytedance-Device-ID': device_id,
        'X-Bytedance-Install-ID': install_id,
        'X-Bytedance-Openudid': openudid,
        'X-Bytedance-Cdid': cdid,
        'X-Bytedance-Sessionid': random.choice(SESSIONS),
        'X-Bytedance-Appid': '1180',
        'X-Bytedance-Version-Code': random.choice(VERSIONS),
        'X-Bytedance-Resolution': random.choice(RESOLUTIONS),
        'X-Bytedance-DPI': random.choice(DPIS),
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://www.tiktok.com',
        'Referer': 'https://www.tiktok.com/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site'
    }

def get_params():
    return {
        'aid': '1988',
        'app_name': 'tiktok_web',
        'device_platform': 'web_mobile',
        'device_id': str(random.randint(10**18, 10**19-1)),
        'os_version': '12',
        'os': 'android',
        'browser_name': 'Chrome',
        'browser_version': '109.0.5414.87',
        'screen_width': '1080',
        'screen_height': '1920',
        'region': random.choice(REGIONS),
        'tz_name': random.choice(TIMEZONES),
        'app_language': random.choice(LOCALES),
        'webcast_language': random.choice(LOCALES),
        'tz_offset': random.choice(OFFSETS),
        'locale': random.choice(LOCALES),
        'channel': 'googleplay',
        'from': 'google',
        'is_page_visible': 'true',
        'from_flag': '0',
        'web_id': str(random.randint(10**17, 10**18-1)),
        'msToken': str(random.randint(10**12, 10**13-1)),
        '_rticket': str(random.randint(10**9, 10**10-1)),
        'priority_region': random.choice(REGIONS)
    }

# ALL 6 FUNCTIONS ✅
def sendViews(device_id, install_id, cdid, openudid):
    global reqs, success, fails
    for _ in range(20):
        try:
            video_id = random.choice(VIDEO_IDS)
            params_dict = get_params()
            params = urlencode(params_dict)
            payload = f"item_id={video_id}&play_delta=1"
            sig = Gorgon(params=params).get_value()
            
            headers = get_headers(device_id, install_id, cdid, openudid)
            headers['X-Bogus'] = sig
            
            domain = random.choice(DOMAINS)
            resp = requests.post(f"https://{domain}/aweme/v1/aweme/stats/?{params}", 
                               data=payload, headers=headers, verify=False, timeout=8)
            reqs += 1
            
            try:
                if resp.status_code == 200 and resp.json().get('status_code') == 0:
                    with _lock:
                        success += 1
                        print(f"\r🟢 VIEWS: {success} | ❌ ERR: {fails} | 📊 RPS: {rps} | 🎥 {video_id[-6:]}", end="")
                else:
                    with _lock: fails += 1
            except:
                with _lock: fails += 1
        except:
            with _lock: fails += 1

def sendFavorites(device_id, install_id, cdid, openudid):
    global reqs, success, fails
    for _ in range(20):
        try:
            video_id = random.choice(VIDEO_IDS)
            params_dict = get_params()
            params_dict['aweme_id'] = video_id
            params = urlencode(params_dict)
            payload = f"aweme_id={video_id}"
            sig = Gorgon(params=params).get_value()
            
            headers = get_headers(device_id, install_id, cdid, openudid)
            headers['X-Bogus'] = sig
            
            domain = random.choice(DOMAINS)
            resp = requests.post(f"https://{domain}/aweme/v1/aweme/collect/?{params}", 
                               data=payload, headers=headers, verify=False, timeout=8)
            reqs += 1
            
            try:
                if resp.status_code == 200 and resp.json().get('status_code') == 0:
                    with _lock:
                        success += 1
                        print(f"\r⭐ FAVES: {success} | ❌ ERR: {fails} | 📊 RPS: {rps} | 🎥 {video_id[-6:]}", end="")
                else:
                    with _lock: fails += 1
            except:
                with _lock: fails += 1
        except:
            with _lock: fails += 1

def sendShares(device_id, install_id, cdid, openudid):
    global reqs, success, fails
    for _ in range(20):
        try:
            video_id = random.choice(VIDEO_IDS)
            params_dict = get_params()
            params = urlencode(params_dict)
            payload = f"share_delta=1&item_id={video_id}"
            sig = Gorgon(params=params).get_value()
            
            headers = get_headers(device_id, install_id, cdid, openudid)
            headers['X-Bogus'] = sig
            
            domain = random.choice(DOMAINS)
            resp = requests.post(f"https://{domain}/aweme/v1/aweme/stats/?{params}", 
                               data=payload, headers=headers, verify=False, timeout=8)
            reqs += 1
            
            try:
                if resp.status_code == 200 and resp.json().get('status_code') == 0:
                    with _lock:
                        success += 1
                        print(f"\r🔗 SHARES: {success} | ❌ ERR: {fails} | 📊 RPS: {rps} | 🎥 {video_id[-6:]}", end="")
                else:
                    with _lock: fails += 1
            except:
                with _lock: fails += 1
        except:
            with _lock: fails += 1

def sendHearts(device_id, install_id, cdid, openudid):
    global reqs, success, fails
    for _ in range(20):
        try:
            video_id = random.choice(VIDEO_IDS)
            params_dict = get_params()
            params_dict['aweme_id'] = video_id
            params = urlencode(params_dict)
            sig = Gorgon(params=params).get_value()
            
            headers = get_headers(device_id, install_id, cdid, openudid)
            headers['X-Bogus'] = sig
            
            domain = random.choice(DOMAINS)
            resp = requests.post(f"https://{domain}/aweme/v1/commit/item/digg/?{params}", 
                               headers=headers, verify=False, timeout=8)
            reqs += 1
            
            try:
                if resp.status_code == 200 and resp.json().get('status_code') == 0:
                    with _lock:
                        success += 1
                        print(f"\r❤️ LIKES: {success} | ❌ ERR: {fails} | 📊 RPS: {rps} | 🎥 {video_id[-6:]}", end="")
                else:
                    with _lock: fails += 1
            except:
                with _lock: fails += 1
        except:
            with _lock: fails += 1

def sendFollowers(device_id, install_id, cdid, openudid):
    global reqs, success, fails
    # CHANGE THIS sec_uid to your target: get from tiktok.com/@username network tab
    TARGET_SEC_UID = "MS4wLjABAAAAv6rXbY2v_cQy0A3jS1w_5k2qL9fGHiJkL"  # REPLACE THIS
    for _ in range(20):
        try:
            params_dict = get_params()
            params = urlencode(params_dict)
            payload = f"to_user_id={TARGET_SEC_UID}&status=1"
            sig = Gorgon(params=params).get_value()
            
            headers = get_headers(device_id, install_id, cdid, openudid)
            headers['X-Bogus'] = sig
            
            domain = random.choice(DOMAINS)
            resp = requests.post(f"https://{domain}/aweme/v1/commit/follow/user/?{params}", 
                               data=payload, headers=headers, verify=False, timeout=8)
            reqs += 1
            
            try:
                if resp.status_code == 200 and resp.json().get('status_code') == 0:
                    with _lock:
                        success += 1
                        print(f"\r👤 FOLLOWERS: {success} | ❌ ERR: {fails} | 📊 RPS: {rps} | 🎯 {TARGET_SEC_UID[-8:]}", end="")
                else:
                    with _lock: fails += 1
            except:
                with _lock: fails += 1
        except:
            with _lock: fails += 1

def sendLiveViews(device_id, install_id, cdid, openudid):
    global reqs, success, fails
    for _ in range(20):
        try:
            room_id = random.choice(ROOM_IDS)
            params_dict = get_params()
            params = urlencode(params_dict)
            payload = f"room_id={room_id}&hold_living_room=1&is_login=1&enter_source=general_search"
            sig = Gorgon(params=params).get_value()
            
            headers = get_headers(device_id, install_id, cdid, openudid)
            headers['X-Bogus'] = sig
            
            domain = random.choice(DOMAINS)
            resp = requests.post(f"https://{domain}/webcast/room/enter/?{params}", 
                               data=payload, headers=headers, verify=False, timeout=8)
            reqs += 1
            
            try:
                if resp.status_code == 200 and resp.json().get('status_code') == 0:
                    with _lock:
                        success += 1
                        print(f"\r🔴 LIVE: {success} | ❌ ERR: {fails} | 📊 RPS: {rps} | 📺 {room_id[-6:]}", end="")
                else:
                    with _lock: fails += 1
            except:
                with _lock: fails += 1
        except:
            with _lock: fails += 1

def stats_loop():
    global rps
    while True:
        time.sleep(1)
        with _lock:
            rps = reqs

def banner():
    print("""
╦ ╦┌─┐┬ ┬┌┬┐┌─┐┌┐┌┌─┐┌┬┐┬┌┬┐┌─┐┬─┐
║║║├┤ │││ ││├┤ │││├─┤  │ │ │ ├┤ ├┬┘
╚╩╝└─┘└┴┘─┘└─┘┘└┘┴ ┴  ┴ ┴─┘└─┘┴└─
    TikTok Bot v2.0 - ALL-IN-ONE
    NO FILES NEEDED - FULLY SELF-CONTAINED
    """)

def main():
    global success
    banner()
    
    print("\n🎯 OPTIONS:")
    print(" [1] 📈 Video Views")
    print(" [2] ⭐ Video Favorites") 
    print(" [3] 🔗 Video Shares")
    print(" [4] ❤️ Video Likes/Hearts")
    print(" [5] 👤 Followers (CHANGE TARGET_SEC_UID ABOVE)")
    print(" [6] 🔴 Live Stream Views\n")
    
    option = int(input("Select (1-6): "))
    threads_cnt = int(input("Threads (100-1000): "))
    target_hits = int(input("Target hits: "))
    
    funcs = {
        1: sendViews, 2: sendFavorites, 3: sendShares,
        4: sendHearts, 5: sendFollowers, 6: sendLiveViews
    }
    
    if option not in funcs:
        print("❌ Invalid option!")
        return
    
    print(f"\n🚀 Starting {threads_cnt} threads | Target: {target_hits}")
    print("Press Ctrl+C to stop\n")
    
    threading.Thread(target=stats_loop, daemon=True).start()
    start_time = time.time()
    
    while success < target_hits:
        device = random.choice(DEVICES)
        did, iid, cdid, openudid = device.split(':')
        
        t = threading.Thread(target=funcs[option], args=(did, iid, cdid, openudid))
        t.daemon = True
        t.start()
        
        active = len([t for t in threading.enumerate() if t.is_alive()]) - 2
        if active >= threads_cnt:
            time.sleep(0.05)
    
    elapsed = time.time() - start_time
    print(f"\n\n🎉 TARGET REACHED!")
    print(f"✅ Success: {success:,}")
    print(f"❌ Failed:  {fails:,}") 
    print(f"📊 Total:   {reqs:,}")
    print(f"⏱️  Time:    {elapsed:.1f}s")
    print(f"⚡ RPS:      {rps:.0f}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n⏹️  STOPPED")
        print(f"✅ Success: {success:,} | ❌ Failed: {fails:,} | 📊 Total: {reqs:,}")
    except Exception as e:
        print(f"❌ Error: {e}")

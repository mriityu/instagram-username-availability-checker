import re
import time
import random
import string
import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from colorama import Fore, Style, init

# Initialize color support
init(autoreset=True)


MAX_THREADS = 10
DELAY_BETWEEN_REQUESTS = 2  # Seconds between each thread finish
username_file = "usernames.txt"

while True:
    proxy_availability = input(Fore.CYAN + "Do you want to use proxies(y/n): ")
	if proxy_availability == "y":
		proxy_file = "proxies.txt"
		break
	elif proxy_availability == "n":
		break
	else:
		print(Fore.RED + "INVALID INPUT")

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:126.0) Gecko/20100101 Firefox/126.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
    "Mozilla/5.0 (Linux; Android 14; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Mobile Safari/537.36"
]

proxies = []


def load_usernames(file_path):
    try:
        with open(file_path, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(Fore.RED + f"[!] File not found: {file_path}")
        return []

def load_proxies(file_path):
    try:
        with open(file_path, 'r') as f:
            proxies = [line.strip() for line in f if ':' in line]
            if not proxies:
                print(Fore.YELLOW + "[!] No valid proxies found. Running without proxies.")
            return proxies
    except FileNotFoundError:
        print(Fore.YELLOW + f"[!] Proxy file not found: {file_path}. Running without proxies.")
        return []

def get_next_user_agent():
    return random.choice(USER_AGENTS)

def get_random_proxy():
    if not proxies:
        return None
    proxy = random.choice(proxies)
    return {"http": f"http://{proxy}", "https": f"http://{proxy}"}

# CSRF Handling

def extract_csrf_token(session, proxy=None):
    session.headers.update({
        'User-Agent': get_next_user_agent(),
        'Accept': 'text/html'
    })

    response = session.get("https://www.instagram.com/", proxies=proxy, timeout=10)

    match = re.search(r'"csrf_token":"(.*?)"', response.text)
    if match:
        return match.group(1)

    token = session.cookies.get('csrftoken')
    if token:
        return token

    raise Exception("CSRF token not found")

# Username Checker

def check_username_availability(username):
    session = requests.Session()
    proxy = get_random_proxy()

    try:
        csrf_token = extract_csrf_token(session, proxy)

        session.headers.update({
            'User-Agent': get_next_user_agent(),
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrf_token,
            'Referer': 'https://www.instagram.com/accounts/emailsignup/',
            'Origin': 'https://www.instagram.com'
        })

        fake_email = ''.join(random.choices(string.ascii_lowercase, k=10)) + "@gmail.com"
        fake_password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
        fake_name = ''.join(random.choices(string.ascii_lowercase, k=8))

        payload = {
            'enc_password': f"#PWD_INSTAGRAM_BROWSER:0:{int(datetime.now().timestamp())}:{fake_password}",
            'email': fake_email,
            'username': username,
            'first_name': fake_name,
            'opt_into_one_tap': 'false'
        }

        url = "https://www.instagram.com/api/v1/web/accounts/web_create_ajax/attempt/"
        response = session.post(url, data=payload, proxies=proxy, timeout=10)
        result = response.json()

        if 'errors' in result and 'username' in result['errors']:
            return username, "taken"
        elif result.get("account_created") is False and result.get("dryrun_passed") is True:
            return username, "available"
        else:
            return username, "error"

    except Exception as e:
        return username, f"error: {str(e)}"

# Threaded Bulk Checker

def check_bulk_usernames(usernames, threads=MAX_THREADS):
    results = []

    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {executor.submit(check_username_availability, u): u for u in usernames}

        for future in as_completed(futures):
            username, status = future.result()
            results.append((username, status))

            if status == "available":
                print(Fore.GREEN + f"{username}: {status}")
            elif status == "taken":
                print(Fore.YELLOW + f"{username}: {status}")
            else:
                print(Fore.RED + f"{username}: {status}")

            time.sleep(DELAY_BETWEEN_REQUESTS)

    return results

# 😊

if __name__ == "__main__":
    usernames = load_usernames(username_file)
    if proxy_availability == "y":
        proxies = load_proxies(proxy_file)

    if not usernames:
        print(Fore.RED + "[!] No usernames loaded.")
    else:
        print(Fore.CYAN + f"🔍 Checking {len(usernames)} usernames with {MAX_THREADS} threads...\n")
        check_bulk_usernames(usernames)
        

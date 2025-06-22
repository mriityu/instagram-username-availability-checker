import os
import re
import random
import string
import requests
from datetime import datetime

def extractCsrftoken(session):
    requestUrl = 'https://www.instagram.com/'
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'Accept': 'text/html',
    })
    response = session.get(requestUrl)

    if response.status_code != 200:
        raise Exception(f"[!] Failed to load Instagram homepage. Status code: {response.status_code}")

    # Try to get CSRF from HTML
    pattern = r'"csrf_token":"(.*?)"'
    match = re.search(pattern, response.text)

    if match:
        token = match.group(1)
        print(f"[+] CSRF token extracted: {token}")
        return token

    # Try from cookies as fallback
    token = session.cookies.get('csrftoken')
    if token:
        print(f"[+] CSRF token from cookies: {token}")
        return token

    raise Exception("[!] CSRF token could not be found.")

def checkUsernameAvailability(session, username, csrftoken):
    url = 'https://www.instagram.com/api/v1/web/accounts/web_create_ajax/attempt/'

    session.headers.update({
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-Requested-With': 'XMLHttpRequest',
        'X-CSRFToken': csrftoken,
        'Referer': 'https://www.instagram.com/accounts/emailsignup/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'Origin': 'https://www.instagram.com'
    })

    fake_email = ''.join(random.choices(string.ascii_lowercase, k=12)) + "@gmail.com"
    fake_password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
    fake_name = ''.join(random.choices(string.ascii_lowercase, k=8))

    payload = {
        'enc_password': f"#PWD_INSTAGRAM_BROWSER:0:{int(datetime.now().timestamp())}:{fake_password}",
        'email': fake_email,
        'username': username,
        'first_name': fake_name,
        'opt_into_one_tap': 'false'
    }

    response = session.post(url, data=payload)

    try:
        result = response.json()
    except Exception as e:
        print("[!] Failed to parse response:", e)
        print(response.text)
        return None

    return result

# ==== MAIN ====
session = requests.session()
csrftoken = extractCsrftoken(session)

while True:
    username = input("Enter username (-1 to quit): ").strip()
    if username == '-1':
        break
    if not username:
        continue

    result = checkUsernameAvailability(session, username, csrftoken)

    if not result:
        print("[!] No response or invalid data.")
        continue

    # Check known error structure
    if 'errors' in result and 'username' in result['errors']:
        msg = result['errors']['username'][0].get('code', 'unavailable').replace('_', ' ')
        print(f"[-] Username '{username}' is taken or invalid: {msg}")
    elif result.get("account_created") is False and "dryrun_passed" in result and result["dryrun_passed"]:
        print(f"[+] Username '{username}' is available.")
    else:
        print(f"[?] Unclear response for '{username}': {result}")

import re
import random
import string
import requests
from datetime import datetime
import csv
import time

def extractCsrftoken(session):
    requestUrl = 'https://www.instagram.com/'
    session.headers.update({
        'User-Agent': 'Mozilla/5.0',
        'Accept': 'text/html'
    })
    response = session.get(requestUrl)

    if response.status_code != 200:
        raise Exception(f"[!] Failed to load Instagram homepage. Status code: {response.status_code}")

    pattern = r'"csrf_token":"(.*?)"'
    match = re.search(pattern, response.text)
    if match:
        return match.group(1)

    token = session.cookies.get('csrftoken')
    if token:
        return token

    raise Exception("[!] CSRF token could not be found.")

def checkUsernameAvailability(session, username, csrftoken):
    url = 'https://www.instagram.com/api/v1/web/accounts/web_create_ajax/attempt/'
    session.headers.update({
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-Requested-With': 'XMLHttpRequest',
        'X-CSRFToken': csrftoken,
        'Referer': 'https://www.instagram.com/accounts/emailsignup/',
        'User-Agent': 'Mozilla/5.0',
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

    try:
        response = session.post(url, data=payload)
        result = response.json()

        if 'errors' in result and 'username' in result['errors']:
            return "taken"
        elif result.get("account_created") is False and result.get("dryrun_passed") is True:
            return "available"
        else:
            return "error"
    except Exception as e:
        print(f"[!] Error checking '{username}': {e}")
        return "error"

def load_usernames(filename):
    with open(filename, "r") as f:
        return [line.strip() for line in f if line.strip()]

def write_results(results, filename="output.csv"):
    with open(filename, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['username', 'status'])
        for row in results:
            writer.writerow(row)

def main():
    input_file = "usernames.txt"
    output_file = "output.csv"

    usernames = load_usernames(input_file)
    if not usernames:
        print("[!] No usernames found in the file.")
        return

    session = requests.session()
    csrftoken = extractCsrftoken(session)

    results = []
    print(f"Checking {len(usernames)} usernames...")

    for username in usernames:
        status = checkUsernameAvailability(session, username, csrftoken)
        print(f"{username}: {status}")
        results.append((username, status))
        time.sleep(2)  # prevent getting blocked, polite delay

    write_results(results, output_file)
    print(f"\n✅ Results saved to '{output_file}'")

if __name__ == "__main__":
    main()

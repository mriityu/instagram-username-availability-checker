import re
import random
import string
import requests
from datetime import datetime
import csv
import time

# Realistic User-Agents (desktop, mobile, different OSes)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:126.0) Gecko/20100101 Firefox/126.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
    "Mozilla/5.0 (Linux; Android 13; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
]

# Optional proxy list (add working proxies or leave empty)
PROXIES = [
    # "http://user:pass@proxyhost:port",
    # "http://proxyhost:port"
]

# Round-robin User-Agent generator
def user_agent_generator():
    agents = USER_AGENTS[:]
    while True:
        random.shuffle(agents)
        for agent in agents:
            yield agent

user_agent_cycle = user_agent_generator()

def get_next_user_agent():
    return next(user_agent_cycle)

def get_random_proxy():
    return random.choice(PROXIES) if PROXIES else None

# Extract CSRF token from Instagram homepage
def extractCsrftoken(session):
    request_url = 'https://www.instagram.com/'
    session.headers.update({
        'User-Agent': get_next_user_agent(),
        'Accept': 'text/html'
    })

    response = session.get(request_url)

    if response.status_code != 200:
        raise Exception(f"[!] Failed to load Instagram homepage. Status code: {response.status_code}")

    match = re.search(r'"csrf_token":"(.*?)"', response.text)
    if match:
        return match.group(1)

    token = session.cookies.get('csrftoken')
    if token:
        return token

    raise Exception("[!] CSRF token could not be found.")

# Check username availability by simulating a signup attempt
def checkUsernameAvailability(session, username, csrftoken):
    url = 'https://www.instagram.com/api/v1/web/accounts/web_create_ajax/attempt/'

    session.headers.update({
        'User-Agent': get_next_user_agent(),
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-Requested-With': 'XMLHttpRequest',
        'X-CSRFToken': csrftoken,
        'Referer': 'https://www.instagram.com/accounts/emailsignup/',
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
        proxy = get_random_proxy()
        response = session.post(url, data=payload, proxies={"http": proxy, "https": proxy} if proxy else None)
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

# Load usernames from file (one per line)
def load_usernames(filename):
    with open(filename, "r") as f:
        return [line.strip() for line in f if line.strip()]

# Write sorted and grouped results to CSV
def write_sorted_results(results, filename="output.csv"):
    available = [r for r in results if r[1] == 'available']
    taken = [r for r in results if r[1] == 'taken']
    errors = [r for r in results if r[1] == 'error']

    grouped = available + taken + errors

    with open(filename, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['username', 'status'])               # Column headers
        writer.writerow(['----------', '----------'])         # Visual separator
        for row in grouped:
            writer.writerow(row)

# Main script logic
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
    print(f"🔍 Checking {len(usernames)} usernames...\n")

    for username in usernames:
        status = checkUsernameAvailability(session, username, csrftoken)
        print(f"{username}: {status}")
        results.append((username, status))
        time.sleep(5)  # Increased delay to avoid rate-limiting

    write_sorted_results(results, output_file)
    print(f"\n✅ Grouped results saved to '{output_file}'")

# Entry point
if __name__ == "__main__":
    main()

# UPDATED --- WORKING ---

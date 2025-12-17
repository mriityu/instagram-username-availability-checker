# 📸 UsernameHunter

> **A lightweight, fast, and efficient Python tool to check the availability of Instagram usernames.**

[![Python](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/mriityu/instagram-username-availability-checker/graphs/commit-activity)

**UsernameHunter** automates the process of validating Instagram handles. Whether you are looking for a new personal brand name or checking a list of potential handles for a business, this script simplifies the process.



## 📝 Features

* **Single & Bulk Mode:** Check a single username or a text file containing thousands.
* **Status Reporting:** Clearly distinguishes between _Available_, _Taken_, and _Banned/Invalid_ usernames.
* **Output Logging:** Automatically saves available usernames to a text file for easy retrieval.
* **Lightweight:** Minimal dependencies, easy to run on any machine with Python installed.
* **Proxy Support:** Compatible with proxies to avoid IP rate-limiting.

## 🛠️ Prerequisites

Before running the tool, ensure you have the following installed:

* **Python 3.6+**: [Download Here](https://www.python.org/downloads/)
* **Git**: [Download Here](https://git-scm.com/downloads)

## 📥 Installation

1.  **Clone the repository:**
    ```bash
    git clone "https://github.com/mriityu/Username-Hunter.git"
    cd Username-Hunter
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: If you do not have a requirements.txt, ensure you have `requests` installed via `pip install requests`)*

## 🚀 Usage

### 1. Simple Run
Run the main script from your terminal:

```bash
python main.py

```

### 2. The Process

1. The script will ask if you want to check a single username or a list.
2. **If List:** Ensure you have a file named `usernames.txt` in the same directory.
3. The script will iterate through the names and print the status in the console.

### 3. Results

* **Green:** Username is Available.
* **Red:** Username is Taken.
* **Yellow:** Error/Rate Limited.

Available usernames are automatically appended to `available.txt`.

## ⚠️ Disclaimer

> **Educational Purposes Only.**
> This tool is designed for educational purposes and legitimate username research. Please do not use this tool to spam Instagram's servers. The developer is not responsible for any misuse of this script or any IP bans resulting from excessive requests.


## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

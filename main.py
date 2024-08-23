import requests
import time
import sys
import threading


# Загрузка списка кошельков из файла
def load_wallets(filename='wallets.txt'):
    with open(filename, 'r') as file:
        wallets = [line.strip() for line in file if line.strip()]
    return wallets


# Загрузка прокси из файла
def load_proxies(filename='proxies.txt'):
    with open(filename, 'r') as file:
        proxies = [line.strip() for line in file if line.strip()]
    return proxies


def get_wallet_data(wallet, proxy=None):
    url = f"https://api-mainnet.magiceden.dev/v2/wallets/{wallet}/activities"

    proxy_dict = {
        'http': proxy,
        'https': proxy
    } if proxy else None

    try:
        response = requests.get(url, proxies=proxy_dict, timeout=10) if proxy_dict else requests.get(url, timeout=10)
        time.sleep(5)

        if response.status_code == 200:
            json_data = response.json()

            unique_days = set()
            unique_months = set()

            for item in json_data:
                if item.get('type') == 'buyNow' and item.get('buyer') == wallet:
                    block_time = item["blockTime"]
                    date = time.strftime('%Y-%m-%d', time.gmtime(block_time))
                    month = time.strftime('%Y-%m', time.gmtime(block_time))

                    unique_days.add(date)
                    unique_months.add(month)

            return {
                'wallet': wallet,
                'unique_days': len(unique_days),
                'unique_months': len(unique_months)
            }
    except requests.exceptions.RequestException as e:
        print(f"Error with proxy {proxy if proxy else 'direct connection'}: {e}")
    return None


def print_loading_animation(stop_event):
    while not stop_event.is_set():
        for char in "|/-\\":
            sys.stdout.write(f'\rLoading {char} ')
            sys.stdout.flush()
            time.sleep(0.1)


def main():
    wallets = load_wallets()
    proxies = load_proxies()

    if not proxies:
        print("\nNo proxies found. Using direct connection.")

    data = []
    stop_event = threading.Event()

    loading_thread = threading.Thread(target=print_loading_animation, args=(stop_event,))
    loading_thread.start()

    for i, wallet in enumerate(wallets):
        proxy = proxies[i % len(proxies)] if proxies else None
        wallet_data = get_wallet_data(wallet, proxy)
        if wallet_data:
            data.append(wallet_data)

    stop_event.set()
    loading_thread.join()

    print("\nResults:")
    for index, item in enumerate(data, start=1):
        print(
            f"{index}. Wallet: {item['wallet']}, Unique Days: {item['unique_days']}, Unique Months: {item['unique_months']}")


if __name__ == "__main__":
    main()

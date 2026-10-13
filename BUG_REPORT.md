# Bug Bounty Security Report: SecureBank Application

## Executive Summary
During a security assessment of the SecureBank API, three significant vulnerabilities were identified. These flaws allow for unauthorized access to sensitive user data, financial loss through balance manipulation (Double Spend), and the ability to spoof payment notifications via broken webhook validation.

---

## 1. Broken Object Level Authorization (BOLA / IDOR)

**Severity:** High
**Status:** Open

### Description
The endpoint `/api/balance/:userId` fails to validate if the requesting user has the authorization to view the balance of the specified `userId`. An attacker can simply change the `userId` parameter in the URL to iterate through and leak the balances of all users in the system.

### Impact
Exposure of sensitive financial information for all bank customers.

### Steps to Reproduce
1. Ensure the application is running.
2. Run the provided PoC script:
   ```bash
   python proof-of-concept/idor_poc.py
   ```
3. Observe that the script successfully fetches balances for `user_1`, `user_2`, and others without any authentication or authorization check.

### Remediation
Implement an authorization check to ensure that the `userId` requested matches the identity of the authenticated user (e.g., by checking a JWT claim or session variable).

---

## 2. Race Condition (Double Spend)

**Severity:** Critical
**Status:** Open

### Description
The `/api/withdraw` endpoint implements a "check-then-act" pattern that is not atomic. Because the balance is checked and then updated in two separate steps with a delay in between, multiple concurrent requests can pass the balance check before any of them update the balance.

### Impact
An attacker can withdraw funds multiple times simultaneously, resulting in a negative balance and direct financial loss for the bank.

### Steps to Reproduce
1. Ensure the application is running.
2. Run the provided PoC script:
   ```bash
   python proof-of-concept/race_condition_poc.py
   ```
3. The script sends 5 simultaneous requests to withdraw 500 units from a user who only has 500 units.
4. Observe that multiple requests return `200 OK`, and the final balance becomes negative.

### Remediation
Use atomic database operations (e.g., `UPDATE accounts SET balance = balance - amount WHERE id = userId AND balance >= amount`) or implement distributed locking/mutexes to ensure that only one withdrawal request is processed at a time per user.

---

## 3. Broken Webhook Signature Validation

**Severity:** High
**Status:** Open

### Description
The `/api/webhooks/payment` endpoint contains a debugging bypass that allows requests with the header `x-bank-signature: DEBUG_MODE` or no signature at all to be processed as valid.

### Impact
An attacker can spoof payment notifications, tricking the system into believing a payment was made when it was not, potentially granting services or credit to an account illegally.

### Steps to Reproduce
1. Ensure the application is running.
2. Run the provided PoC script:
   ```bash
   python proof-of-concept/webhook_bypass_poc.py
   ```
3. Observe that the server returns `200 OK` when the `DEBUG_MODE` header is provided, bypassing the actual secret validation.

### Remediation
Remove all debug-mode bypasses from production code. Ensure that the signature validation is mandatory and uses a constant-time comparison algorithm to prevent timing attacks.

---

## Conclusion
The SecureBank application exhibits critical security failures in authorization and concurrency control. Immediate remediation of these issues is required to prevent financial loss and data breaches.

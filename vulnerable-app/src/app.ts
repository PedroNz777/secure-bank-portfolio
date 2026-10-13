import express, { Request, Response } from 'express';
import { BankDatabase } from './database';

const app = express();
app.use(express.json());

const db = new BankDatabase();

// Seed initial data
db.createUser("user_1", 1000); // Alice
db.createUser("user_2", 500);  // Bob

/**
 * VULNERABILITY 1: BOLA / IDOR
 * The endpoint takes userId from params and doesn't check if the
 * authenticated user has permission to view this specific account.
 */
app.get('/api/balance/:userId', (req: Request, res: Response) => {
    const { userId } = req.params;
    const balance = db.getBalance(userId);

    if (balance === null) {
        return res.status(404).json({ error: "User not found" });
    }

    res.json({ userId, balance });
});

/**
 * VULNERABILITY 2: Race Condition (Double Spend)
 * The balance check and update are not atomic.
 * Between the 'getBalance' and 'setBalance', another request can slip in.
 */
app.post('/api/withdraw', async (req: Request, res: Response) => {
    const { userId, amount } = req.body;

    const currentBalance = db.getBalance(userId);
    if (currentBalance === null) return res.status(404).json({ error: "User not found" });

    if (currentBalance < amount) {
        return res.status(400).json({ error: "Insufficient funds" });
    }

    // Artificial delay to make the Race Condition easier to trigger in the PoC
    await new Promise(resolve => setTimeout(resolve, 100));

    const newBalance = currentBalance - amount;
    db.setBalance(userId, newBalance);

    res.json({ message: "Withdrawal successful", newBalance });
});

/**
 * VULNERABILITY 3: Broken Webhook Signature Validation
 * The app checks for the presence of a signature, but the validation
 * logic is flawed (e.g., it compares the signature to a constant
 * or allows empty signatures if not handled correctly).
 */
app.post('/api/webhooks/payment', (req: Request, res: Response) => {
    const signature = req.headers['x-bank-signature'];
    const payload = req.body;

    // BUG: The developer implemented a "bypass" for testing that was left in production
    // OR uses a weak comparison that can be bypassed.
    if (signature === 'DEBUG_MODE' || !signature) {
        console.log("Webhook processed without valid signature!");
        return res.status(200).json({ status: "processed" });
    }

    // Mock validation logic
    if (signature === 'valid_secret_123') {
        return res.status(200).json({ status: "processed" });
    }

    res.status(401).json({ error: "Invalid signature" });
});

const PORT = 3000;
app.listen(PORT, () => {
    console.log(`🚀 SecureBank (Vulnerable) running on http://localhost:${PORT}`);
});

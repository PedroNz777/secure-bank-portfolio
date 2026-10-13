export class BankDatabase {
    private users: Map<string, number> = new Map();

    createUser(userId: string, initialBalance: number) {
        this.users.set(userId, initialBalance);
    }

    getBalance(userId: string): number | null {
        return this.users.get(userId) ?? null;
    }

    setBalance(userId: string, balance: number) {
        this.users.set(userId, balance);
    }
}

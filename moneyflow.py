import pandas as pd
from queue import PriorityQueue

EPSILON = 0.000001

class Currency:
    def __init__(self, text, prefix):
        self.text = text
        self.prefix = prefix

    def __float__(self):
        return float(self.text.lstrip(self.prefix))

def main():
    net = {}
    credits = {}
    debits = {}

    with open('road trip $$$ - Money.csv') as f:
        df = pd.read_csv(f)
        totals = df[0:1].dropna(axis=1).values.tolist()[0][2::2]
        totals = list(map(lambda x: float(Currency(x, '$CA')), totals))
        payee_list = df[10:11].dropna(axis=1).values.tolist()[0]
        for _, row in df[1:9].iterrows():
            payer = row['Name']
            for i, col in enumerate(row[2::2]):
                payee = payee_list[i]
                if payee == 'Self':
                    payee = payer
                elif payee == '?':
                    break
                weight = float(col)
                amount = weight * totals[i]
                net.setdefault(payer, 0)
                net.setdefault(payee, 0)
                debits.setdefault(payer, 0)
                credits.setdefault(payee, 0)
                net[payer] -= amount
                debits[payer] -= amount
                net[payee] += amount
                credits[payee] += amount

    debt = 0
    debtors = PriorityQueue()
    credit = 0
    creditors = PriorityQueue()

    print('Name    / Debit    / Credit   / Net Balance')
    for person in sorted(net.keys()):
        if net[person] < 0:
            debt += net[person]
            debtors.put((net[person], person))
        elif net[person] > 0:
            credit -= net[person]
            creditors.put((-net[person], person))
        print(f'{person:7} / ${debits[person] if person in debits else 0:7.2f} / ${credits[person] if person in credits else 0:7.2f} / ${net[person]:7.2f}')
    print()

    print('Transfers:')
    transfers = []
    while True:
        debt, debtor = debtors.get()
        credit, creditor = creditors.get()
        transfer = -max(debt, credit)
        transfers.append(f'{debtor:7} -> {creditor:7}: ${transfer:.2f}')
        net[debtor] += transfer
        net[creditor] -= transfer
        if debt - credit > EPSILON:
            creditors.put((credit - debt, creditor))
        elif credit - debt > EPSILON:
            debtors.put((debt - credit, debtor))
        if debtors.empty() and creditors.empty():
            break
    transfers.sort()
    print('\n'.join(transfers))
    print()

    print('Net Balances:')
    for person in sorted(net.keys()):
        print(f'{person:7} ${0 if abs(net[person]) < EPSILON else net[person]:.2f}')
        assert abs(net[person]) < EPSILON


if __name__ == '__main__':
    main()

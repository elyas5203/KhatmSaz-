import csv
with open('docs/ai/audit/ITEMS.csv', encoding='utf-8') as f:
    r = csv.DictReader(f)
    a01 = [row for row in r if 'identity' in row['path'] or 'phone' in row['path'] or 'account_merge' in row['path'] or 'authorization' in row['path'] or 'session' in row['path']]
    for row in a01:
        print(f"{row['path']}::{row['name']}")

import csv
import io

data = []
with open('c:/xampp/htdocs/Khatm/docs/ai/audit/WORK_PACKAGES.csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    for row in reader:
        if row[0] in ('A11', 'A12'):
            row[1] = 'IN_PROGRESS'
            row[2] = 'Antigravity'
            row[3] = '2026-10-04T12:30:00+03:30'
            row[4] = 'a2f55b412078b0ab3b23085c5b2f1cc84c4eb6ce'
            row[6] = 'Tests run, bugs identified, awaiting owner fix command'
        data.append(row)

with open('c:/xampp/htdocs/Khatm/docs/ai/audit/WORK_PACKAGES.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerows(data)

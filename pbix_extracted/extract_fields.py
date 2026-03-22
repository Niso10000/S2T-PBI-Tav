import json, sys, io, re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('d:/Desktop/CCode/S2T_PBI/Tav/pbix_extracted/layout.json', encoding='utf-8') as f:
    raw = f.read()

# Extract all Entity values
entities = re.findall(r'Entity\\":\\"([^\\"]+)\\"', raw)
print('=== TABLES REFERENCED IN VISUALS ===')
for e in sorted(set(entities)):
    print(' ', e)

print()

# Extract Entity.Property pairs - greedy but within reasonable distance
ep_pairs = re.findall(r'Entity\\":\\"([^\\"]+)\\".*?Property\\":\\"([^\\"]+)\\"', raw)
result = {}
for e, p in ep_pairs:
    if len(e) < 80 and len(p) < 100:
        result.setdefault(e, set()).add(p)

print('=== COLUMNS/MEASURES BY TABLE ===')
for tbl in sorted(result.keys()):
    print(f'\nTable: {tbl}')
    for f in sorted(result[tbl]):
        print(f'  {f}')

# Also extract queryRef
qrefs = re.findall(r'queryRef\\":\\"([^\\"]+)\\"', raw)
print('\n=== ALL QUERY REFS ===')
for qr in sorted(set(qrefs)):
    print(' ', qr)

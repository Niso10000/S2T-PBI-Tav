import re, sys, io, struct

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('d:/Desktop/CCode/S2T_PBI/Tav/pbix_extracted/contents/DataModel', 'rb') as f:
    raw = f.read()

print(f'DataModel size: {len(raw):,} bytes')
print(f'First 32 bytes hex: {raw[:32].hex()}')
print(f'First 32 bytes: {repr(raw[:32])}')

# Check for ZIP/gzip/other compression
print(f'Magic bytes: {raw[:4].hex()}')

# Try to find JSON blobs by scanning for { patterns
# in different encodings
for encoding in ['utf-8', 'utf-16-le', 'latin-1']:
    try:
        text = raw.decode(encoding, errors='replace')
        # Count Hebrew characters as a quality metric
        heb_count = sum(1 for c in text if '\u0590' <= c <= '\u05FF')
        json_like = text.count('"name"') + text.count('"expression"')
        print(f'{encoding}: Hebrew chars={heb_count}, "name" count={json_like}')
    except:
        print(f'{encoding}: FAILED')

# Find all substantial Hebrew strings in UTF-16-LE
text16 = raw.decode('utf-16-le', errors='replace')
# Find segments with Hebrew content
heb_segs = re.findall(r'[\u0590-\u05FF\uFB1D-\uFB4F]{2,}[\w\s\u0590-\u05FF\uFB1D-\uFB4F\-\(\)\'\"]*', text16)
print(f'\n=== Hebrew strings in DataModel (UTF-16) ===')
unique_heb = sorted(set(s.strip() for s in heb_segs if len(s.strip()) > 3), key=lambda x: -len(x))
for s in unique_heb[:100]:
    print(f'  {repr(s)}')

# Look for measure-like patterns - Hebrew names followed by DAX
print('\n=== Looking for DAX-like content ===')
# Search for CALCULATE, SUM, DIVIDE etc in UTF-16
dax_funcs = ['CALCULATE', 'SUM', 'DIVIDE', 'IF', 'COUNTROWS', 'FILTER', 'ALL', 'AVERAGE', 'SUMX', 'AVERAGEX']
for func in dax_funcs:
    count = text16.count(func)
    if count > 0:
        print(f'  {func}: {count} occurrences')

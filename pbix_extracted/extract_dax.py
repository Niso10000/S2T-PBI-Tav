import re, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('d:/Desktop/CCode/S2T_PBI/Tav/pbix_extracted/contents/DataModel', 'rb') as f:
    raw = f.read()

# Try to find the embedded JSON model schema
# Power BI stores the model as a compressed column store, but there are readable sections
# Search for "expression" patterns which indicate DAX

# Look for UTF-16 LE sections that contain JSON-like data
# Try every 2-byte aligned position
text16 = raw.decode('utf-16-le', errors='replace')

# Search for DAX expression patterns
# Measures often appear as: "expression": "CALCULATE(..."
# or similar patterns

# Find sections that look like JSON table/measure definitions
import json

# Look for [= or CALCULATE or SUM or DIVIDE patterns (common DAX)
dax_patterns = re.findall(r'[A-Z]{2,}\s*\([^)]{0,200}\)', text16)
print('=== DAX FUNCTION CALLS FOUND ===')
seen = set()
for p in dax_patterns:
    p_clean = p.strip()
    if p_clean not in seen and len(p_clean) > 5:
        seen.add(p_clean)
        print(p_clean[:200])

print('\n=== MEASURE/EXPRESSION PATTERNS ===')
# Look for expression-like patterns
exprs = re.findall(r'"expression"\s*:\s*"([^"]{5,500})"', text16)
for e in exprs[:50]:
    print(repr(e))

# Look for table/column definition patterns
print('\n=== TABLE DEFINITION PATTERNS ===')
tbl_defs = re.findall(r'"name"\s*:\s*"([^"]+)"[^{]*?"description"\s*:\s*"([^"]*)"', text16)
for name, desc in tbl_defs[:50]:
    print(f'Table: {name}, Desc: {desc}')

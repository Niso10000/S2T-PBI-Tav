import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('d:/Desktop/CCode/S2T_PBI/Tav/pbix_extracted/contents/DataModel', 'rb') as f:
    raw = f.read(1000)
text = raw.decode('utf-16-le', errors='replace')
print(repr(text[:200]))

# Also look for known magic bytes
print(f'\nHex dump of first 100 bytes:')
for i in range(0, 100, 16):
    chunk = raw[i:i+16]
    hex_part = ' '.join(f'{b:02x}' for b in chunk)
    asc_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
    print(f'{i:04x}: {hex_part:<48} {asc_part}')

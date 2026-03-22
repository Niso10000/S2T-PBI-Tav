"""
Attempt to decompress the XPress9-compressed DataModel using Windows ctypes.
COMPRESSION_FORMAT_XPRESS_HUFF = 4 (or sometimes 5)
"""
import ctypes
import ctypes.wintypes
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ntdll = ctypes.windll.ntdll

COMPRESSION_FORMAT_XPRESS = 3
COMPRESSION_FORMAT_XPRESS_HUFF = 4
COMPRESSION_ENGINE_MAXIMUM = 0x0100

# Read the file - skip the header (first null-terminated string)
with open('d:/Desktop/CCode/S2T_PBI/Tav/pbix_extracted/contents/DataModel', 'rb') as f:
    raw = f.read()

# Find end of header string (null-terminated UTF-16)
header_end = raw.find(b'\x00\x00\x00\x00', 0) + 4
print(f'Header ends at offset: {header_end}')
print(f'Header: {raw[:header_end].decode("utf-16-le", errors="replace")}')

# The compressed data starts after the header
# Try to find where actual data begins
# Usually there's some metadata about block sizes

# Print bytes around header end
for offset in range(header_end, header_end + 64, 4):
    val = int.from_bytes(raw[offset:offset+4], 'little')
    print(f'  offset {offset}: {raw[offset:offset+4].hex()} = {val}')

# Get workspace size
format_flag = ctypes.c_uint16(COMPRESSION_FORMAT_XPRESS_HUFF | COMPRESSION_ENGINE_MAXIMUM)
workspace_size = ctypes.c_ulong(0)
fragment_size = ctypes.c_ulong(0)

status = ntdll.RtlGetCompressionWorkSpaceSize(
    format_flag,
    ctypes.byref(workspace_size),
    ctypes.byref(fragment_size)
)
print(f'\nRtlGetCompressionWorkSpaceSize status: 0x{status:08x}')
print(f'Workspace size: {workspace_size.value}')

if workspace_size.value > 0:
    workspace = (ctypes.c_uint8 * workspace_size.value)()

    # Try decompressing a chunk
    compressed = raw[header_end:]
    compressed_buf = (ctypes.c_uint8 * len(compressed))(*compressed)

    # Try with a large output buffer
    out_size = len(compressed) * 10
    out_buf = (ctypes.c_uint8 * out_size)()
    final_size = ctypes.c_ulong(0)

    status2 = ntdll.RtlDecompressBufferEx(
        format_flag,
        out_buf,
        out_size,
        compressed_buf,
        len(compressed),
        ctypes.byref(final_size),
        workspace
    )
    print(f'Decompress status: 0x{status2:08x}, final size: {final_size.value}')
    if status2 == 0:
        result = bytes(out_buf[:final_size.value])
        with open('d:/Desktop/CCode/S2T_PBI/Tav/pbix_extracted/datamodel_decompressed.bin', 'wb') as out:
            out.write(result)
        print('Saved decompressed data!')
        # Print first 200 bytes as UTF-16
        print(repr(result[:200].decode('utf-16-le', errors='replace')))

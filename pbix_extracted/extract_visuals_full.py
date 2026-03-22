import json, sys, io, re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('d:/Desktop/CCode/S2T_PBI/Tav/pbix_extracted/layout.json', encoding='utf-8') as f:
    data = json.load(f)

# Extract all filter/slicer info and full visual details
print('=== FULL VISUAL DETAILS PER PAGE ===\n')

for s in data.get('sections', []):
    page = s.get('displayName', '')
    print(f'\n{"="*60}')
    print(f'PAGE: {page}')
    print(f'{"="*60}')

    # Page-level filters
    page_filters_str = s.get('filters', '[]')
    try:
        page_filters = json.loads(page_filters_str) if isinstance(page_filters_str, str) else page_filters_str
        if page_filters:
            print(f'Page Filters: {json.dumps(page_filters, ensure_ascii=False)[:500]}')
    except:
        pass

    for vc in s.get('visualContainers', []):
        try:
            config = json.loads(vc.get('config', '{}'))
        except:
            continue
        sv = config.get('singleVisual', {})
        vtype = sv.get('visualType', 'unknown')

        # Skip decorative
        if vtype in ('shape', 'textbox', 'image', 'actionButton', 'pageNavigator', 'ScrollingTextVisual1448795304508'):
            continue

        # Get title
        title = ''
        title_obj = sv.get('vcObjects', {}).get('title', [{}])
        if title_obj:
            props = title_obj[0].get('properties', {}) if title_obj else {}
            title_val = props.get('text', {}).get('expr', {}).get('Literal', {}).get('Value', '')
            title = title_val.strip("'")

        print(f'\n  Visual: [{vtype}] {title or "(no title)"}')

        # Extract prototypeQuery
        pq = sv.get('prototypeQuery', {})

        # FROM tables
        from_tables = pq.get('From', [])
        if from_tables:
            entities = [f.get('Entity', '') for f in from_tables]
            print(f'  Tables: {entities}')

        # SELECT fields
        selects = pq.get('Select', [])
        if selects:
            fields = []
            for sel in selects:
                name = sel.get('Name', '')
                if name:
                    fields.append(name)
            if fields:
                print(f'  Fields: {fields}')

        # WHERE (filters)
        wheres = pq.get('Where', [])
        if wheres:
            print(f'  Filters: {json.dumps(wheres, ensure_ascii=False)[:300]}')

        # Visual-level filters
        vis_filters_str = vc.get('filters', '[]')
        try:
            vis_filters = json.loads(vis_filters_str) if isinstance(vis_filters_str, str) else vis_filters_str
            if vis_filters:
                print(f'  Visual Filters: {json.dumps(vis_filters, ensure_ascii=False)[:500]}')
        except:
            pass

        # For slicers, extract the field
        if vtype == 'slicer':
            projs = sv.get('projections', {})
            vals = projs.get('Values', [])
            for v in vals:
                qr = v.get('queryRef', '')
                if qr:
                    print(f'  Slicer Field: {qr}')

        # Column properties
        col_props = sv.get('columnProperties', {})
        if col_props:
            for k, v in list(col_props.items())[:5]:
                display = v.get('displayName', '')
                if display:
                    print(f'  Display: {k} -> {display}')

# Report-level filters
print('\n=== REPORT LEVEL FILTERS ===')
report_filters_str = data.get('filters', '[]')
try:
    report_filters = json.loads(report_filters_str) if isinstance(report_filters_str, str) else report_filters_str
    if report_filters:
        print(json.dumps(report_filters, ensure_ascii=False, indent=2))
except Exception as e:
    print('Error:', e)

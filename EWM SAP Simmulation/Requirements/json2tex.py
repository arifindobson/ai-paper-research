"""Render annotated JSON samples as colored LaTeX blocks for the requirements note.

Usage: python3 json2tex.py   (rewrites the JSON blocks between the % JSON:<name> markers
in external-picking-engine-requirements.tex)
"""
import json
import re
from pathlib import Path

TEX = Path(__file__).with_name('external-picking-engine-requirements.tex')
NOTE_COL = 58  # column where annotations start

SAMPLES = {
    'api1': {
        'title': r'GET /inventory?warehouse=WH01\&products=E,F,G \quad$\rightarrow$\quad 200 OK',
        'caption': r'\api{getInventoryDetails} response excerpt (data from the simulation, tab 7).',
        'label': 'lst:api1',
        'data': {
            'warehouse': 'WH01',
            'snapshotVersion': '2026-10-21T08:15:02Z#4711',
            'generatedAt': '2026-10-21T08:15:02Z',
            'next': None,
            'quants': [
                {
                    'quantId': '6f1c...',
                    'product': 'E',
                    'batch': 'E2611-30',
                    'sled': '2026-11-30',
                    'grDateTime': '2026-09-10T07:42:00Z',
                    'bin': '06-L9',
                    'storageType': '0030',
                    'storageSection': '0001',
                    'activityArea': 'PCK-R',
                    'qtyAvailable': 500,
                    'baseUoM': 'PC',
                    'storedUoM': 'PAL',
                    'storedQty': 1,
                    'huId': 'P-1002',
                    'huType': 'EUR',
                    'isFullHU': True,
                    'stockType': 'F2',
                    'blocked': False,
                    'changedAt': '2026-10-20T16:03:11Z',
                },
                {
                    'quantId': '9a07...',
                    'product': 'E',
                    'batch': 'E2611-10',
                    'sled': '2026-11-10',
                    'grDateTime': '2026-08-12T09:10:00Z',
                    'bin': '04-R4',
                    'storageType': '0020',
                    'qtyAvailable': 200,
                    'storedUoM': 'CAR',
                    'storedQty': 4,
                    'huId': None,
                    'isFullHU': False,
                },
            ],
        },
        'notes': {
            'snapshotVersion': 'echo it in createWOWT',
            'next': 'paging token, null = last page',
            'sled': 'key 2: earliest expiry',
            'grDateTime': 'key 4: first goods receipt',
            'bin': 'source bin, node in layout graph',
            'storageType': 'key 3: priority per layer',
            'activityArea': 'WO grouping',
            'qtyAvailable': 'physical - open removal, base UoM',
            'storedUoM': 'key 1: UoM layer filter',
            'isFullHU': 'only full HUs enter the PAL layer',
            'blocked': 'true = never a candidate',
            'changedAt': 'concurrency check',
            '9a07...': 'second quant: fields as above',
        },
    },
    'api2': {
        'title': r'POST /warehouse-orders \quad Idempotency-Key: 8f2c4e1a-...',
        'caption': r'\api{createWOWT} request excerpt: the forklift WO of delivery PM\#124.',
        'label': 'lst:api2',
        'data': {
            'requestId': '8f2c4e1a-...',
            'planRunId': 'PDE-20261021-0815-07',
            'warehouse': 'WH01',
            'snapshotVersion': '2026-10-21T08:15:02Z#4711',
            'warehouseOrders': [{
                'woRef': 'PDE-WO-3',
                'woType': 'FULL_HU',
                'queue': 'FORKLIFT',
                'resourceType': 'FL',
                'activityArea': 'PCK-R',
                'consolidationGroup': 'CG-ST17',
                'destination': '9010-LANE-124',
                'plannedDistance': 186,
                'plannedDuration': 240,
                'tasks': [{
                    'wtRef': 'PDE-WT-1',
                    'seqNo': 1,
                    'odo': 'PM#124',
                    'odoItem': 10,
                    'product': 'E',
                    'batch': 'E2611-30',
                    'qty': 1,
                    'uom': 'PAL',
                    'sourceBin': '06-L9',
                    'sourceHU': 'P-1002',
                    'quantId': '6f1c...',
                    'destinationBin': '9010-LANE-124',
                    'layerTrace': 'PAL; tie on expiry with 09-L2; decided at Stype prio',
                }],
            }],
        },
        'notes': {
            'requestId': 'idempotency key',
            'snapshotVersion': 'from getInventoryDetails',
            'woType': 'FULL_HU = forklift WO',
            'destination': 'GI staging lane of the delivery',
            'plannedDistance': 'metres on the layout graph',
            'plannedDuration': 'seconds',
            'seqNo': 'pick order inside the WO',
            'uom': 'layer UoM, not base UoM',
            'sourceHU': 'set = HU WT, pallet not opened',
            'quantId': 're-checked against the snapshot',
            'layerTrace': 'audit: why this quant',
        },
    },
    'api2r': {
        'title': r'200 OK \quad (partial success: WOs are all-or-nothing)',
        'caption': r'\api{createWOWT} response: one WO created, one rejected because its stock changed after the snapshot.',
        'label': 'lst:api2r',
        'data': {
            'requestId': '8f2c4e1a-...',
            'warehouseOrders': [
                {'woRef': 'PDE-WO-3', 'status': 'CREATED', 'ewmWO': '20004711',
                 'tasks': [{'wtRef': 'PDE-WT-1', 'status': 'CREATED', 'ewmWT': '100045671'}]},
                {'woRef': 'PDE-WO-2', 'status': 'REJECTED',
                 'tasks': [{'wtRef': 'PDE-WT-7', 'status': 'REJECTED', 'reason': 'STOCK_CHANGED',
                            'detail': '04-R4: available 2 CAR, planned 3 CAR'}]},
            ],
        },
        'notes': {
            'ewmWO': 'EWM warehouse order number',
            'ewmWT': 'EWM warehouse task number',
            'REJECTED': 'whole WO rolled back',
            'reason': 'PDE re-plans this item only',
        },
    },
}


def esc(s):
    """Escape for fancyvrb with commandchars \\{} ."""
    return s.replace('\\', r'\textbackslash{}').replace('{', r'\{').replace('}', r'\}')


def tok(line):
    """Colour one pretty-printed JSON line; return (tex, plain_length)."""
    out, plain, i = [], 0, 0
    while i < len(line):
        c = line[i]
        if c == ' ':
            j = i
            while j < len(line) and line[j] == ' ':
                j += 1
            out.append(line[i:j]); plain += j - i; i = j
        elif c == '"':
            j = i + 1
            while line[j] != '"':
                j += 2 if line[j] == '\\' else 1
            s = line[i:j + 1]
            is_key = line[j + 1:j + 2] == ':'
            out.append((r'\jk{%s}' if is_key else r'\js{%s}') % esc(s)); plain += len(s); i = j + 1
        elif c in '{}[]:,':
            out.append(r'\jp{%s}' % {'{': r'\LB', '}': r'\RB'}.get(c, c)); plain += 1; i += 1
        else:
            m = re.match(r'true|false|null|-?\d+(\.\d+)?', line[i:])
            s = m.group(0)
            out.append((r'\jb{%s}' if s[0] in 'tfn' else r'\jn{%s}') % s); plain += len(s); i += len(s)
    return ''.join(out), plain


def render(name, spec):
    lines = json.dumps(spec['data'], indent=2, ensure_ascii=False).split('\n')
    notes, used, body = spec['notes'], set(), []
    for ln in lines:
        tex, n = tok(ln)
        for k, note in notes.items():
            if k not in used and (f'"{k}":' in ln or f'"{k}"' in ln.split(':', 1)[-1]):
                tex += ' ' * max(2, NOTE_COL - n) + r'\jc{%s}' % esc(note)
                used.add(k)
                break
        body.append(tex)
    missing = set(notes) - used
    assert not missing, (name, missing)
    return '\n'.join([
        f'% JSON:{name} (generated by json2tex.py - edit the script, not this block)',
        r'\begin{jsonbox}{%s}' % spec['title'],
        r'\begin{Verbatim}[commandchars=\\\{\}]',
        *body,
        r'\end{Verbatim}',
        r'\end{jsonbox}',
        r'\jsonlegend',
        r'\captionof{jsonlisting}{%s}\label{%s}' % (spec['caption'], spec['label']),
        f'% END JSON:{name}',
    ])


if __name__ == '__main__':
    tex = TEX.read_text()
    for name, spec in SAMPLES.items():
        block = render(name, spec)
        pat = re.compile(r'% JSON:' + name + r'\b.*?% END JSON:' + name, re.S)
        assert pat.search(tex), f'marker for {name} missing'
        tex = pat.sub(lambda _: block, tex)
    TEX.write_text(tex)
    print('updated', TEX.name)

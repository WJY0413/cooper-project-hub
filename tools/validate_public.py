"""Offline checks for this reviewed snapshot; not a substitute for content review."""
from pathlib import Path
import csv
import hashlib
import io
import json
import re
import sqlite3
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    manifest = json.loads((ROOT / 'manifest.json').read_text(encoding='utf-8'))
    assert len(manifest['articles']) == 22
    assert len({r['id'] for r in manifest['articles']}) == 22
    assert len(manifest['packages']) == 10
    checks = 0
    for row in manifest['articles']:
        assert (ROOT / row['path']).is_file(), row['path']
        if row.get('download'):
            assert (ROOT / row['download']).is_file(), row['download']
    for md in ROOT.rglob('*.md'):
        if '.git' in md.parts:
            continue
        text = md.read_text(encoding='utf-8')
        for target in re.findall(r'\]\(([^)]+)\)', text):
            if target.startswith(('http:', 'https:', '#', 'mailto:')):
                continue
            path = (md.parent / target.split('#')[0]).resolve()
            assert path.is_relative_to(ROOT.resolve()) and path.exists(), (md, target)
            checks += 1
    for row in manifest['packages']:
        p = ROOT / row['path']
        assert hashlib.sha256(p.read_bytes()).hexdigest() == row['sha256'], p
        with zipfile.ZipFile(p) as z:
            assert z.testzip() is None, p
            for name in z.namelist():
                assert not name.startswith(('/', '\\')) and '..' not in Path(name).parts
                if name.endswith('.sqlite'):
                    with tempfile.TemporaryDirectory() as tmp:
                        db = Path(tmp) / 'check.sqlite'
                        db.write_bytes(z.read(name))
                        with sqlite3.connect(db) as con:
                            assert con.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
                            for (table,) in con.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"):
                                quoted = table.replace('"', '""')
                                assert con.execute(f'SELECT COUNT(*) FROM "{quoted}"').fetchone()[0] == 0
                        con.close()
    for csvfile in (ROOT / 'templates').glob('*.csv'):
        rows = list(csv.reader(io.StringIO(csvfile.read_text(encoding='utf-8-sig'))))
        assert len(rows) == 1 and rows[0], csvfile
    print(f'PASS: 22 articles, 10 ZIPs, {checks} local links, header-only CSVs, empty SQLite database')


if __name__ == '__main__':
    main()

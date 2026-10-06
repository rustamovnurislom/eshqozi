from datetime import datetime, timezone
from pathlib import Path
import sqlite3
import time

from .storage import Store


def snapshot(store: Store, directory: str, keep_days: int = 7) -> Path:
    folder=Path(directory)
    folder.mkdir(parents=True,exist_ok=True)
    stamp=datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
    destination=folder/f'eshqozi-{stamp}.sqlite3'
    partial=destination.with_suffix('.partial')
    store.backup(str(partial))
    with sqlite3.connect(partial) as con:
        if con.execute('PRAGMA integrity_check').fetchone()[0]!='ok':
            raise RuntimeError('Zaxira nusxasi integrity tekshiruvidan o‘tmadi')
    partial.replace(destination)
    cutoff=time.time()-keep_days*86400
    for old in folder.glob('eshqozi-*.sqlite3'):
        if old!=destination and old.stat().st_mtime<cutoff:
            old.unlink()
    return destination


def scheduled(store: Store, keep_days: int):
    directory=str(Path(store.path).parent/'backups')
    while True:
        snapshot(store,directory,keep_days)
        print('Kunlik backup yaratildi.',flush=True)
        time.sleep(86400)

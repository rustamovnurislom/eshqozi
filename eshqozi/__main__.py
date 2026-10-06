import argparse
import json
import logging
import sys
import os

from .config import Settings
from .knowledge import Knowledge
from .storage import Store


def main():
    os.umask(0o077)
    parser = argparse.ArgumentParser(description='Eshqo‘zi botini ishga tushirish')
    parser.add_argument('command',choices=['serve','init','check','backup','scheduled-backup'])
    parser.add_argument('--destination',help='backup uchun yangi fayl yo‘li')
    args = parser.parse_args()
    try:
        settings = Settings.from_env()
        if args.command=='serve':
            import uvicorn
            from .app import create_app
            logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(name)s %(message)s')
            logging.getLogger('httpx').setLevel(logging.WARNING)
            uvicorn.run(create_app(settings),host=settings.host,port=settings.port,access_log=False)
        else:
            store = Store(settings.db_path)
            store.migrate()
            if args.command=='scheduled-backup':
                from .backup import scheduled
                scheduled(store,settings.backup_days)
            elif args.command=='backup':
                if not args.destination:
                    parser.error('backup uchun --destination kerak')
                store.backup(args.destination)
                print('Ma’lumotlar bazasi zaxirasi yaratildi.')
            else:
                knowledge = Knowledge(store,settings.knowledge_path)
                print(json.dumps({'mode':settings.mode,'profiles':len(knowledge.profiles),**store.status()},ensure_ascii=False))
    except (ValueError,FileNotFoundError,RuntimeError) as exc:
        print(str(exc),file=sys.stderr)
        raise SystemExit(1) from None


if __name__=='__main__':
    main()

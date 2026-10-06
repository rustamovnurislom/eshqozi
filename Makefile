.PHONY: install init test run check backup
install:
	uv sync --frozen --cache-dir /tmp/eshqozi-uv-cache --link-mode copy
init:
	.venv/bin/python -m eshqozi init
test:
	.venv/bin/python -m unittest discover -s tests -v
run:
	.venv/bin/python -m eshqozi serve
check:
	.venv/bin/python -m eshqozi check
backup:
	.venv/bin/python -m eshqozi backup --destination var/backups/eshqozi-$$(date -u +%Y%m%d-%H%M%S).sqlite3

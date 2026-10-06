from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
import fitz, json, subprocess, os
ROOT = Path(__file__).resolve().parent
PDF = json.loads((ROOT / 'download_manifest.json').read_text())[4]['pdf_path']
OUT = ROOT / 'm5_ocr'
OUT.mkdir(exist_ok=True)
TESS = Path('/workspace/research/surxondaryo/tessdata')

def page(n):
    dst = OUT / f'{n+1:03}.txt'
    if dst.exists() and dst.stat().st_size > 0:
        return n+1
    doc = fitz.open(PDF)
    image = OUT / f'{n+1:03}.png'
    doc[n].get_pixmap(matrix=fitz.Matrix(2.1,2.1)).save(image)
    env = os.environ.copy()
    env['OMP_THREAD_LIMIT'] = '1'
    subprocess.run(['tesseract', str(image), str(dst.with_suffix('')), '--tessdata-dir', str(TESS), '-l', 'uzb', '--psm', '3'], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    image.unlink()
    return n+1

if __name__ == '__main__':
    # Contents first, then all searchable spreads. The first and last pages are covers/blanks.
    order = [94,93,92,91] + [n for n in range(1,96) if n not in [94,93,92,91]]
    with ProcessPoolExecutor(max_workers=4) as ex:
        for f in as_completed([ex.submit(page,n) for n in order]):
            print('OCR PDF',f.result(),flush=True)
    text = '\f'.join((OUT/f'{n:03}.txt').read_text() if (OUT/f'{n:03}.txt').exists() else '' for n in range(1,98))+'\f'
    (ROOT/'M5_ocr.txt').write_text(text)
    print('DONE',len(text),flush=True)

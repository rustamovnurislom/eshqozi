from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
import fitz,json,subprocess,os,time
BASE=Path('/workspace/research/surxondaryo')
PDF=json.loads((BASE/'sources.json').read_text())[0]['file']
OUT=BASE/'rahimov_ocr';OUT.mkdir(exist_ok=True)
def page(n):
 dst=OUT/f'{n+1:03}.txt'
 if dst.exists() and dst.stat().st_size>0:return n+1
 doc=fitz.open(PDF);img=OUT/f'{n+1:03}.png'
 doc[n].get_pixmap(matrix=fitz.Matrix(2.5,2.5)).save(img)
 env=os.environ.copy();env['OMP_THREAD_LIMIT']='1'
 subprocess.run(['tesseract',str(img),str(dst.with_suffix('')),'--tessdata-dir',str(BASE/'tessdata'),'-l','uzb_cyrl+rus','--psm','3'],env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=True)
 img.unlink()
 return n+1
if __name__=='__main__':
 with ProcessPoolExecutor(max_workers=4) as ex:
  for f in as_completed([ex.submit(page,n) for n in range(96)]):print('OCR page',f.result(),flush=True)
 text='\n\n'.join(f'=== PDF PAGE {n} / PRINTED {n} ===\n'+(OUT/f'{n:03}.txt').read_text() for n in range(1,97))
 (BASE/'source_1_ocr.txt').write_text(text)
 print('DONE',len(text),flush=True)

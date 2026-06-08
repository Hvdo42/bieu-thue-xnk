"""
build.py – Build Biểu thuế XNK từ template + data.

  python build.py        → local/index.html   (6MB standalone, mở file:// được)
  python build.py --web  → dist/index.html (74KB) + dist/app_data.json (6MB)
"""
import json, os, sys, shutil

sys.stdout.reconfigure(encoding='utf-8')
BASE          = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(BASE, 'template.html')
DATA_PATH     = os.path.join(BASE, 'app_data.json')

OFFLINE_MODE = '--web' not in sys.argv

with open(TEMPLATE_PATH, encoding='utf-8') as f:
    template = f.read()
with open(DATA_PATH, encoding='utf-8') as f:
    raw_json = f.read()

if OFFLINE_MODE:
    OUT_PATH = os.path.join(BASE, 'local', 'index.html')
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)

    out_html = template.replace('/*__DATA__*/', 'window._DATA = ' + raw_json + ';')
    out_html = out_html.replace('/*__INIT__*/', "document.addEventListener('DOMContentLoaded', init);")

    with open(OUT_PATH, 'w', encoding='utf-8') as f:
        f.write(out_html)
    print(f'[offline] local/index.html  ({os.path.getsize(OUT_PATH)/1e6:.1f} MB) – mở file:// trực tiếp được')

else:
    OUT_PATH  = os.path.join(BASE, 'dist', 'index.html')
    DIST_DATA = os.path.join(BASE, 'dist', 'app_data.json')
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)

    init_injection = """document.addEventListener('DOMContentLoaded', function(){
  var _bar = document.createElement('div');
  _bar.style.cssText = 'position:fixed;top:0;left:0;right:0;background:#1565C0;color:#fff;padding:10px 18px;font-size:14px;z-index:9999;text-align:center';
  _bar.textContent = '⏳ Đang tải dữ liệu biểu thuế...';
  document.body.prepend(_bar);
  fetch('./app_data.json')
    .then(function(r){ if(!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
    .then(function(d){
      window._DATA = d;
      D = d;
      document.body.removeChild(_bar);
      init();
    })
    .catch(function(e){
      _bar.style.background = '#c62828';
      _bar.textContent = '⚠ Không tải được dữ liệu (' + e.message + '). Dùng bản offline local/index.html.';
    });
});"""

    out_html = template.replace('/*__DATA__*/', 'window._DATA = null;')
    out_html = out_html.replace('/*__INIT__*/', init_injection)

    with open(OUT_PATH, 'w', encoding='utf-8') as f:
        f.write(out_html)
    shutil.copy2(DATA_PATH, DIST_DATA)
    readme = os.path.join(BASE, 'README.md')
    if os.path.exists(readme):
        shutil.copy2(readme, os.path.join(BASE, 'dist', 'README.md'))

    print(f'[web] dist/index.html       ({os.path.getsize(OUT_PATH)//1024} KB)')
    print(f'[web] dist/app_data.json    ({os.path.getsize(DIST_DATA)/1e6:.1f} MB)')
    print('Deploy: upload cả thư mục dist/ lên GitHub Pages')

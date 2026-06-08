"""
setup_build.py – Chạy 1 lần để tách data khỏi index.html và tạo build pipeline.

Chạy: python setup_build.py
Kết quả:
  app_data.json   ← data nguồn (12000 mục thuế)
  template.html   ← app shell, placeholder thay cho data
  build.py        ← build pipeline chính thức
  local/          ← offline build (double-click mở được)
  dist/           ← web build (upload GitHub)
"""
import json, os, re, sys, shutil

BASE = os.path.dirname(os.path.abspath(__file__))
SRC  = os.path.join(BASE, 'index.html')

sys.stdout.reconfigure(encoding='utf-8')

# ── 1. Đọc index.html theo dòng ──────────────────────────────────────────────
print('Đọc index.html...')
with open(SRC, encoding='utf-8') as f:
    lines = f.readlines()

DATA_LINE_PREFIX = 'window._DATA = '
data_line_idx = None
for i, line in enumerate(lines):
    if line.startswith(DATA_LINE_PREFIX):
        data_line_idx = i
        break

if data_line_idx is None:
    print('LỖI: Không tìm thấy dòng window._DATA = ...')
    sys.exit(1)

print(f'  Data nằm ở dòng {data_line_idx + 1} ({len(lines[data_line_idx])//1024} KB)')

# ── 2. Tách JSON data ─────────────────────────────────────────────────────────
raw_data_line = lines[data_line_idx].strip()
# Bỏ prefix "window._DATA = " và suffix ";"
json_str = raw_data_line[len(DATA_LINE_PREFIX):]
if json_str.endswith(';'):
    json_str = json_str[:-1]

print('  Parse JSON...')
data = json.loads(json_str)
count = data.get('meta', {}).get('count', '?')
print(f'  Số mục: {count}')

# ── 3. Lưu app_data.json ──────────────────────────────────────────────────────
app_data_path = os.path.join(BASE, 'app_data.json')
with open(app_data_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
size_mb = os.path.getsize(app_data_path) / 1e6
print(f'  Đã ghi app_data.json ({size_mb:.1f} MB)')

# ── 4. Tạo template.html ──────────────────────────────────────────────────────
template_lines = (
    lines[:data_line_idx]
    + ['/*__DATA__*/\n']
    + lines[data_line_idx + 1:]
)
template_path = os.path.join(BASE, 'template.html')
with open(template_path, 'w', encoding='utf-8') as f:
    f.writelines(template_lines)
print(f'  Đã ghi template.html ({os.path.getsize(template_path)//1024} KB)')

# ── 5. Tạo build.py ───────────────────────────────────────────────────────────
build_py = r'''"""
build.py – Build XNK Tra cứu từ template + data.

  python build.py        → local/index.html   (standalone, mở file:// được)
  python build.py --web  → dist/index.html + dist/app_data.json (GitHub Pages)
"""
import json, os, sys

sys.stdout.reconfigure(encoding=\'utf-8\')
BASE          = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(BASE, \'template.html\')
DATA_PATH     = os.path.join(BASE, \'app_data.json\')

OFFLINE_MODE = \'--web\' not in sys.argv

if OFFLINE_MODE:
    OUT_PATH = os.path.join(BASE, \'local\', \'index.html\')
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
else:
    OUT_PATH      = os.path.join(BASE, \'dist\', \'index.html\')
    DIST_DATA     = os.path.join(BASE, \'dist\', \'app_data.json\')
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)

# Đọc data
with open(DATA_PATH, encoding=\'utf-8\') as f:
    raw_json = f.read()

# Đọc template
with open(TEMPLATE_PATH, encoding=\'utf-8\') as f:
    template = f.read()

if OFFLINE_MODE:
    # Nhúng data trực tiếp vào HTML
    injection = \'window._DATA = \' + raw_json + \';\'
    out_html  = template.replace(\'/*__DATA__*/\', injection)
    with open(OUT_PATH, \'w\', encoding=\'utf-8\') as f:
        f.write(out_html)
    size_mb = os.path.getsize(OUT_PATH) / 1e6
    print(f\'[offline] {OUT_PATH}  ({size_mb:.1f} MB) – mở file:// trực tiếp được\')
else:
    # Nhúng fetch() thay cho data
    fetch_js = """window._DATA = null;
(function(){
  var el = document.getElementById(\'search-input\');
  document.querySelector(\'.s-stats\') && (document.querySelector(\'.s-stats\').textContent = \'Đang tải dữ liệu...\');
  fetch(\'./app_data.json\')
    .then(function(r){ if(!r.ok) throw new Error(\'HTTP \' + r.status); return r.json(); })
    .then(function(d){
      window._DATA = d;
      D = d;
      _initApp();
    })
    .catch(function(e){
      document.body.insertAdjacentHTML(\'afterbegin\',
        \'<div style="background:#c62828;color:#fff;padding:10px 18px;font-size:14px">\' +
        \'&#9888; Không tải được dữ liệu (\' + e.message + \'). \' +
        \'Dùng bản offline hoặc mở qua web server.</div>\');
    });
})();"""
    out_html = template.replace(\'/*__DATA__*/\', fetch_js)
    with open(OUT_PATH, \'w\', encoding=\'utf-8\') as f:
        f.write(out_html)
    import shutil
    shutil.copy2(DATA_PATH, DIST_DATA)
    print(f\'[web] dist/index.html  ({os.path.getsize(OUT_PATH)//1024} KB)\')
    print(f\'[web] dist/app_data.json  ({os.path.getsize(DIST_DATA)/1e6:.1f} MB)\')
'''

build_path = os.path.join(BASE, 'build.py')
with open(build_path, 'w', encoding='utf-8') as f:
    f.write(build_py)
print(f'  Đã ghi build.py')

# ── 6. Build ngay offline ─────────────────────────────────────────────────────
print('\nBuild offline mode...')
os.makedirs(os.path.join(BASE, 'local'), exist_ok=True)
out_path = os.path.join(BASE, 'local', 'index.html')
injection = 'window._DATA = ' + json_str + ';'
with open(template_path, encoding='utf-8') as f:
    template = f.read()
out_html = template.replace('/*__DATA__*/', injection)
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(out_html)
print(f'  local/index.html  ({os.path.getsize(out_path)/1e6:.1f} MB)')

# ── 7. Build web mode ─────────────────────────────────────────────────────────
print('Build web mode...')
os.makedirs(os.path.join(BASE, 'dist'), exist_ok=True)
# Cần app phải gọi _initApp() sau khi fetch — check xem có hàm này không
if '_initApp' not in template:
    print('  [!] template.html chưa có hàm _initApp(). Web mode cần wrap init vào hàm.')
    print('  --> Sẽ dùng phương pháp reload thay thế')
    fetch_js = """window._DATA = null;
(function(){
  fetch('./app_data.json')
    .then(function(r){ if(!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
    .then(function(d){
      window._DATA = d;
      window.location.reload();
    })
    .catch(function(e){
      document.body.insertAdjacentHTML('afterbegin',
        '<div style="background:#c62828;color:#fff;padding:10px 18px;font-size:14px">' +
        '&#9888; Không tải được dữ liệu (' + e.message + '). ' +
        'Mở qua web server hoặc dùng bản offline local/index.html.</div>');
    });
})();"""
else:
    fetch_js = """window._DATA = null;
(function(){
  fetch('./app_data.json')
    .then(function(r){ if(!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
    .then(function(d){ window._DATA = d; D = d; _initApp(); })
    .catch(function(e){
      document.body.insertAdjacentHTML('afterbegin',
        '<div style="background:#c62828;color:#fff;padding:10px 18px;font-size:14px">' +
        '&#9888; Không tải được dữ liệu (' + e.message + '). ' +
        'Mở qua web server hoặc dùng bản offline local/index.html.</div>');
    });
})();"""

dist_html = template.replace('/*__DATA__*/', fetch_js)
dist_html_path = os.path.join(BASE, 'dist', 'index.html')
with open(dist_html_path, 'w', encoding='utf-8') as f:
    f.write(dist_html)
shutil.copy2(app_data_path, os.path.join(BASE, 'dist', 'app_data.json'))
print(f'  dist/index.html  ({os.path.getsize(dist_html_path)//1024} KB)')
print(f'  dist/app_data.json  ({os.path.getsize(os.path.join(BASE,"dist","app_data.json"))/1e6:.1f} MB)')

# ── 8. Copy README vào dist ───────────────────────────────────────────────────
readme = os.path.join(BASE, 'README.md')
if os.path.exists(readme):
    shutil.copy2(readme, os.path.join(BASE, 'dist', 'README.md'))

print('\nHoàn thành! Cấu trúc:')
print('  dist/    ← upload lên GitHub')
print('  local/   ← mở offline để test')

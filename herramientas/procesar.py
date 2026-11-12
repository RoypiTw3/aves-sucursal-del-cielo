#!/usr/bin/env python3
"""Descarga, recorta y comprime las fotos y los cantos de las aves.

Uso: python3 procesar.py fuentes.json <carpeta_temporal>

fuentes.json:
{
  "fotos":  [{"ave": "bichofue", "n": 1, "titulo": "File:....jpg", "modo": "mayor", "voltear": false, "mini": true}],
  "cantos": [{"ave": "bichofue", "url": "https://xeno-canto.org/123456/download", "inicio": 0, "duracion": 20}]
}

Escribe sitio/img/<ave>-<n>.webp, sitio/img/<ave>-mini.webp, sitio/audio/<ave>.mp3
y herramientas/medidas.json con la proporción, el autor y la licencia de cada foto,
y la duración y la forma de onda de cada canto.
"""
import html
import json
import os
import re
import struct
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

UA = 'AvesCaliExpo/1.0 (proyecto educativo)'
AQUI = os.path.dirname(os.path.abspath(__file__))
SITIO = os.path.normpath(os.path.join(AQUI, '..', 'sitio'))
RECORTAR = os.path.join(AQUI, 'recortar')


def get(url, dest=None):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    for intento in range(5):
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                data = r.read()
            break
        except urllib.error.HTTPError as e:
            if e.code != 429 or intento == 4:
                raise
            time.sleep(6 * (intento + 1))
    time.sleep(1.5)
    if dest:
        with open(dest, 'wb') as fh:
            fh.write(data)
    return data


def limpia(s):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', s or ''))).strip()


def info_commons(titulo):
    q = urllib.parse.urlencode({'action': 'query', 'titles': titulo, 'prop': 'imageinfo',
                                'iiprop': 'url|size|extmetadata', 'iiurlwidth': 1920, 'format': 'json'})
    d = json.loads(get('https://commons.wikimedia.org/w/api.php?' + q))
    p = next(iter(d['query']['pages'].values()))
    ii = p['imageinfo'][0]
    md = ii.get('extmetadata', {})
    return {'descarga': ii.get('thumburl') or ii['url'], 'url': ii['descriptionurl'],
            'autor': limpia(md.get('Artist', {}).get('value')),
            'licencia': limpia(md.get('LicenseShortName', {}).get('value'))}


def medida(png):
    out = subprocess.run(['sips', '-g', 'pixelWidth', '-g', 'pixelHeight', png], capture_output=True, text=True).stdout
    return int(re.search(r'pixelWidth: (\d+)', out).group(1)), int(re.search(r'pixelHeight: (\d+)', out).group(1))


def reducir(src, dst, maximo):
    w, h = medida(src)
    if max(w, h) > maximo:
        subprocess.run(['sips', '-Z', str(maximo), src, '--out', dst], check=True, capture_output=True)
    else:
        subprocess.run(['cp', src, dst], check=True)


def foto(f, tmp):
    inf = info_commons(f['titulo'])
    base = f"{f['ave']}-{f['n']}"
    src = os.path.join(tmp, base + '.src')
    get(inf['descarga'], src)
    png = os.path.join(tmp, base + '.png')
    subprocess.run([RECORTAR, src, png, f.get('modo', 'mayor')], check=True)
    if f.get('voltear'):
        subprocess.run(['sips', '-f', 'horizontal', png], check=True, capture_output=True)
    small = os.path.join(tmp, base + '-r.png')
    reducir(png, small, f.get('max', 900))
    subprocess.run(['cwebp', '-quiet', '-q', '82', '-alpha_q', '90', '-m', '6', small,
                    '-o', os.path.join(SITIO, 'img', base + '.webp')], check=True)
    w, h = medida(small)
    res = {'src': f'img/{base}.webp', 'ar': round(w / h, 4), 'autor': inf['autor'],
           'licencia': inf['licencia'], 'url': inf['url'], 'titulo': f['titulo']}
    if f.get('mini'):
        mini = os.path.join(tmp, base + '-mini.png')
        reducir(png, mini, 220)
        subprocess.run(['cwebp', '-quiet', '-q', '80', '-alpha_q', '85', mini,
                        '-o', os.path.join(SITIO, 'img', f"{f['ave']}-mini.webp")], check=True)
        res['mini'] = f"img/{f['ave']}-mini.webp"
    return res


def duracion(path):
    out = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', path],
                         capture_output=True, text=True).stdout.strip()
    return float(out)


def canto(c, tmp):
    src = os.path.join(tmp, c['ave'] + '.audio')
    get(c['url'], src)
    total = duracion(src)
    ini = float(c.get('inicio', 0))
    d = min(float(c.get('duracion', 25)), total - ini)
    dst = os.path.join(SITIO, 'audio', c['ave'] + '.mp3')
    af = f"afade=t=in:st=0:d=0.25,afade=t=out:st={max(0, d - 0.8):.2f}:d=0.8,loudnorm=I=-16:TP=-1.5:LRA=11"
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', f'{ini:.2f}', '-t', f'{d:.2f}', '-i', src,
                    '-af', af, '-ac', '1', '-ar', '44100', '-b:a', '80k', dst], check=True)
    raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', dst, '-ac', '1', '-ar', '8000', '-f', 's16le', '-'],
                         capture_output=True, check=True).stdout
    n = len(raw) // 2
    s = struct.unpack('<%dh' % n, raw[:n * 2])
    barras = 56
    per = max(1, n // barras)
    rms = []
    for i in range(barras):
        seg = s[i * per:(i + 1) * per] or (0,)
        rms.append((sum(x * x for x in seg) / len(seg)) ** 0.5)
    tope = max(rms) or 1
    return {'src': f"audio/{c['ave']}.mp3", 'dur': round(n / 8000, 1),
            'picos': [round(0.12 + 0.88 * (v / tope) ** 0.8, 2) for v in rms],
            'kb': round(os.path.getsize(dst) / 1024)}


def main():
    cfg = json.load(open(sys.argv[1]))
    tmp = sys.argv[2]
    os.makedirs(tmp, exist_ok=True)
    salida_path = os.path.join(AQUI, 'medidas.json')
    salida = json.load(open(salida_path)) if os.path.exists(salida_path) else {'fotos': {}, 'cantos': {}}
    for f in cfg.get('fotos', []):
        try:
            r = foto(f, tmp)
            salida['fotos'][f"{f['ave']}-{f['n']}"] = r
            print('foto ok', f['ave'], f['n'], r['ar'], r['licencia'], '|', r['autor'])
        except Exception as e:  # noqa: BLE001
            print('foto FALLÓ', f['ave'], f['n'], e)
    for c in cfg.get('cantos', []):
        try:
            r = canto(c, tmp)
            salida['cantos'][c['ave']] = r
            print('canto ok', c['ave'], r['dur'], 's', r['kb'], 'KB')
        except Exception as e:  # noqa: BLE001
            print('canto FALLÓ', c['ave'], e)
    json.dump(salida, open(salida_path, 'w'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()

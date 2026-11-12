#!/usr/bin/env python3
"""Genera los códigos QR (uno general y uno por ave) y una hoja para imprimir.

Uso: python qr.py https://direccion-publicada.app/

Necesita la librería segno y node (para leer sitio/datos.js).
Escribe qr/<id>.svg, qr/<id>.png y qr/hoja.html.
"""
import html
import json
import os
import subprocess
import sys

import segno

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.normpath(os.path.join(AQUI, '..'))
SITIO = os.path.join(RAIZ, 'sitio')
SALIDA = os.path.join(RAIZ, 'qr')


def aves():
    js = ("global.window={};require(" + json.dumps(os.path.join(SITIO, 'datos.js')) + ");"
          "console.log(JSON.stringify({p:window.PROYECTO,a:window.AVES.map(a=>({id:a.id,nombre:a.nombre,"
          "cientifico:a.cientifico,fondo:a.fondo,tarjeta:a.tarjeta,foto:a.fotos[a.objs[0].f].src}))}))")
    return json.loads(subprocess.run(['node', '-e', js], capture_output=True, text=True, check=True).stdout)


def main():
    base = sys.argv[1].rstrip('/') + '/'
    os.makedirs(SALIDA, exist_ok=True)
    d = aves()
    items = [{'id': 'general', 'nombre': d['p'].get('nombre', 'Aves de la sucursal del cielo'), 'cientifico': 'Las cinco aves',
              'fondo': '#FBFAF8', 'tarjeta': '#FFFFFF', 'foto': None, 'url': base}]
    items += [dict(a, url=base + '#/' + a['id']) for a in d['a']]
    tarjetas = []
    for it in items:
        q = segno.make(it['url'], error='q', micro=False)
        q.save(os.path.join(SALIDA, it['id'] + '.svg'), scale=10, border=2, dark='#1D1B2E')
        q.save(os.path.join(SALIDA, it['id'] + '.png'), scale=24, border=2, dark='#1D1B2E')
        svg = q.svg_inline(scale=6, border=0, dark='#1D1B2E')
        foto = '<img class="ave" src="../sitio/' + it['foto'] + '" alt="">' if it['foto'] else ''
        texto = 'Escanea y conoce las cinco aves' if it['id'] == 'general' else 'Escanea y escucha su canto'
        tarjetas.append(
            '<article style="background:' + it['tarjeta'] + '">' + foto
            + '<div class="tx"><h2>' + html.escape(it['nombre']) + '</h2><p class="sc">' + html.escape(it['cientifico']) + '</p></div>'
            + '<div class="qr">' + svg + '</div><p class="ins">' + texto + '</p>'
            + '<p class="url">' + html.escape(it['url']) + '</p></article>')
        print('QR', it['id'], it['url'])
    hoja = """<!doctype html><html lang="es"><head><meta charset="utf-8"><title>Códigos QR · Aves de la sucursal del cielo</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Figtree:ital,wght@0,400..700;1,400&display=swap">
<style>
@page{size:A4;margin:10mm}
*{box-sizing:border-box}body{margin:0;font-family:Figtree,system-ui,sans-serif;color:#1D1B2E;background:#eee}
main{display:grid;grid-template-columns:1fr 1fr;gap:6mm;width:190mm;margin:10mm auto}
article{position:relative;height:88mm;border-radius:6mm;padding:7mm;overflow:hidden;break-inside:avoid;display:flex;flex-direction:column;border:0.3mm solid rgba(29,27,46,.12)}
.ave{position:absolute;right:4mm;top:4mm;height:30mm;max-width:34mm;object-fit:contain}
h2{margin:0;font-weight:500;font-size:7mm;line-height:1.05;max-width:52mm;letter-spacing:-.02em}
.sc{margin:1.5mm 0 0;font-style:italic;font-size:3.4mm;opacity:.7}
.qr{margin-top:auto;align-self:flex-start;background:#fff;border-radius:3mm;padding:3mm}
.qr svg{display:block;width:34mm;height:34mm}
.ins{position:absolute;left:50mm;bottom:20mm;margin:0;font-weight:500;font-size:4mm;max-width:30mm;line-height:1.25}
.url{position:absolute;left:50mm;bottom:8mm;margin:0;font-size:2.3mm;opacity:.6;max-width:36mm;overflow-wrap:anywhere}
@media print{body{background:none}main{margin:0 auto}}
</style></head><body><main>""" + ''.join(tarjetas) + '</main></body></html>'
    with open(os.path.join(SALIDA, 'hoja.html'), 'w') as fh:
        fh.write(hoja)
    print('hoja', os.path.join(SALIDA, 'hoja.html'))


if __name__ == '__main__':
    main()

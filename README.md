# Aves de la sucursal del cielo

Página web para celular de la exposición «Aves de la sucursal del cielo», en Cali. Junto a cada ave hay un código QR que abre su página.

Las cinco aves: tangara rastrojera, pechirrojo, bichofué, azulejo común y espatulilla.

- **Portada:** las aves en figuras de papel plegado. Se cambia de ave deslizando hacia arriba o con la isla de abajo.
- **Página de cada ave:** fotos reales tomadas en Cali y un recorrido con su canto, cómo reconocerla, dónde vive en Cali, su nido, qué come y un dato curioso.

Cada ave tiene su propia dirección, para los QR: `#/tangara-rastrojera`, `#/pechirrojo`, `#/bichofue`, `#/azulejo` y `#/espatulilla`. La de créditos es `#/creditos`.

## Carpetas

- `sitio/`: la página que se publica. `index.html` tiene el diseño y el código; `datos.js` tiene todos los textos, créditos y medidas. Para corregir un texto, edita `datos.js`.
- `sitio/img/`: fotos recortadas de las aves (Cali) y fotos de nidos.
- `sitio/ilus/`: ilustraciones de papel de la portada.
- `sitio/audio/`: cantos de xeno-canto.
- `herramientas/`: scripts para recortar fotos (`recortar.swift`), igualar su brillo (`igualar.swift`), preparar fotos y cantos (`procesar.py`), armar `datos.js` (`armar_datos.py`) y generar los QR (`qr.py`).

## Ver la página en el computador

```
python3 -m http.server 8765 --directory sitio
```

Y abre http://localhost:8765.

## Publicación

Cada vez que se sube un cambio a `main`, GitHub Actions publica la carpeta `sitio/` en GitHub Pages.

## Créditos

Las fotos de las aves son de observadores de iNaturalist en Cali. Las fotos de nidos son de iNaturalist y los cantos de xeno-canto. Todo se usa según sus licencias Creative Commons y sin fines comerciales; el detalle por foto y grabación está en cada página y en `#/creditos`. Los textos citan sus fuentes, entre ellas la Guía ilustrada de las aves de Santiago de Cali (2025) y el libro «Aves de Cali» de la Universidad Icesi.

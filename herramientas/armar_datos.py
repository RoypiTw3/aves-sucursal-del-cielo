#!/usr/bin/env python3
"""Arma sitio/datos.js con los textos de las aves y las medidas de fotos, nidos, cantos e ilustraciones.

Uso: python3 armar_datos.py
Lee herramientas/medidas.json (fotos elegidas, nidos, créditos, cantos) y sitio/ilus/medidas.json (ilustraciones).
Si después editas sitio/datos.js a mano, no vuelvas a correr este script o perderás esos cambios.
"""
import json
import os
import re

AQUI = os.path.dirname(os.path.abspath(__file__))
SITIO = os.path.normpath(os.path.join(AQUI, '..', 'sitio'))
MED = json.load(open(os.path.join(AQUI, 'medidas.json')))
ILUS_MED = os.path.join(SITIO, 'ilus', 'medidas.json')
ILUS = json.load(open(ILUS_MED)) if os.path.exists(ILUS_MED) else {}

GUIA_CALI = ['Guía ilustrada de las aves de Santiago de Cali, 2025 (DAGMA, CVC y Asociación Calidris)',
             'https://calidris.org.co/wp-content/uploads/2025/09/Libro-de-aves-de-Cali-2025-baja.pdf']
DAGMA_HORA = ['DAGMA: avistamiento de aves en Cali',
              'https://www.cali.gov.co/dagma/publicaciones/167121/avistamiento-de-aves-en-cali-una-actividad-para-todas-las-edades/']
DAGMA_PANCE = ['DAGMA (2023): Corazón de Pance alberga casi el 20 % de las especies de aves de Cali',
               'https://www.cali.gov.co/dagma/publicaciones/174082/corazon-de-pance-alberga-casi-el-20-de-las-especies-de-aves-que-habitan-en-cali/']
UNIVALLE_2015 = ['Hernández-C et al. (2015). Aves del campus de la Universidad del Valle. Rev. Colombiana Cienc. Anim. 7(1)',
                 'https://dialnet.unirioja.es/descarga/articulo/9423106.pdf']
ICESI = ['Pizano et al. (2024). Aves de Cali. Editorial Universidad Icesi', 'https://www.icesi.edu.co/editorial/aves-de-cali/']
TEMPRANO = 'Temprano en la mañana, como recomienda el DAGMA.'

# Lugar corto para el pie de foto de cada nido
LUGAR_NIDO = {
    'El Poblado, Medellin, Colombia': 'Medellín',
    'Maribel, La Estrella, Antioquia, Colombia': 'La Estrella, Antioquia',
    'San Pedro, Cali, Valle del Cauca, Colombia': 'Barrio San Pedro, Cali',
    'Gamboa, Colón Province, Panama': 'Gamboa, Panamá',
    'Parque nacional El Palmar, Entre Rios': 'Entre Ríos, Argentina',
}


# Ubicación de cada figura: c = [centro x %, centro y %, ancho %] en la tarjeta;
# m = celular (cx: centro horizontal, w: ancho máximo, vy: 0 arriba / 1 abajo en su zona);
# d = computador (x, y en % de pantalla; w en % del ancho). sp = profundidad al cambiar de ave.
# La figura 0 va arriba del nombre (vuelo), la 1 abajo a la izquierda (posado) y la 2 abajo a la derecha (nido).
def objs(m0, m1, m2, d0, d1, d2):
    return [
        {'f': 0, 'sp': 0.9, 'c': [60, 22, 56], 'm': m0, 'd': d0},
        {'f': 1, 'sp': 1.1, 'c': [27, 64, 46], 'm': m1, 'd': d1},
        {'f': 2, 'sp': 1.25, 'c': [72, 75, 46], 'm': m2, 'd': d2},
    ]


AVES = [
    {
        'id': 'tangara-rastrojera', 'corto': 'Tangara', 'titulo': ['Tangara', 'rastrojera'],
        'nombre': 'Tangara rastrojera', 'cientifico': 'Stilpnia vitriolina', 'g': 'a',
        'fondo': '#BEE5D3', 'tarjeta': '#D7F0E4',
        'otros': 'También: tángara rastrojera.',
        'objs': objs({'cx': 0.58, 'w': 0.62}, {'cx': 0.27, 'w': 0.46, 'vy': 0.1}, {'cx': 0.74, 'w': 0.48, 'vy': 0.85},
                     {'x': 30, 'y': 20, 'w': 19}, {'x': 9, 'y': 69, 'w': 15}, {'x': 80, 'y': 67, 'w': 16}),
        'mini': {'size': '190%', 'pos': '100% 0%'},
        'canto': {
            'ono': '«tsiip» · «dzii»',
            'frase': 'Llamados cortos y suaves que la pareja usa para hablarse.',
            'autor': 'Andrew Spencer', 'xc': 'XC22151', 'url': 'https://xeno-canto.org/22151',
            'lugar': 'El 18, zona rural de Cali, 2008', 'licencia': 'CC BY-NC-ND 2.5, usada sin modificar',
        },
        'reconocer': {
            'frase': 'Coronilla color óxido, antifaz negro y cuerpo gris plateado. Alas y cola con bordes verde azulados.',
            'datos': [['Tamaño', '14 cm'], ['Peso', '18 a 27 g'], ['Macho y hembra', 'Parecidos'], ['En Cali', 'Todo el año']],
        },
        'cali': {
            'frase': 'Parques, jardines, rastrojos y bordes de bosque. Casi siempre anda en pareja.',
            'lugares': [['Jardín Botánico de Cali', ''], ['Universidad del Valle', 'Residente en el campus'],
                        ['Ecoparque Corazón de Pance', ''], ['Zoológico de Cali', ''], ['Km 18', 'Zona rural, donde se grabó su canto']],
            'hora': TEMPRANO,
        },
        'nido': {
            'frase': 'Una taza abierta de pasto, raíces finas, musgo y telaraña. No hay nidos descritos en Cali: estos datos vienen de un nido estudiado en Ecuador.',
            'datos': [['Forma', 'Taza abierta'], ['Huevos', '2, azul pálido'], ['Incubación', '14 a 15 días'], ['Quién incuba', 'La hembra']],
        },
        'come': {'frase': 'Insectos y frutas. A veces se junta con otras aves en árboles con fruta.', 'chips': ['Insectos', 'Frutas']},
        'dato': 'Su nombre científico, vitriolina, viene del latín y quiere decir «de vidrio».',
        'fuentes': [GUIA_CALI,
                    ['Birds of the World: Scrub Tanager', 'https://birdsoftheworld.org/bow/species/scrtan1/cur/introduction'],
                    ['Freile (2015). Nido de la tangara rastrojera en Ecuador. Ornitología Neotropical 26', 'https://ornneo.journals.publicknowledgeproject.org/index.php/ornneo/article/view/12'],
                    UNIVALLE_2015, DAGMA_PANCE, DAGMA_HORA,
                    ['Wikipedia: Stilpnia vitriolina', 'https://es.wikipedia.org/wiki/Stilpnia_vitriolina'],
                    ['iNaturalist: observaciones en Cali', 'https://www.inaturalist.org/observations?taxon_id=979968&place_id=29259']],
    },
    {
        'id': 'pechirrojo', 'corto': 'Pechirrojo', 'titulo': ['Pechirrojo'],
        'nombre': 'Pechirrojo', 'cientifico': 'Pyrocephalus rubinus', 'g': 'o',
        'fondo': '#F7C6B2', 'tarjeta': '#FBDDD0',
        'otros': 'También: atrapamoscas pechirrojo, titiribí o petirrojo.',
        'objs': objs({'cx': 0.56, 'w': 0.6}, {'cx': 0.26, 'w': 0.44, 'vy': 0.15}, {'cx': 0.74, 'w': 0.46, 'vy': 0.9},
                     {'x': 30, 'y': 21, 'w': 18}, {'x': 9, 'y': 67, 'w': 12}, {'x': 80, 'y': 67, 'w': 15}),
        'mini': {'size': '200%', 'pos': '50% 0%'},
        'canto': {
            'ono': '«pi-d\'d\'d\'riít»',
            'frase': 'Un trino corto. En época de cría el macho canta suspendido en el aire. No hay grabaciones libres de Cali; esta es de Pereira.',
            'autor': 'David Monroy Rengifo', 'xc': 'XC457290', 'url': 'https://xeno-canto.org/457290',
            'lugar': 'Pereira, 2019', 'licencia': 'CC BY-NC-SA 4.0',
        },
        'reconocer': {
            'frase': 'El macho es rojo escarlata con antifaz, espalda y alas oscuras. La hembra es parda, con la barriga salmón.',
            'datos': [['Tamaño', '13 cm'], ['Peso', '11 a 14 g'], ['Macho', 'Rojo y negruzco'], ['Hembra', 'Parda y salmón']],
        },
        'cali': {
            'frase': 'Común en toda la ciudad. Busca zonas abiertas cerca del agua y se posa en ramas bajas o cercas de alambre.',
            'lugares': [['Universidad del Valle', '132 registros en 2011 y 2012'], ['Universidad Icesi', ''],
                        ['Ecoparque Corazón de Pance', ''], ['Parque La Flora', ''], ['Parque Panamericano', '']],
            'hora': 'En la mañana. El macho canta desde antes del amanecer.',
        },
        'nido': {
            'frase': 'Una taza poco profunda de ramitas, raíces y plumas, unida con telaraña, en la horqueta de una rama. La hace la hembra.',
            'datos': [['Forma', 'Taza poco profunda'], ['Huevos', '2 o 3, crema con manchas'], ['Incubación', '13 a 15 días'], ['Pichones', '14 a 16 días en el nido']],
        },
        'come': {'frase': 'Insectos que caza en el aire desde una percha baja. Mientras espera, sube y baja la cola.', 'chips': ['Saltamontes', 'Mariposas', 'Moscas']},
        'dato': 'Pyrocephalus quiere decir «cabeza de fuego». En Armenia, los machos de los barrios más construidos empezaron a cantar 101 minutos antes del amanecer, en promedio.',
        'fuentes': [ICESI, GUIA_CALI,
                    ['Sánchez-González et al. (2021). Canto del amanecer en zonas urbanas de Armenia. Ethology Ecology & Evolution 33', 'https://doi.org/10.1080/03949370.2020.1837963'],
                    ['Universidad del Valle: registros de aves del campus 2011-2012 (GBIF)', 'https://doi.org/10.15472/bcuofb'],
                    DAGMA_PANCE,
                    ['Audubon: Vermilion Flycatcher', 'https://www.audubon.org/field-guide/bird/vermilion-flycatcher'],
                    ['Animal Diversity Web: Pyrocephalus rubinus', 'https://animaldiversity.org/accounts/Pyrocephalus_rubinus/'],
                    ['Birds Colombia: titiribí pechirrojo', 'https://birdscolombia.com/2016/08/10/titiribi-pechirrojo-pyrocephalus-rubinus/'],
                    ['iNaturalist: observaciones en Cali', 'https://www.inaturalist.org/observations?taxon_name=Pyrocephalus&nelat=3.52&nelng=-76.44&swlat=3.30&swlng=-76.62&quality_grade=research']],
    },
    {
        'id': 'bichofue', 'corto': 'Bichofué', 'titulo': ['Bichofué'],
        'nombre': 'Bichofué', 'cientifico': 'Pitangus sulphuratus', 'g': 'o',
        'fondo': '#F6E3A1', 'tarjeta': '#FAEDC4',
        'otros': 'También: bichofué gritón o cristofué.',
        'objs': objs({'cx': 0.62, 'w': 0.5}, {'cx': 0.25, 'w': 0.42, 'vy': 0.1}, {'cx': 0.74, 'w': 0.46, 'vy': 0.8},
                     {'x': 31, 'y': 21, 'w': 12}, {'x': 9, 'y': 66, 'w': 11}, {'x': 80, 'y': 66, 'w': 13}),
        'mini': {'size': '210%', 'pos': '50% 0%'},
        'canto': {
            'ono': '«bi-cho-fuí»',
            'frase': 'De su llamado viene su nombre. En Cali, los bichofués de zonas ruidosas cantan las primeras notas más agudas.',
            'autor': 'Camilo E. Sánchez Sarria', 'xc': 'XC549480', 'url': 'https://xeno-canto.org/549480',
            'lugar': 'Parque de Multicentro, Cali, 2020', 'licencia': 'CC BY-NC-SA 4.0',
        },
        'reconocer': {
            'frase': 'Pecho amarillo, espalda café y una ceja blanca ancha sobre un antifaz negro. El sirirí se le parece, pero no tiene la ceja blanca.',
            'datos': [['Tamaño', '22 cm'], ['Peso', '52 a 71 g'], ['Macho y hembra', 'Iguales'], ['En Cali', 'Todo el año']],
        },
        'cali': {
            'frase': 'Una de las aves más comunes de los barrios y avenidas de Cali. Prefiere árboles cerca del agua.',
            'lugares': [['Parque de Multicentro', 'Aquí se grabó su canto'], ['Ecoparque Lago de las Garzas', ''],
                        ['Ecoparque Río Pance', ''], ['Jardín Botánico de Cali', ''], ['Unicentro', 'Lo fotografiaron adentro en 2021']],
            'hora': TEMPRANO,
        },
        'nido': {
            'frase': 'Una bola grande de pasto con techo y entrada a un lado. La pareja la arma en lo alto de un árbol o en un poste.',
            'datos': [['Forma', 'Bola con entrada lateral'], ['Huevos', '2 a 5, crema con pintas'], ['Incubación', '13 a 17 días'], ['Quién lo hace', 'Macho y hembra']],
        },
        'come': {'frase': 'De todo: insectos, frutas, lagartijas y hasta pececitos que saca del agua lanzándose en picada.', 'chips': ['Insectos', 'Frutas', 'Lagartijas', 'Peces']},
        'dato': 'Fue la mascota de los Juegos Mundiales Cali 2013, con el nombre «Bichofué Gritón».',
        'fuentes': [['Mendoza y Arce-Plata (2012). Canto del bichofué en Cali. Revista de Ciencias, Universidad del Valle 16', 'https://revistaciencias.univalle.edu.co/index.php/revista_de_ciencias/article/download/500/622/1534'],
                    GUIA_CALI,
                    ['The World Games: Cali presenta su mascota oficial (2013)', 'https://www.theworldgames.org/news/Cali-presents-official-mascot-1207'],
                    ['Corrales-Moya y Sandoval (2021). Nidos en postes de energía. Ornitología Neotropical 32', 'https://doi.org/10.58843/ornneo.v32i1.739'],
                    ['Tesis Universidad Icesi (2014) sobre aves del Jardín Botánico y el Ecoparque Río Cali', 'https://repository.icesi.edu.co/bitstreams/cada93c7-05af-4558-b046-b820bc9ec438/download'],
                    ['Bichofué en Unicentro, Wikimedia Commons', 'https://commons.wikimedia.org/wiki/File:Bichofu%C3%A9_Unicentro_02.jpg'],
                    ['Diario Occidente: ¿Bichofué o sirirí?', 'https://occidente.co/galeria/bichofue-o-siriri/'],
                    ['Wikipedia: Pitangus sulphuratus', 'https://es.wikipedia.org/wiki/Pitangus_sulphuratus'],
                    ['Animal Diversity Web: Pitangus sulphuratus', 'https://animaldiversity.org/accounts/Pitangus_sulphuratus/'],
                    DAGMA_HORA],
    },
    {
        'id': 'azulejo', 'corto': 'Azulejo', 'titulo': ['Azulejo', 'común'],
        'nombre': 'Azulejo común', 'cientifico': 'Thraupis episcopus', 'g': 'o',
        'fondo': '#B7D3F3', 'tarjeta': '#D2E3F8',
        'otros': 'En Cali le dicen azulejo.',
        'objs': objs({'cx': 0.56, 'w': 0.66}, {'cx': 0.27, 'w': 0.46, 'vy': 0.1}, {'cx': 0.7, 'w': 0.56, 'vy': 0.95},
                     {'x': 30, 'y': 21, 'w': 20}, {'x': 9, 'y': 68, 'w': 14}, {'x': 79, 'y': 70, 'w': 22}),
        'mini': {'size': '200%', 'pos': '100% 0%'},
        'canto': {
            'ono': '',
            'frase': 'Chillidos agudos y rápidos. En esta grabación, dos azulejos vocalizan en los árboles del Parque de Multicentro.',
            'autor': 'Camilo E. Sánchez Sarria', 'xc': 'XC549443', 'url': 'https://xeno-canto.org/549443',
            'lugar': 'Parque de Multicentro, Cali, 2020', 'licencia': 'CC BY-NC-SA 4.0',
        },
        'reconocer': {
            'frase': 'Gris azulado claro, con alas y cola de azul más fuerte. En Cali tiene el hombro azul brillante.',
            'datos': [['Tamaño', '16 cm'], ['Peso', '28 a 40 g'], ['Macho y hembra', 'Iguales'], ['En Cali', 'Todo el año']],
        },
        'cali': {
            'frase': 'Una de las aves más comunes de Cali. Anda en pareja o en grupos pequeños por parques, jardines y árboles de la calle.',
            'lugares': [['Ecoparque Lago de las Garzas', 'En 8 de cada 10 listas de eBird'], ['Parque del Acueducto, San Antonio', ''],
                        ['Universidad del Valle', ''], ['Ecoparque Río Pance', ''], ['Zoológico de Cali', '']],
            'hora': TEMPRANO,
        },
        'nido': {
            'frase': 'Una taza profunda de fibras y musgo unida con telaraña, escondida en una horqueta o entre hojas de palma.',
            'datos': [['Forma', 'Taza profunda'], ['Huevos', '1 a 3, gris azulado'], ['Incubación', '12 a 14 días'], ['Altura', '3 a 20 m']],
        },
        'come': {'frase': 'Sobre todo frutas; también néctar e insectos. En Cali llega a comederos con banano o guayaba.', 'chips': ['Frutas', 'Néctar', 'Insectos']},
        'dato': 'Episcopus quiere decir «obispo» en latín. A veces no hace nido: se roba el de aves más pequeñas.',
        'fuentes': [GUIA_CALI,
                    ['El País Cali (2023): las aves son un tesoro natural que vuela sobre Cali', 'https://www.elpais.com.co/cali/las-aves-son-un-tesoro-natural-que-vuelan-sobre-cali.html'],
                    ['eBird: frecuencia del azulejo común en el Valle del Cauca', 'https://ebird.org/barchart?r=CO-VAC&yr=all&m=&spp=bugtan'],
                    ['Smithsonian National Zoo: Blue-gray tanager', 'https://nationalzoo.si.edu/node/7687'],
                    ['Birds of the World: Blue-gray Tanager', 'https://birdsoftheworld.org/bow/species/bugtan/cur/introduction'],
                    ['Cueva et al. (2022). Variación geográfica del azulejo. PLOS ONE', 'https://pmc.ncbi.nlm.nih.gov/articles/PMC9534438/'],
                    ['Diario Occidente: los azulejos en mi jardín', 'https://occidente.co/cali/las-aves-de-cali/los-azulejos-en-mi-jardin/'],
                    DAGMA_HORA],
    },
    {
        'id': 'espatulilla', 'corto': 'Espatulilla', 'titulo': ['Espatulilla'],
        'nombre': 'Espatulilla', 'cientifico': 'Todirostrum cinereum', 'g': 'a',
        'fondo': '#CDBBF2', 'tarjeta': '#DFD3F7',
        'otros': 'También: espatulilla común o titirijí común.',
        'objs': objs({'cx': 0.58, 'w': 0.5}, {'cx': 0.27, 'w': 0.44, 'vy': 0.1}, {'cx': 0.74, 'w': 0.42, 'vy': 0.85},
                     {'x': 30, 'y': 21, 'w': 15}, {'x': 9, 'y': 67, 'w': 13}, {'x': 80, 'y': 66, 'w': 12}),
        'mini': {'size': '190%', 'pos': '0% 0%'},
        'canto': {
            'ono': '«tic tic tic»',
            'frase': 'Un «tic» agudo que repite muchas veces. Al amanecer puede llegar a 110 por minuto.',
            'autor': 'Juan Pablo Arboleda', 'xc': 'XC573575', 'url': 'https://xeno-canto.org/573575',
            'lugar': 'Cali, 2020', 'licencia': 'CC BY-NC-SA 4.0',
        },
        'reconocer': {
            'frase': 'Muy pequeña: cara negra, barriga amarilla, ojo claro y pico largo y plano. Salta de lado con la cola parada.',
            'datos': [['Tamaño', '9,5 cm'], ['Peso', '4 a 8 g'], ['Pico', 'Largo y plano'], ['En Cali', 'Todo el año']],
        },
        'cali': {
            'frase': 'Jardines, parques y arbustos. Busca insectos entre las hojas, cerca del suelo: mira los arbustos, no la copa de los árboles.',
            'lugares': [['Universidad del Valle', 'Residente en el campus'], ['Barrio Pance', ''],
                        ['Barrio San Pedro', 'Una pareja hizo aquí su nido en 2025'], ['Parque de Multicentro', ''], ['Ciudad Jardín', '']],
            'hora': 'Al amanecer, cuando más canta.',
        },
        'nido': {
            'frase': 'Una bolsa colgante tejida con pasto, fibras y telaraña, con la entrada a un lado. La pareja la cuelga de una rama delgada.',
            'datos': [['Forma', 'Bolsa colgante'], ['Huevos', '2 o 3, blancos'], ['Incubación', '15 a 18 días'], ['Altura', '1 a 5 m']],
        },
        'come': {'frase': 'Insectos y arañas que atrapa en las hojas; a veces frutas.', 'chips': ['Insectos', 'Arañas', 'Frutas']},
        'dato': 'Cuando atrapa un insecto, su pico hace un chasquido que se alcanza a oír.',
        'fuentes': [GUIA_CALI, UNIVALLE_2015,
                    ['iNaturalist: pareja haciendo su nido en San Pedro, Cali (2025)', 'https://www.inaturalist.org/observations/285010292'],
                    ['iNaturalist: observaciones en Cali', 'https://www.inaturalist.org/observations?taxon_name=Todirostrum%20cinereum&place_id=29259'],
                    ['Wikipedia: Common tody-flycatcher', 'https://en.wikipedia.org/wiki/Common_tody-flycatcher'],
                    ['Wikipedia: Todirostrum cinereum', 'https://es.wikipedia.org/wiki/Todirostrum_cinereum'],
                    ['Birds Colombia: espatulilla común', 'https://birdscolombia.com/2017/02/16/todirostrum-cinereum/'],
                    DAGMA_HORA],
    },
]

PROYECTO = {
    'nombre': 'Aves de la sucursal del cielo',
    'lugar': 'Cali, Colombia',
    'intro': [
        'Cali es una ciudad de aves: en su zona urbana y sus alrededores se han reportado más de 300 especies, según la Guía ilustrada de las aves de Santiago de Cali (2025).',
        'Esta página presenta cinco aves que viven en Cali todo el año: cómo reconocerlas, cómo suena su canto, cómo hacen su nido y dónde verlas.',
    ],
    'creditos': 'Las fotos de las aves fueron tomadas en Cali por observadores de iNaturalist. Las de los nidos también vienen de iNaturalist y los cantos, de xeno-canto. '
                'Todo se usa según sus licencias Creative Commons y sin fines comerciales. '
                'A las fotos de las aves se les quitó el fondo y se les ajustó el brillo, y algunos cantos se recortaron; esas versiones se comparten con la misma licencia de la original. '
                'Las figuras de papel de la portada son ilustraciones hechas para esta página.',
}


def autor_limpio(a):
    return re.sub(r'\s+from\s+.*$', '', a).strip()


def main():
    salida = []
    for a in AVES:
        fotos = []
        for f in MED['final'][a['id']]:
            autor = autor_limpio(f['autor'])
            if autor == 'Segidawiki':
                autor = 'Sebastián Giraldo Dávila (Segidawiki)'
            fotos.append({'src': f['src'], 'ar': f['ar'], 'autor': autor, 'licencia': f['licencia'], 'url': f['url'],
                          'fuente': f.get('fuente', 'Wikimedia Commons'), 'lugar': f.get('lugar', ''), 'alt': a['nombre']})
        c = MED['cantos'][a['id']]
        a2 = dict(a)
        a2['fotos'] = fotos
        a2['mini'] = dict(a['mini'], src=f"img/{a['id']}-mini.webp")
        a2['canto'] = dict(a['canto'], src=c['src'], dur=c['dur'], picos=c['picos'])
        nido = dict(a['nido'])
        nido['fotos'] = [dict(f, lugar=LUGAR_NIDO.get(f['lugar'], f['lugar'])) for f in MED.get('nidos', {}).get(a['id'], [])]
        for f in nido['fotos']:
            f.pop('fecha', None)
        if nido.get('ilus') and not os.path.exists(os.path.join(SITIO, nido['ilus'])):
            nido.pop('ilus')
        a2['nido'] = nido
        # Ilustraciones de la portada, solo aves: vuelo (arriba), posado (izquierda), posado2 (derecha).
        # Mientras no exista posado2, va la figura posada en espejo.
        def ilu(nombre):
            archivo = f"{a['id']}-{nombre}.svg"
            if archivo in ILUS and os.path.exists(os.path.join(SITIO, 'ilus', archivo)):
                return {'src': 'ilus/' + archivo, 'ar': ILUS[archivo]}
            return None
        v, p, p2 = ilu('vuelo'), ilu('posado'), ilu('posado2')
        if p and not p2:
            p2 = dict(p, flip=True)
        ilus = [x for x in (v, p, p2) if x]
        if len(ilus) == 3:
            a2['ilus'] = ilus
            # La isla también usa la figura de papel (posada), para que la portada sea pareja
            a2['mini'] = {'src': ilus[1]['src'], 'size': '88%', 'pos': '50% 55%'}
        salida.append(a2)

    def compacto(obj):
        txt = json.dumps(obj, ensure_ascii=False, indent=1)
        txt = re.sub(r'\[\s*((?:-?[\d.]+\s*,\s*)*-?[\d.]+)\s*\]', lambda m: '[' + ', '.join(x.strip() for x in m.group(1).split(',')) + ']', txt)
        txt = re.sub(r'\[\s*("(?:[^"\\]|\\.)*")\s*,\s*("(?:[^"\\]|\\.)*")\s*\]', r'[\1, \2]', txt)
        return txt
    js = ('/* Datos de las aves. Generado por herramientas/armar_datos.py.\n'
          '   Puedes corregir los textos aquí mismo; si lo haces, no vuelvas a correr ese script. */\n'
          'window.AVES = ' + compacto(salida) + ';\n'
          'window.PROYECTO = ' + compacto(PROYECTO) + ';\n')
    with open(os.path.join(SITIO, 'datos.js'), 'w') as fh:
        fh.write(js)
    print('datos.js listo:', len(js) // 1024, 'KB · ilustraciones:', sum(1 for a in salida if 'ilus' in a), 'de', len(salida))


if __name__ == '__main__':
    main()

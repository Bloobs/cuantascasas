# Número de viviendas en alquiler

Dashboard web para consultar la oferta de viviendas en alquiler por provincias de España.

## Demo

Una vez activado **GitHub Pages** para este repositorio, el dashboard estará disponible en:

[Abrir el dashboard](https://bloobs.github.io/cuantascasas/)


## Características

- Mapa interactivo de España por provincias.
- Valor mostrado como el mayor dato disponible entre los portales.
- Tooltip con el detalle de cada portal.
- Comparación con el día, la semana o el mes anterior.
- Colores verde y rojo para indicar aumentos y descensos.
- Totales nacionales y totales por portal.
- Zoom y desplazamiento del mapa.
- Diseño responsive para ordenador, tablet y móvil.
- Modo claro y modo oscuro, con preferencia guardada en el navegador.

## Archivos principales

- [`index.html`](./index.html): dashboard completo, autocontenido y sin dependencias externas.
- [`housing_counts.json`](./housing_counts.json): histórico de datos agrupado por fecha.
- [`cuentacasas.py`](./cuentacasas.py): script opcional que obtiene los datos de los portales y actualiza el histórico.

El HTML y el JSON deben permanecer en la misma carpeta para que el dashboard pueda cargar los datos correctamente.

## Formato de los datos

El JSON utiliza una fecha como clave principal:

```json
{
  "2026-10-05": {
    "Madrid": {
      "idealista": 11208,
      "fotocasa": 9627,
      "pisos": 4073,
      "habitaclia": 8453,
      "oferta_estimada": 12889
    }
  }
}
```

Cada nueva ejecución de `cuentacasas.py` actualiza la fecha del día. Si se ejecuta varias veces en el mismo día, se reemplaza únicamente ese registro y no se crean duplicados.

## Ejecución local

El navegador debe cargar el HTML mediante HTTP para que `fetch()` pueda leer el JSON:

```bash
python3 -m http.server
```

Después abre [http://localhost:8000/](http://localhost:8000/).

## Actualización de datos

El script de Python consulta Idealista, Fotocasa, Pisos.com y Habitaclia. Antes de escribir el JSON valida los resultados: un valor `0` solo se acepta cuando el estado de la consulta es `OK`. Si un portal devuelve `0` junto con un error HTTP, bloqueo o error de consulta, la ejecución no actualiza el histórico para evitar guardar datos incorrectos.

Las dependencias necesarias para el actualizador son:

```bash
pip install camoufox curl-cffi beautifulsoup4
```

El dashboard publicado en GitHub Pages solo necesita estos dos archivos:

```text
index.html
housing_counts.json
```

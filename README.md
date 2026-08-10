# Mannheim Tree Cover Map (Baumfläche)

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE) [![Live map](https://img.shields.io/badge/status-live-brightgreen.svg)](https://abu-hamad.de/map/)

A web map of Mannheim. Every building is colored by the average tree cover within 60 meters of it. Dark and quiet. No account, nothing to install.

## Open the live map

**[Open the live map](https://abu-hamad.de/map/)**

![Mannheim tree cover map](screenshot/map.png)

The map interface is in German.

## What this map shows

Every building in Mannheim is colored by how much tree cover surrounds it. Cool blue colors mean leafy surroundings. Yellow, orange, and brown colors mean little shade. The dark theme keeps the colors easy to read.

## Why it matters

In summer 2026 Germany experienced a heatwave. In dense neighborhoods it gets especially hot. Trees are the city's natural shade. In July 2026, [SPIEGEL reported](https://www.spiegel.de/wissenschaft/natur/hitze-in-europa-wie-gut-stadtbaeume-vor-extremer-waerme-schuetzen-a-9a0b26e5-f8ae-4fa5-a897-2f2b026f5226) that around 30 percent of a building's 60 m surroundings should be shaded to protect against extreme heat. This map shows where shade is missing: yellow, orange, and brown buildings stand in surroundings with little tree cover.

## How to read the map

- **Colors.** A building's color is its tree-cover percentage within a 60 m radius. The legend runs from 0 to 100 percent.

- **Click a building.** The popup shows the exact percentage. It also marks whether the building reaches the 30 % shading guideline. It compares the building with its district and with the city.

- **Toggle "Bäume".** Switch the detected tree areas on or off. This lets you compare the colored buildings with the actual tree canopy.

- **Click a district.** The popup shows the district's average. It shows the rank among Mannheim's 38 districts. It also compares the district with the city.

- **"Mannheim im Überblick".** The overview card shows city-wide averages: mean tree cover, buildings with sufficient shade, and detected tree areas.

## Where the data comes from

The map starts with official aerial imagery (20 cm resolution) and building data for Mannheim. A computer-vision model detects tree canopy in the imagery. Each building gets the average tree-cover value within its 60 m surroundings. The current data release is 2026.01.

The result is a static, pre-computed map. The values are automatic estimates from aerial images. They are not measurements on the ground. The site has no server-side database or analytics. The only end-device write is the dismissal flag for the first-visit story modal. Standard HTTP connection data (IP, User-Agent, timestamp) reaches Cloudflare, BKG, MapLibre, and Ko-fi. The page is served through Cloudflare and loads the basemap, the glyph fonts, and the Ko-fi image from those origins. See the [Datenschutzerklärung](https://abu-hamad.de/map/datenschutz) for the full list.

## Credits

This map reproduces the presentation of [CityTreeCover](https://github.com/jcscaptures/CityTreeCover) by Jakob Schultz.

Map data:

**Buildings and city boundary.** LGL. Datenquelle: LGL, www.lgl-bw.de, dl-de/by-2-0 (Daten verändert). License text: [govdata.de/dl-de/by-2-0](https://www.govdata.de/dl-de/by-2-0).

**Base map.** © GeoBasis-DE / BKG (2026) dl-de/by-2-0. [bkg.bund.de](https://www.bkg.bund.de).

**Stadtteile.** Stadt Mannheim, GDI-MA, dl-de/by-2-0 (Daten verändert).

## License

This project is published under the [MIT License](LICENSE). The map data is used under its own terms. See the credits above.

## For developers

The source code is on [GitHub](https://github.com/donrami/MATreeCover). The front end uses [MapLibre GL JS 5.7.1](https://github.com/maplibre/maplibre-gl-js) and [PMTiles 4.4.0](https://github.com/protomaps/PMTiles). The data pipeline runs on Python 3.11. The pipeline, deployment, and tests are documented in [DEVELOPMENT.md](DEVELOPMENT.md).

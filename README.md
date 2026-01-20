# TerraForge v1.2.1 🗺️
**Procedural Biome/Island & Dungeon Map Generator using Simplex Noise**

**TerraForge** is a versatile Python toolset for procedural map generation. 

It includes tools for creating noise-based biome maps and multi-level dungeon layouts with fine-grained control over terrain shaping, biome placement, and dungeon structure.

***

## 🚀 Features
### 🌍 Biome Generator (TerraForge)
- Elevation, Moisture, and Temperature map generation
- Supports single and clustered multi-island generation
- Falloff support: Radial, Edge, or None
- Parameters for island spread, spacing, scale, and strength
- Basic biome color mapping based on environmental conditions
- Outputs high-resolution PNG images
- JSON preset import/export for reuse in games

## 🏰 Dungeon Generator (DungeonForge)
- Multi-level dungeon generation (3D stack of floors)
- Procedural room placement and corridor carving
- Up/down stairs for vertical navigation
- Console-based movement demo included
- Optional PNG export per dungeon level
- Tile color customization for export
- JSON preset import/export

***

## 📦 Requirements
* [noise](https://pypi.org/project/noise/)
* [numpy](https://pypi.org/project/numpy/)
* [pillow](https://pypi.org/project/pillow/)

***
## 📦 Installation
You can install TerraForge using [pip](https://pypi.org/project/terraforge-core/).
```
pip install terraforge-core
```

***

## 🧪 Demos

### Biome Map Generator
Run the included demo script:

```bash
python demo.py
```

The generated maps will be saved as biome_map, elevation_map, moisture_map, temperature_map, (noise_type)_map.

### Dungeon Map Generator
Run either the included dungeon_demo script or dungeon_demo1 script.
```
python dungeon_demo.py
```
Console based demo with movement.

```
python dungeon_demo1.py
```

Generates .pngs for each dungeon level. 

***

## 🚀 Usage - TerraForge (Biome Maps)
`from terraforge import TerraForge`

`generator = TerraForge(map_size=300, image_size=(600, 600))`

`generator.generate(output_dir="maps")`

## 🔁 Preset Workflow
```
generator.export_preset("world_preset.json")

generator.import_preset("world_preset.json")
generator.generate("maps")
```

***

## 🚀 Usage - DungeonForge (Dungeons)
`from dungeonforge import DungeonForge`

`generator = DungeonForge()`

`dungeon_map = generator.generate()`

## 🔁 Preset Workflow
```
generator.export_preset("dungeon_preset.json")

generator.import_preset("dungeon_preset.json")
generator.generate()
```

***
## ⚙️ Customization Options

### Biome Generator
Edit the values in terraforgepro.py or the demo to control:

- map_size and image_size

- falloff type: "radial", "edge", or None

- num_islands, island_spread, min_island_spacing

- noise types (elevation, moisture, temperature)

- biome_thresholds for  noise types (elevation, moisture, and temperature)

### Dungeon Generator
- Map size (width, height)
- Number of levels (z_levels)
- Maximum rooms and room size constraints
- Tile symbols and export colors
- Specify which levels to export (levels=[0, 2])
***
## Related Tools
### [TerraForge Studio](https://github.com/BriannaLadson/TerraForge/releases/tag/v0.1.0)
<img width="1366" height="768" alt="Screenshot (583)" src="https://github.com/user-attachments/assets/77317d68-3519-4ec8-85af-8072338c43bb" />

**A GUI tool built on top of the TerraForge library that allows you to quickly generate multi-level dungeons for games, prototypes, and tabletop use.**

***

## Related Libraries
* [CQCalendar](https://github.com/BriannaLadson/CQCalendar): A lightweight, tick-based time/calendar/lunar cycle system for Python games and simulations.
* [MoonTex](https://github.com/BriannaLadson/MoonTex): A procedural moon texture generator for Python that creates stylized, noise-based moon phase images.

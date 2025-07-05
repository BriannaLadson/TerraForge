# 🌍 TerraForge
A customizable Python tool for generating maps for games and simulations.

Features:
* 🗺️ Biome Maps – Generate overworld maps using customizable noise-based elevation
* 🏰 Dungeon Maps – Procedurally generate multi-level dungeons with rooms, corridors, and stairs
* 🖼️ Image Export – Export biome maps as images (PNG format)

***

## 🧰 Features
* Procedural elevation map generation using simplex noise
* Biome assignment based on elevation values
* Export elevation and biome maps as .png images
* Fully customizable noise and biome settings
* Image size and output directory control
* Customizable dungeon generator

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

## 🚀 Usage - TerraForge (Biome Maps)
`from terraforge import TerraForge`

`generator = TerraForge(map_size=300, image_size=(600, 600))`

`generator.generate(output_dir="maps")`

***

## 🚀 Usage - DungeonForge (Dungeons)
`from dungeonforge import DungeonForge`

`generator = DungeonForge()`

`dungeon_map = generator.generate()`

***
### 🚀 Want More Power? Try TerraForgePro
**[TerraForgePro](https://gum.co/u/rwq2bbml) adds:**
- Noise Types:
  - Elevation
  - Moisture
  - Temperature
 
- Island Falloff Shaping:
  - Radial (Default)
  - Edge (Coastal Shaping)
  - Archipelago (Multiple Island Centers)

💡 You can technically add moisture and temperature in the free version, but TerraForgePro handles it out of the box—plus you get new falloff types, better island generation, and future updates.

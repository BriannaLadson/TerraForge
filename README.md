# 🌍 TerraForge
A customizable Python tool for generating biome maps using noise-based elevation and image export.

***

## 🧰 Features
* Procedural elevation map generation using simplex noise
* Biome assignment based on elevation values
* Export elevation and biome maps as .png images
* Fully customizable noise and biome settings
* Image size and output directory control

***

## 📦 Requirements
* [noise](https://pypi.org/project/noise/)
* [numpy](https://pypi.org/project/numpy/)
* [pillow](https://pypi.org/project/pillow/)

***

## 🚀 Usage
`from terraforge import TerraForge`

`generator = TerraForge(map_size=300, image_size=(600, 600))`

`generator.generate(output_dir="maps")`

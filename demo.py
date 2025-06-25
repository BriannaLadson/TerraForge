from terraforge import TerraForge

elevation = {
	"seed": 0,
	"octaves": 10,
	"persistence": .5,
	"lacunarity": 2,
	"min_color": "#000000",
	"max_color": "#FFFFFF",
	"falloff": {
		"type": "radial",
		"strength": 0,
	},
	"zoom": 1,
}

noise_types = {
	"elevation": elevation,
}

generator = TerraForge(
	noise_types = noise_types,
)

generator.generate()

print("Check directory for generated maps!")
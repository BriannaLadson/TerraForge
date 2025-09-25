"""
This is a demo for TerraForge.
It generates a biome, elevation, moisture, and temperature map and saves them to the currency directory.
"""

from terraforge import TerraForge
import random

#Noise Types
elevation = {
	"seed": random.randint(0, 1000),
	"octaves": 10,
	"persistence": .5,
	"lacunarity": 2,
	"min_color": "#000000",
	"max_color": "#FFFFFF",
	"falloff": {
		"type": random.choice(["radial", "edge"]),
		"strength": .5,
	},
	"zoom": .25,
	"redistribution": 1
}

moisture = {
	"seed": random.randint(0, 1000),
	"octaves": 10,
	"persistence": .5,
	"lacunarity": 2,
	"min_color": "#000000",
	"max_color": "#0000FF",
	"falloff": {
		"type": random.choice(["radial", "edge"]),
		"strength": random.uniform(0, 1),
	},
	"zoom": 1,
	"redistribution": 1,
}

temperature = {
	"seed": random.randint(0, 1000),
	"octaves": 10,
	"persistence": .5,
	"lacunarity": 2,
	"min_color": "#000000",
	"max_color": "#FF0000",
	"falloff": {
		"type": random.choice(["radial", "edge"]),
		"strength": random.uniform(0, 1),
	},
	"zoom": 1,
	"redistribution": 1,
}

noise_types = {
	"elevation": elevation,
	"moisture": moisture,
	"temperature": temperature,
}

#Biomes
ocean = {
	"color": "#1E3A8A", 
	"rules": {
		"elevation":(0,.3),
	},
}

beach = {
	"color": "#F4A261", 
	"rules": {
		"elevation": (.3, .4)
	},
}

forest = {
	"color": "#3E7C3C", 
	"rules": {
		"elevation": (.4, .6), 
		"moisture": (.5,1)
	}
}

plains = {
	"color": "#A7C957", 
	"rules": {
		"elevation": (.4, .6), 
		"moisture":(0, .5)
	}
}

dry_highlands = {
	"color": "#DDA15E", 
	"rules": {
		"elevation": (.6, .8), 
		"moisture":(0, .5),
	}
}

wet_highlands = {
	"color": "#264653", 
	"rules": {
		"elevation": (.6, .8), 
		"moisture":(.5, 1)
	}
}

snowy_mountain = {
	"color": "#FFFFFF", 
	"rules": {
		"elevation": (.8, 1), 
		"temperature":(0,.4)
	}
}

rocky_mountain = {
	"color": "#707070", 
	"rules": {
		"elevation": (.8, 1), 
		"temperature":(.4,1)
	}
}

biomes = [
	ocean,
	beach,
	forest,
	plains,
	dry_highlands,
	wet_highlands,
	snowy_mountain,
	rocky_mountain,
]

generator = TerraForge(
	noise_types=noise_types,
	biomes = biomes,
	map_size = 300,
	image_size=None, #(width,height)
	num_islands = random.randint(1, 10),
	island_spread = random.uniform(.1, .3),
	min_island_spacing = None, # This has to be a postive integer.
)

generator.generate()

print("Maps Generated! Check the current directory!")
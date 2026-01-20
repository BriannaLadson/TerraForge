import noise
import numpy as np
from PIL import Image
import os
import json
from copy import deepcopy

class TerraForge:
	def __init__(
		self, 
		noise_types=None, 
		biomes=None, 
		map_size=300, 
		image_size=None, 
		num_islands=1, 
		island_spread=.3,
		min_island_spacing=None,
	):
		#Noise Types
		if noise_types is not None:
			self.noise_types = noise_types
			
		else:
			self.noise_types = {
				"elevation": {
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
					"zoom": .3,
					"redistribution": 1,
				},
				"moisture": {
					"seed": 0,
					"octaves": 10,
					"persistence": .5,
					"lacunarity": 2,
					"min_color": "#000000",
					"max_color": "#0000FF",
					"falloff": {
						"type": "radial",
						"strength": 0,
					},
					"zoom": .3,
					"redistribution": 1,
				},
				"temperature": {
					"seed": 0,
					"octaves": 10,
					"persistence": .5,
					"lacunarity": 2,
					"min_color": "#000000",
					"max_color": "#FF0000",
					"falloff": {
						"type": "radial",
						"strength": 0,
					},
					"zoom": .3,
					"redistribution": 1,
				},
			}
			
		#Biomes
		self.biomes = [
			{"color": "#1E3A8A", "rules": {"elevation":(0,.3)},}, #Ocean
			{"color": "#F4A261", "rules": {"elevation": (.3, .4)}}, #Beach
			{"color": "#3E7C3C", "rules": {"elevation": (.4, .6), "moisture": (.5,1)}}, #Forest
			{"color": "#A7C957", "rules": {"elevation": (.4, .6), "moisture":(0, .5)}}, #Plains
			{"color": "#DDA15E", "rules": {"elevation": (.6, .8), "moisture":(0, .5)}}, #Dry Highlands
			{"color": "#264653", "rules": {"elevation": (.6, .8), "moisture":(.5, 1)}}, #Wet Highlands
			{"color": "#FFFFFF", "rules": {"elevation": (.8, 1), "temperature":(0,.4)}}, #Snowy Mountains
			{"color": "#707070", "rules": {"elevation": (.8, 1), "temperature":(.4,1)}}, #Rocky Mountains
		]
		
		if not biomes == None:
			self.biomes = biomes
			
		#Map Size
		self.map_size = map_size
		
		#Image Size
		if image_size is None:
			self.image_size = (map_size, map_size)
			
		elif isinstance(image_size, int):
			self.image_size = (image_size, image_size)
			
		else:
			self.image_size = image_size
			
		#Island Settings
		self.num_islands = num_islands
		
		self.island_spread = island_spread
		
		self.min_island_spacing = (min_island_spacing if min_island_spacing is not None else int(self.map_size * .15))
		
	def generate(self, output_dir="."):
		os.makedirs(output_dir, exist_ok=True)
		
		self.generate_noise()
		
		self.export_noise_map_images(output_dir)
		
		self.export_biome_map_image(output_dir)
		
	def generate_noise(self):
		self.noise_maps = {}
		
		self.island_centers = self.generate_island_centers(count=self.num_islands, spacing=self.min_island_spacing)
		
		width = height = self.map_size
		center_x = self.map_size / 2
		center_y = self.map_size / 2
		max_distance = np.sqrt(center_x**2 + center_y**2)
		
		for noise_type, settings in self.noise_types.items():
			noise_map = np.zeros((self.map_size, self.map_size))
			
			falloff = settings.get("falloff", None)
			
			zoom = settings.get("zoom", 1)
			
			redistribution = settings.get("redistribution", 1)
			
			for y in range(self.map_size):
				for x in range(self.map_size):
					nx = (x / self.map_size - .5) / zoom
					ny = (y / self.map_size - .5) / zoom
					
					#Can also use noise.pnoise2 for Perlin
					noise_value = noise.snoise2(
						nx,
						ny,
						octaves=settings["octaves"],
						persistence=settings["persistence"],
						lacunarity=settings["lacunarity"],
						base=settings["seed"],
					)
					
					noise_value = noise_value / 2 + .5 # Normalize
					
					#Use Radial Falloff
					if falloff:
						falloff_type = falloff.get("type")
						strength = falloff.get("strength", 0)
						
						if falloff_type == "radial":
							if self.num_islands > 1:
								noise_value = self.apply_multi_radial_falloff(x, y, noise_value, self.island_centers, strength)
							
							else:
								noise_value = self.apply_radial_falloff(x, y, noise_value, width, height, strength)
					
						elif falloff_type == "edge":
							noise_value = self.apply_edge_falloff(x, y, noise_value, width, height, strength)
					
					noise_value = noise_value ** redistribution
					
					#Normalize between 0-1
					noise_map[y, x] = min(1, max(0, noise_value))
					
			self.noise_maps[noise_type] = noise_map
			
		#Assign Biomes
		self.assign_biomes()
		
	def apply_radial_falloff(self, x, y, noise_value, width, height, strength):
		if strength <= 0:
			return noise_value
			
		center_x, center_y = width // 2, height // 2
		max_distance = np.sqrt(center_x ** 2 + center_y ** 2)
		
		dx = x - center_x
		dy = y - center_y
		distance = np.sqrt(dx ** 2 + dy ** 2)
		
		radial = 1 - (distance / max_distance)
		radial = max(0, min(1, radial))
		
		return noise_value * ((1 - strength) + strength * radial)
		
	def apply_edge_falloff(self, x, y, noise_value, width, height, strength):
		if strength <= 0:
			return noise_value
			
		#Distance to nearest edge
		left = x
		right = width - x
		top = y
		bottom = height - y
		distance = min(left, right, top, bottom)
		
		max_distance = min(width, height) / 2 # Normalize based on half size
		edge_falloff = distance / max_distance
		edge_falloff = max(0, min(1, edge_falloff))
		
		return noise_value * ((1 - strength) + strength * edge_falloff)
		
	def apply_multi_radial_falloff(self, x, y, noise_value, centers, strength):
		if strength <= 0:
			return noise_value
			
		#Distance to nearest center
		closest = min(np.hypot(x - cx, y - cy) for cx, cy in centers)
		
		#Max possible distance is from one corner to the opposite corner
		max_dist = self.map_size * self.island_spread
		falloff = 1 - (closest / max_dist) # 1 at centre -> 0 at farthest edge
		falloff = max(0, min(1, falloff)) # clamp
		
		return noise_value * ((1 - strength) + strength * falloff)
		
	def generate_island_centers(self, count, spacing):
		centers = []
		attempts = 0
		max_attempts = count * 20
		
		while len(centers) < count and attempts < max_attempts:
			x = np.random.randint(0, self.map_size)
			y = np.random.randint(0, self.map_size)
			
			too_close = any(np.hypot(x - cx, y - cy) < spacing for cx, cy in centers)
			
			if not too_close:
				centers.append((x, y))
				
			attempts += 1
			
		return centers
		
	def assign_biomes(self):
		self.biome_map = np.empty((self.map_size, self.map_size), dtype=object)
		
		for y in range(self.map_size):
			for x in range(self.map_size):
				for biome in self.biomes:
					matches = True
					
					for noise_type, (min_val, max_val) in biome["rules"].items():
						value = self.noise_maps.get(noise_type, None)
						
						if value is None:
							matches = False
							break
							
						cell_value = value[y, x]
						
						if not (min_val <= cell_value <= max_val):
							matches = False
							break
							
					if matches:
						self.biome_map[y, x] = biome["color"]
						break
		
	def hex_to_rgb(self, hex_color):
		hex_color = hex_color.lstrip("#")
		
		return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
		
	def interpolate_color(self, c1, c2, t):
		return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))
		
	def export_noise_map_images(self, output_dir="."):
		for noise_type, noise_map in self.noise_maps.items():
			settings = self.noise_types[noise_type]
			min_color = self.hex_to_rgb(settings.get("min_color", "#000000"))
			max_color = self.hex_to_rgb(settings.get("max_color", "#FFFFFF"))
			
			img_width, img_height = self.image_size
			img = Image.new("RGB", (img_width, img_height))
			scale_x = self.map_size / img_width
			scale_y = self.map_size / img_height
			
			for y in range(img_height):
				for x in range(img_width):
					source_x = int(x * scale_x)
					source_y = int(y * scale_y)
					
					value = noise_map[source_y, source_x]
					color = self.interpolate_color(min_color, max_color, value)
					img.putpixel((x, y), color)
					
			img.save(f"{output_dir}/{noise_type}_map.png")
			
	def export_biome_map_image(self, output_dir="."):
		img_width, img_height = self.image_size
		
		img = Image.new("RGB", (img_width, img_height))
		
		scale_x = self.map_size / img_width
		scale_y = self.map_size / img_height
		
		for y in range(img_height):
			for x in range(img_width):
				source_x = int(x * scale_x)
				source_y = int(y * scale_y)
				
				hex_color = self.biome_map[source_y, source_x]
				rgb_color = self.hex_to_rgb(hex_color)
				img.putpixel((x, y), rgb_color)
				
		img.save(f"{output_dir}/biome_map.png")
		
	def tile_color(self, x:int, y:int, default="#000000"):
		if not hasattr(self, "biome_map") or self.biome_map is None:
			raise RuntimeError("assign_biomes() has not been run")
		
		x %= self.map_size
		y %= self.map_size
			
		return self.biome_map[y,x]

		
	def export_preset(self, path: str):
		"""Save this TerraForge configuration as a JSON preset."""
		preset = {
			"version": "1.0",
			"map_size": int(self.map_size),
			"image_size": [int(self.image_size[0]), int(self.image_size[1])],
			"num_islands": int(self.num_islands),
			"island_spread": float(self.island_spread),
			"min_island_spacing": int(self.min_island_spacing),
			"noise_types": self.noise_types,
			"biomes": self.biomes,
		}
		
		os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
		with open(path, "w", encoding="utf-8") as f:
			json.dump(preset, f, indent=4)


	def import_preset(self, path: str):
		"""Load a TerraForge configuration from a JSON preset onto this instance."""
		with open(path, "r", encoding="utf-8") as f:
			data = json.load(f)
		
		self._validate_preset(data)
		
		# Apply values (fallback to existing if missing)
		self.map_size = int(data.get("map_size", self.map_size))
		
		image_size = data.get("image_size", [self.image_size[0], self.image_size[1]])
		if isinstance(image_size, list):
			self.image_size = (int(image_size[0]), int(image_size[1]))
		
		self.num_islands = int(data.get("num_islands", self.num_islands))
		self.island_spread = float(data.get("island_spread", self.island_spread))
		
		if "min_island_spacing" in data:
			self.min_island_spacing = int(data["min_island_spacing"])
		
		if "noise_types" in data:
			self.noise_types = data["noise_types"]
		
		if "biomes" in data:
			self.biomes = data["biomes"]
		
		if hasattr(self, "noise_maps"):
			delattr(self, "noise_maps")
		if hasattr(self, "biome_map"):
			delattr(self, "biome_map")
		if hasattr(self, "island_centers"):
			delattr(self, "island_centers")


	def _validate_preset(self, data: dict):
		if not isinstance(data, dict):
			raise ValueError("Preset must be a JSON object.")
		
		if "version" in data and not isinstance(data["version"], str):
			raise ValueError("'version' must be a string.")
		
		if "noise_types" in data and not isinstance(data["noise_types"], dict):
			raise ValueError("'noise_types' must be a dict.")
		
		if "biomes" in data and not isinstance(data["biomes"], list):
			raise ValueError("'biomes' must be a list.")
		
		if "image_size" in data:
			img = data["image_size"]
			if not (isinstance(img, (list, tuple)) and len(img) == 2):
				raise ValueError("'image_size' must be [width, height].")
	
	
	
	
	
	
	
	
	
	
	
	
	
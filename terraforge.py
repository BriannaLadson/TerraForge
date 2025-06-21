import noise
import numpy as np
from PIL import Image
import os

class TerraForge:
	def __init__(self, noise_types=None, biomes=None, map_size=100, image_size=None):
		#Noise Types
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
			}
		}
		
		if noise_types:
			self.noise_types.update(noise_types)
			
		#Biomes
		self.biomes = [
			{"color": "#1E3A8A", "rules": {"elevation":(0,.3)},}, #Ocean
			{"color": "#F4A261", "rules": {"elevation": (.3, .4)}}, #Beach
			{"color": "#3E7C3C", "rules": {"elevation": (.4, .6)}}, #Lowlands
			{"color": "#264653", "rules": {"elevation": (.6, .8)}}, #Highlands
			{"color": "#707070", "rules": {"elevation": (.8, 1)}}, #Mountains
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
		
	def generate(self, output_dir="."):
		os.makedirs(output_dir, exist_ok=True)
		
		self.generate_noise()
		
		self.assign_biomes()
		
		self.export_noise_map_images(output_dir)
		
		self.export_biome_map_image(output_dir)
		
	def generate_noise(self):
		self.noise_maps = {}
		
		width = height = self.map_size
		center_x = self.map_size / 2
		center_y = self.map_size / 2
		max_distance = np.sqrt(center_x**2 + center_y**2)
		
		for noise_type, settings in self.noise_types.items():
			noise_map = np.zeros((self.map_size, self.map_size))
			
			falloff = settings.get("falloff", None)
			
			for y in range(self.map_size):
				for x in range(self.map_size):
					nx = (x / self.map_size - .5)
					ny = (y / self.map_size - .5)
					
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
					if falloff and falloff.get("type") == "radial":
						falloff_type = falloff.get("type")
						strength = falloff.get("strength", 0)
						
						if falloff_type == "radial":
							noise_value = self.apply_radial_falloff(x, y, noise_value, width, height, strength)
					
					#Normalize between 0-1
					noise_map[y, x] = min(1, max(0, noise_value))
					
		self.noise_maps[noise_type] = noise_map
		
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

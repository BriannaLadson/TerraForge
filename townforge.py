import random
import numpy as np
from PIL import Image, ImageDraw

class TownForge:
	GROUND = 0
	BUILDING = 1
	DOOR = 2
	
	def __init__(
		self, 
		building_types=None, 
		map_size=300, 
		seed=None,
		image_size=None,
		building_padding=4,
		ground_color="#3E7C3C",
		door_color="#FFD700",
		outline_color="black",
		max_failures_multiplier=20,
		door_sides=("north", "south", "east", "west"),
		map_edge_padding=5,
		door_inset=1,
	):
		# Building Types
		if building_types is not None:
			self.building_types = building_types
			
		else:
			self.building_types = {
				"house": {
					"id": "house",
					"name": "House",
					"color": "#8B5A2B",
					"size": (8, 14),
					"min_quantity": 30,
					"max_quantity": 80,
					"priority": 1,
				},
				"shop": {
					"id": "shop",
					"name": "Shop",
					"color": "#708090",
					"size": (10, 16),
					"min_quantity": 8,
					"max_quantity": 20,
					"priority": 10,
				},
				"tavern": {
					"id": "tavern",
					"name": "Tavern",
					"color": "#A239F6",
					"size": (12, 18),
					"min_quantity": 2,
					"max_quantity": 5,
					"priority": 20,
				},
				"temple": {
					"id": "temple",
					"name": "Temple",
					"color": "#0EC2F7",
					"size": (18, 26),
					"min_quantity": 1,
					"max_quantity": 3,
					"priority": 30,
				},
				"guildhall": {
					"id": "guildhall",
					"name": "Guildhall",
					"color": "#556B2F",
					"size": (18, 24),
					"min_quantity": 1,
					"max_quantity": 3,
					"priority": 35,
				},
				"castle": {
					"id": "castle",
					"name": "Castle",
					"color": "#696969",
					"size": (35, 50),
					"min_quantity": 0,
					"max_quantity": 1,
					"priority": 100,
				},
			}
			
		self.buildings = []
		
		self.map_size = map_size
		
		self.rng = random.Random(seed)
		
		self.seed = seed
		
		if image_size is None:
			self.image_size = (map_size, map_size)
			
		elif isinstance(image_size, int):
			self.image_size = (image_size, image_size)
			
		else:
			self.image_size = image_size
			
		self.building_padding = building_padding
		
		self.ground_color = ground_color
		
		self.door_color = door_color
		
		self.outline_color = outline_color
		
		self.max_failures_multiplier = max_failures_multiplier
		
		self.door_sides = door_sides
		
		self.map_edge_padding = map_edge_padding
		
		self.door_inset = door_inset
		
	def generate(self):
		self.buildings = []
		
		self.town_map = np.full(
			(self.map_size, self.map_size),
			self.GROUND,
			dtype=np.uint8
		)
		
		self.place_buildings()
		
		return self.town_map
		
	def place_buildings(self):
		sorted_building_types = sorted(
			self.building_types.items(),
			key=lambda item: item[1].get("priority", 0),
			reverse=True,
		)
		
		for building_type_id, building_type in sorted_building_types:
			quantity = self.rng.randint(
				building_type["min_quantity"],
				building_type["max_quantity"]
			)
			
			placed = 0
			failures = 0
			max_failures = quantity * self.max_failures_multiplier
			
			while placed < quantity and failures < max_failures:
				success = self.place_building(building_type_id, building_type, placed)
				
				if success:
					placed += 1
					
				else:
					failures += 1
				
	def place_building(self, building_type_id, building_type, index):
		min_size, max_size = building_type["size"]
		
		width = self.rng.randint(min_size, max_size)
		height = self.rng.randint(min_size, max_size)
		
		x = self.rng.randint(self.map_edge_padding, self.map_size - width - self.map_edge_padding)
		y = self.rng.randint(self.map_edge_padding, self.map_size - height - self.map_edge_padding)
		
		building = {
			"id": f"{building_type_id}_{index}",
			"type": building_type_id,
			"name": building_type["name"],
			"x": x,
			"y": y,
			"width": width,
			"height": height,
			"color": building_type["color"],
		}
		
		door_x, door_y = self.get_random_door_position(building)
		
		building["door"] = (door_x, door_y)
		
		if self.overlaps_existing(building, self.building_padding):
			return False
		
		self.buildings.append(building)
		
		self.town_map[y:y + height, x:x + width] = self.BUILDING
		
		self.town_map[door_y, door_x] = self.DOOR
		
		return True
		
	def overlaps_existing(self, new_building, padding=4):
		x1 = new_building["x"]
		y1 = new_building["y"]
		
		x2 = x1 + new_building["width"]
		y2 = y1 + new_building["height"]
		
		for building in self.buildings:
			bx1 = building["x"]
			by1 = building["y"]
			
			bx2 = bx1 + building["width"]
			by2 = by1 + building["height"]
			
			if (
				x1 < bx2 + padding and
				x2 + padding > bx1 and
				y1 < by2 + padding and
				y2 + padding > by1
			):
				return True
		
		return False
		
	def get_random_door_position(self, building):
		x = building["x"]
		y = building["y"]
		
		width = building["width"]
		height = building["height"]
		
		side = self.rng.choice(self.door_sides)
		inset = self.door_inset
		
		if side == "north":
			return self.rng.randint(x + inset, x + width - 1 - inset), y
			
		elif side == "south":
			return self.rng.randint(x + inset, x + width - 1 - inset), y + height - 1
			
		elif side == "east":
			return x + width - 1, self.rng.randint(y + inset, y + height - 1 - inset)
			
		else:
			return x, self.rng.randint(y + inset, y + height - 1 - inset)
		
	def export_town_map_image(self, output_dir=".", show_building_names=False, building_name_color="white"):
		if not hasattr(self, "town_map"):
			raise ValueError("Town map has not been generated yet. Call generate() first.")
			
		img = Image.new("RGB", self.image_size, "white")
		draw = ImageDraw.Draw(img)
		
		cell_w = self.image_size[0] / self.map_size
		cell_h = self.image_size[1] / self.map_size
		
		#Draw Ground
		draw.rectangle(
			[0, 0, self.image_size[0], self.image_size[1]],
			fill=self.ground_color
		)
		
		#Draw Buildings
		for building in self.buildings:
			x0 = int(building["x"] * cell_w)
			y0 = int(building["y"] * cell_h)
			
			x1 = int((building["x"] + building["width"]) * cell_w)
			y1 = int((building["y"] + building["height"]) * cell_h)
			
			draw.rectangle(
				[x0, y0, x1, y1],
				fill=building["color"],
				outline=self.outline_color
			)
				
			#Draw Doors
			door_x, door_y = building["door"]
			
			dx0 = int(door_x * cell_w)
			dy0 = int(door_y * cell_h)
			
			dx1 = int((door_x + 1) * cell_w)
			dy1 = int((door_y + 1) * cell_h)
			
			draw.rectangle(
				[dx0, dy0, dx1, dy1],
				fill=self.door_color
			)
			
			if show_building_names:
				cx = (x0 + x1) // 2
				cy = (y0 + y1) // 2
				
				draw.text(
					(cx, cy),
					building["name"],
					fill=building_name_color,
					anchor="mm"
				)
			
		img.save(f"{output_dir}/town_map.png")
		
	def get_building_at(self, x, y):
		for building in self.buildings:
			if (
				building["x"] <= x < building["x"] + building["width"] and
				building["y"] <= y < building["y"] + building["height"]
			):
				return building
				
		return None
		
	def get_building_by_door(self, x, y):
		for building in self.buildings:
			if building["door"] == (x, y):
				return building
				
		return None
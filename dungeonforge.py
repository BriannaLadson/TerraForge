import random
import numpy as np
from PIL import Image, ImageDraw
import os

class DungeonForge:
	FLOOR = 0
	WALL = 1
	UP = 2
	DOWN = 3
	
	def __init__(
		self,
		level_size = 25,
		room_size = (3, 6),
		max_rooms = 10,
		max_failure = 10,
		z_levels = 3,
		seed = None,
		image_size = None,
	):	
		
		self.min_room_size = room_size[0]
		self.max_room_size = room_size[1]
		self.max_rooms = max_rooms
		self.rooms = []
		
		if level_size is None or level_size <=0:
			level_size = 25
		
		min_level_size = self.max_room_size + 2
		
		if level_size < min_level_size:
			level_size = min_level_size
			
		self.level_size = int(level_size)
		
		self.max_failure = max_failure
		
		self.z_levels = z_levels
		
		self.rng = random.Random(seed)
		
		if image_size is None:
			self.image_size = (self.level_size * 16, self.level_size * 16)
			
		elif isinstance(image_size, int):
			if image_size <= 0:
				self.image_size = (self.level_size * 16, self.level_size * 16)
			
			else:
				self.image_size = (image_size, image_size)
			
		else:
			w, h = image_size
			
			if w <= 0 or h <= 0:
				self.image_size = (self.level_size * 16, self.level_size * 16)
				
			else:
				self.image_size = (int(w), int(h))
			
	def generate(self):
		self.dungeon_map = [self.generate_level() for _ in range(self.z_levels)]
		
		self.place_stairs()
		
		return self.dungeon_map
		
	def generate_level(self):
		level = np.full((self.level_size, self.level_size), self.WALL, dtype=np.uint8)
		self.rooms = []
		failures = 0
		
		while len(self.rooms) < self.max_rooms and failures < self.max_failure:
			w = self.rng.randint(self.min_room_size, self.max_room_size)
			h = self.rng.randint(self.min_room_size, self.max_room_size)
			x = self.rng.randint(1, self.level_size - w - 1)
			y = self.rng.randint(1, self.level_size - h - 1)
			
			new_room = (x, y, x + w, y + h)
			
			if self.overlaps_existing(new_room):
				failures += 1
				continue
				
			self.create_room(level, new_room)
			self.rooms.append(new_room)
			
		self.connect_rooms(level)
			
		return level
		
	def overlaps_existing(self, new_room):
		x1, y1, x2, y2 = new_room
		
		for room in self.rooms:
			rx1, ry1, rx2, ry2 = room
			
			if (x1 <= rx2 and x2 >= rx1 and y1 <= ry2 and y2 >= ry1):
				return True
				
		return False
		
	def create_room(self, level, room):
		x1, y1, x2, y2 = room
		
		level[y1:y2, x1:x2] = self.FLOOR
		
	def center(self, room):
		x1, y1, x2, y2 = room
		
		return ((x1 + x2) // 2, (y1 + y2) // 2)
		
	def connect_rooms(self, level):
		for i in range(len(self.rooms) - 1):
			(x1, y1) = self.center(self.rooms[i])
			(x2, y2) = self.center(self.rooms[i + 1])
			
			if self.rng.choice([True, False]):
				self.dig_h_corridor(level, x1, x2, y1)
				self.dig_v_corridor(level, y1, y2, x2)
				
			else:
				self.dig_v_corridor(level, y1, y2, x1)
				self.dig_h_corridor(level, x1, x2, y2)
				
	def dig_h_corridor(self, level, x1, x2, y):
		if x1 > x2: 
			x1, x2, = x2, x1
			
		level[y, x1:x2+1] = self.FLOOR
			
	def dig_v_corridor(self, level, y1, y2, x):
		if y1 > y2:
			y1, y2 = y2, y1
			
		level[y1:y2+1, x] = self.FLOOR
			
	def place_stairs(self):
		for z in range(self.z_levels - 1):
			level_a = self.dungeon_map[z]
			level_b = self.dungeon_map[z + 1]
			
			ys, xs = np.where((level_a == self.FLOOR) & (level_b == self.FLOOR))
			
			if len(xs):
				idx = self.rng.randrange(len(xs))
				y, x = int(ys[idx]), int(xs[idx])
					
			else:
				ay, ax = np.where(level_a == self.FLOOR)
				if len(ax) == 0:
					raise RuntimeError("No floor tiles to place stairs.")
				
				idx = self.rng.randrange(len(ax))
				y, x = int(ay[idx]), int(ax[idx])
				
				if level_b[y, x] == self.WALL:
					level_b[y, x] = self.FLOOR
					self.ensure_accessible(level_b, y, x)				
			
			level_a[y, x] = self.DOWN
			level_b[y, x] = self.UP
			
			self.ensure_accessible(level_a, y, x)
			self.ensure_accessible(level_b, y, x)
			
	def ensure_accessible(self, level:np.ndarray, y:int, x:int):
		for dy, dx in ((1,0), (-1,0), (0,1), (0,-1)):
			ny, nx = y + dy, x + dx
			if 0 <= ny < self.level_size and 0 <= nx < self.level_size:
				if level[ny, nx] == self.FLOOR:
					return
					
		best_d, ty, tx = self.level_size**2, None, None
		ys, xs = np.where(level == self.FLOOR)
		
		for fy, fx in zip(ys, xs):
			d = abs(int(fy) - y) + abs(int(fx) - x)
			
			if d and d < best_d:
				best_d, ty, tx = d, int(fy), int(fx)
		
		if tx is None:
			for dy in (-1,0,1):
				for dx in (-1,0,1):
					ny, nx = y + dy, x + dx
					if 0 <= ny < self.level_size and 0 <= nx < self.level_size:
						level[ny, nx] = self.FLOOR
						
				return
				
		self.dig_h_corridor(level, x, tx, y)
		self.dig_v_corridor(level, y, ty, tx)
				
	def connect_isolated_tile(self, level, start_pos):
		for y in range(self.level_size):
			for x in range(self.level_size):
				if level[y, x] == self.FLOOR and (x, y) != start_pos:
					path = self.get_cooridor_path(start_pos, (x, y))
					if path:
						for px, py in path:
							if 0 <= px < self.level_size and 0 <= py < self.level_size:
								if level[py, px] == self.WALL:
									level[py, px] = self.FLOOR
						return 
						
	def export_dungeon_map_images(self, output_dir=".", levels=None, tile_colors=None):
		if not hasattr(self, "dungeon_map"):
			raise ValueError("Dungeon map has not been generated yet. Call generate() first.")
			
		if levels is None or levels == "all":
			level_indices = list(range(self.z_levels))
			
		elif isinstance(levels, int):
			level_indices = [levels]
			
		else:
			level_indices = list(levels)
			
		default_tile_colors = {
			self.FLOOR: (255, 255, 255),
			self.WALL: (0, 0, 0),
			self.UP: (0, 255, 0),
			self.DOWN: (255, 0, 0),
		}
		
		if tile_colors is None:
			tile_colors = default_tile_colors
			
		else:
			for key, val in default_tile_colors.items():
				tile_colors.setdefault(key, val)
		
		for i in level_indices:
			if i < 0 or i >= len(self.dungeon_map):
				continue
				
			level = self.dungeon_map[i]
			img = Image.new("RGB", self.image_size, "white")
			draw = ImageDraw.Draw(img)
			
			cell_w = self.image_size[0] / self.level_size
			cell_h = self.image_size[1] / self.level_size
			
			for y in range(self.level_size):
				for x in range(self.level_size):
					color = tile_colors.get(level[y, x], (128, 128, 128))
					
					x0 = int(x * cell_w)
					y0 = int(y * cell_h)
					x1 = int((x + 1) * cell_w)
					y1 = int((y + 1) * cell_h)
					
					draw.rectangle([x0, y0, x1, y1], fill=color)
					
			img.save(os.path.join(output_dir, f"dungeon_level_{i}.png"))
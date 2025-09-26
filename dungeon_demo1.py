from dungeonforge import DungeonForge

generator = DungeonForge(
	level_size = 25, # Dungeon Size
	room_size = (3, 6), # Min/Max Room Size
	max_rooms = 10, # Max Rooms Per Level
	max_failure = 10, # Max Generation Failures Per Level
	z_levels = 3, # Max Levels
	seed = None, # Pass In the Same Seed/Settings to Get the Same Dungeon
	image_size = None, # Size of Generated Images
)

dungeon_map = generator.generate()

generator.export_dungeon_map_images(
	output_dir=".", # Where Generated Images are Stored
	levels=None, # Levels You Want Images Generated For
	tile_colors=None, # What Color You Want Each Tile Type to Be
)
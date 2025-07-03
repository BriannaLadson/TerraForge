"""
Cross-platform console demo for DungeonForge.
Keys:
	W A S D – move
	<       – use an UP stair (go up a level)
	>       – use a DOWN stair (go down a level)
	Q       – quit
"""
import os, sys, platform
import numpy as np
from dungeonforge import DungeonForge
import random

def _unix_getch():
	import tty, termios
	fd  = sys.stdin.fileno()
	old = termios.tcgetattr(fd)
	try:
		tty.setraw(fd)
		ch = sys.stdin.read(1)
	finally:
		termios.tcsetattr(fd, termios.TCSADRAIN, old)
	return ch

def _win_getch():
	import msvcrt
	return msvcrt.getch().decode("utf-8", "ignore")

def _fallback_getch():
	return input("> ")[0:1] if sys.stdin.readable() else "q"

if platform.system() == "Windows":
	getch = _win_getch
else:
	try:
		getch = _unix_getch
		import termios, tty 
	except Exception:
		getch = _fallback_getch

generator = DungeonForge(
	level_size=random.randint(20, 30), 
	max_rooms=random.randint(5, 10), 
	z_levels=random.randint(3, 10), 
	seed=random.randint(0, 100))
dungeon = generator.generate()
level_h, level_w = dungeon[0].shape

GLYPH = {
	DungeonForge.FLOOR: ".",
	DungeonForge.WALL : "#",
	DungeonForge.UP   : "<",
	DungeonForge.DOWN : ">"
}

z  = 0
ys, xs = np.where(dungeon[0] == DungeonForge.UP)
if len(xs) == 0:
	ys, xs = np.where(dungeon[0] == DungeonForge.FLOOR)
py, px = int(ys[0]), int(xs[0])


def clear_screen():
	os.system("cls" if platform.system() == "Windows" else "clear")

def draw():
	clear_screen()
	print(f"Level {z}  (WASD move, < up, > down, Q quit)\n")
	for y in range(level_h):
		row = []
		for x in range(level_w):
			row.append("@") if (y, x) == (py, px) else row.append(GLYPH[dungeon[z][y, x]])
		print("".join(row))
		
while True:
	draw()
	key = getch().lower()

	if key == "q":
		break

	dy = dx = 0
	if key == "w":	dy = -1
	elif key == "s":	dy =  1
	elif key == "a":	dx = -1
	elif key == "d":	dx =  1
	elif key == ">":		# go down
		if dungeon[z][py, px] == DungeonForge.DOWN and z < len(dungeon) - 1:
			z += 1
			continue
	elif key == "<":		# go up
		if dungeon[z][py, px] == DungeonForge.UP and z > 0:
			z -= 1
			continue
	else:
		continue	# ignore unknown keys

	ny, nx = py + dy, px + dx
	if 0 <= ny < level_h and 0 <= nx < level_w:
		if dungeon[z][ny, nx] != DungeonForge.WALL:
			py, px = ny, nx

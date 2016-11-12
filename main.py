import libtcodpy as libtcod
import random
from src.entity import Entity
from src.tile import Tile
from src.rectangle import Rect

# Core logic function.
def handle_logic():

	key = libtcod.console_wait_for_keypress(True)
	if handle_player(key): # If the exit key is pressed
		return True # Exit

	#handle_entities()

# Takes a key press from the player, and updates their state based on it
def handle_player(key):
	if key.vk == libtcod.KEY_ENTER and key.lalt:
		#Alt+Enter: toggle fullscreen
		libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

	elif key.vk == libtcod.KEY_ESCAPE:
		return True  #exit game FIXME

	global player

	movex = movey = 0

	#movement keys
	if libtcod.console_is_key_pressed(libtcod.KEY_UP):
		movey -= 1

	elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN):
		movey += 1

	elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT):
		movex -= 1

	elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT):
		movex += 1

	player.move(movex, movey, map)
	global stairs
	if stairs.x == player.x and stairs.y == player.y:
		make_map()

# Loops through all the entities and figures out what they should be doing on this tick
def handle_entities():
	print "handled"

def make_map():
	global map

	map = [[Tile(True)
		for y in range(MAP_HEIGHT)]
			for x in range(MAP_WIDTH)]

	rooms = []
	num_rooms = 0
	for r in range(MAX_ROOMS):
		w = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
		h = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
		x = libtcod.random_get_int(0, 0, MAP_WIDTH - w - 1)
		y = libtcod.random_get_int(0, 0, MAP_HEIGHT - h - 1)
		new_room = Rect(x, y, w, h)
		intersected = False
		for room in rooms:
			if new_room.overlap(room):
				intersected = True
				break

		if not intersected:
			create_room(new_room)
			(newx,newy) = new_room.center()
			if num_rooms == 0:
				player.x = newx
				player.y = newy
			else:
				(prevx, prevy) = rooms[num_rooms-1].center();
				if libtcod.random_get_int(0, 0, 1) == 1:
					create_horz_tunnel(prevx, newx, prevy)
					create_vert_tunnel(prevy, newy, newx)
				else:
					create_vert_tunnel(prevy, newy, prevx)
					create_horz_tunnel(prevx, newx, newy)
			rooms.append(new_room)
			num_rooms += 1
	stairs_index = random.randint(1, num_rooms-1)
	(stairsx, stairsy) = rooms[stairs_index].center()
	global stairs
	stairs.clear()
	del entities[0]
	stairs = Entity(stairsx, stairsy, '=', libtcod.red, con, 'object', 'stairs', [], {})
	entities.insert(0, stairs)

def get_entity(x, y):
	for entity in entities:
		if entity.x == x and entity.y == y:
			return entity

	return False

def create_room(room):
	global map
	#go through the tiles in the rectangle and make them passable
	for x in range(room.x1 + 1, room.x2):
		for y in range(room.y1 + 1, room.y2):
			map[x][y].blocked = False
			map[x][y].block_sight = False

def create_horz_tunnel(x1, x2, y):
	global map
	for x in range(min(x1, x2), max(x1, x2) + 1):
		map[x][y].blocked = False
		map[x][y].block_sight = False

def create_vert_tunnel(y1, y2, x):
	global map
	for y in range(min(y1, y2), max(y1, y2) + 1):
		map[x][y].blocked = False
		map[x][y].block_sight = False

def render_all():

	for entity in entities:
		entity.draw();

	for y in range(MAP_HEIGHT):
		for x in range(MAP_WIDTH):
			wall = map[x][y].block_sight
			if wall:
				libtcod.console_set_char_background(con, x, y, color_dark_wall, libtcod.BKGND_SET)
			else:
				libtcod.console_set_char_background(con, x, y, color_dark_ground, libtcod.BKGND_SET)

	libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)

SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
color_dark_wall = libtcod.Color(50, 50, 50)
color_dark_ground = libtcod.Color(100, 100, 100)

MAP_WIDTH = 80
MAP_HEIGHT = 45

ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 60

LIMIT_FPS = 20

libtcod.console_set_custom_font('dejavu16x16_gs_tc.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)

libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'All-American Lawnmower Task Force', False)
con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)
libtcod.sys_set_fps(LIMIT_FPS)

initialStats = {"health":100, "attack":10, "defense":0.0, "nourishment":100}

player = Entity(SCREEN_WIDTH/2, SCREEN_HEIGHT/2, '@', libtcod.white, con, "Player", "Apple Johnnyseed", ["hands"], initialStats)
stairs = Entity(0, 0, '=', libtcod.red, con, 'object', 'stairs', [], {})
entities = [stairs, player]
make_map()
while not libtcod.console_is_window_closed():
	render_all()
	for entity in entities:
		entity.clear()
	libtcod.console_flush()
	exit = handle_logic() # Update game logic
	if exit:
		break

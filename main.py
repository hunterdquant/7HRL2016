import libtcodpy as libtcod
import random
from src.entity import Entity
from src.tile import Tile
from src.rectangle import Rect

# Core logic function.
def handle_logic():

	global player

	key = libtcod.console_wait_for_keypress(True)
	player_command = handle_input(key, player)
	if player_command[0] == "E" : # If the exit key is pressed
		return True # Exit
	elif player_command[0] == "U" : # If no valid key is pressed
		return False # Pass

	handle_player(player_command, player)

	handle_entities()

	global entities
	for i in range(0, len(entities)):
		if entities[i].group == "objects":
			if entities[i].stats["health"] <= 0:
				del entities[i]

# Takes a key press from the player, and updates their state based on it
def handle_input(key, player):
	if key.vk == libtcod.KEY_ENTER and key.lalt:
		#Alt+Enter: toggle fullscreen
		libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

	elif key.vk == libtcod.KEY_ESCAPE:
		return "E"  #exit game

	move_x = move_y = 0

	#movement keys
	if libtcod.console_is_key_pressed(libtcod.KEY_UP):
		move_y -= 1

	elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN):
		move_y += 1

	elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT):
		move_x -= 1

	elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT):
		move_x += 1

	elif libtcod.console_is_key_pressed(libtcod.KEY_DELETE):
		print "waiting!"
		move_x += 0
		move_y += 0

	else:
		return "U" # Useless keypress

	return [move_x, move_y]

# Loops through all the entities and figures out what they should be doing on this tick
def handle_entities():
	global entities
	print "AGH"
	#for entity in entities:
		#if entity.group == "enemy":
		#	planx = entity.x + random.randint(-1, 1);
		#	plany = entity.y + random.randint(-1, 1);
		#	while (map[planx][plany].blocked):
		#		planx = entity.x + random.randint(-1, 1);
		#		plany = entity.y + random.randint(-1, 1);

def get_random_enemy():
	global enemy_types
	idx = random.randint(0, len(enemy_types) - 1)
	etype = enemy_types[idx]
	if etype == enemy_types[0]:
		return Entity(0, 0, 'G', libtcod.yellow, con, "enemy", etype, [], {"health":25,"damage":5,"defense":0.0,"nourishment":100})
	elif etype == enemy_types[1]:
		return Entity(0, 0, 'N', libtcod.white, con, "enemy", etype, [], {"health":25,"damage":5,"defense":0.0,"nourishment":100})
	elif etype == enemy_types[2]:
		return Entity(0, 0, 'B', libtcod.orange, con, "enemy", etype, [], {"health":25,"damage":5,"defense":0.0,"nourishment":100})
	elif etype == enemy_types[3]:
		return Entity(0, 0, 'L', libtcod.cyan, con, "enemy", etype, [], {"health":25,"damage":5,"defense":0.0,"nourishment":100})


# Handles player commands based on previously parsed input
def handle_player(player_command, player):
	move_x = player_command[0]
	move_y = player_command[1]

	planned_x = player.x + move_x
	planned_y = player.y + move_y

	move_entity = get_entity(planned_x, planned_y)
	print move_entity

	if move_entity:
		# Do thing!
		handle_single_entity(move_entity)
	else:
		# Coast is clear, feel free to run move function
		player.move(move_x, move_y, map)

# Handle a single entity, as seen by player
def handle_single_entity(sent):
	global player

	if sent.group == "player":
		# Do nothing
		return;

	elif sent.group == "object":

		if sent.name == "stairs":
			global entities
			global player
			global stairs
			for entity in entities:
				entity.clear()

			entities = []

			entities.append(stairs)
			entities.append(player)

			make_map()
			return;

	elif sent.group == "item":
		return;

	elif sent.group == "enemy":
		# Attack the enemy!
		sent.stats["health"] = sent.stats["health"] - player.stats["attack"]
		if sent.stats["health"] <= 0:
			sent.clear()
			return
		player.stats["health"] = player.stats["health"] - sent.stats["damage"] 
		if player.stats["health"] <= 0:
			print "YOU DED SON"
			exit()
			return

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
			else: # Not player spawn!
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
	stairs = Entity(stairsx, stairsy, '=', libtcod.blue, con, 'object', 'stairs', [], {})
	entities.insert(0, stairs)

	#Generate monsters!
	for i in range (0, num_rooms):
		randy = random.randint(1, num_rooms - 1);
		randMonst = get_random_enemy();
		(centx, centy) = rooms[randy].center();
		randMonst.x = centx;
		randMonst.y = centy;
		entities.append(randMonst);



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


	libtcod.console_set_default_background(panel, libtcod.black)
	libtcod.console_clear(panel)

	global player
	render_bar(30, 1, BAR_WIDTH, 'HP', player.stats["health"], 100,
		libtcod.light_red, libtcod.darker_red)

	global events

	render_text(10, 3, "Inventory", player.inventory)
	render_text(5, 5, "Events", events)

	libtcod.console_blit(panel, 0, 0, SCREEN_WIDTH, PANEL_HEIGHT, 0, 0, PANEL_Y)

def render_bar(x, y, total_width, name, value, maximum, bar_color, back_color):
	bar_width = int(float(value) / maximum * total_width)

	libtcod.console_set_default_background(panel, back_color)
	libtcod.console_rect(panel, x, y, total_width, 1, False, libtcod.BKGND_SCREEN)

	libtcod.console_set_default_background(panel, bar_color)
	if bar_width > 0:
		libtcod.console_rect(panel, x, y, bar_width, 1, False, libtcod.BKGND_SCREEN)

	libtcod.console_set_default_foreground(panel, libtcod.white)
	libtcod.console_print_ex(panel, x + total_width / 2, y, libtcod.BKGND_NONE, libtcod.CENTER,
		name + ': ' + str(value) + '/' + str(maximum))

def render_text(x, y, name, list):
	libtcod.console_set_default_background(panel, libtcod.white)
	string = name + ": "
	for elem in list:
		string += elem + ", "
	libtcod.console_print_ex(panel, x, y, libtcod.BKGND_NONE, libtcod.CENTER, string)

enemy_types = ["Garden Gnome", "Skinny Dipper", "Doggo", "Lawnmower"]

SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
color_dark_wall = libtcod.Color(50, 100, 50)
color_dark_ground = libtcod.Color(100, 150, 100)

MAP_WIDTH = 80
MAP_HEIGHT = 43

ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 60

LIMIT_FPS = 20

libtcod.console_set_custom_font('dejavu16x16_gs_tc.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)

libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'All-American Lawnmower Task Force', False)
con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)
libtcod.sys_set_fps(LIMIT_FPS)

initialStats = {"health":100, "attack":10, "defense":0.0, "nourishment":100}

player = Entity(SCREEN_WIDTH/2, SCREEN_HEIGHT/2, '@', libtcod.red, con, "player", "Apple Johnnyseed", ["hands"], initialStats)
stairs = Entity(0, 0, '=', libtcod.blue, con, 'object', 'stairs', [], {})
entities = [stairs, player]

BAR_WIDTH = 20
PANEL_HEIGHT = 7
PANEL_Y = SCREEN_HEIGHT - PANEL_HEIGHT

panel = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT)

events = []

make_map()
while not libtcod.console_is_window_closed():
	render_all()
	for entity in entities:
		entity.clear()
	libtcod.console_flush()
	exit = handle_logic() # Update game logic
	if exit:
		break

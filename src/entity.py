import libtcodpy as libtcod

class Entity:
    def __init__(self, x, y, char, color, con):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.con = con

    def move(self, dx, dy, map):
        if not map[self.x + dx][self.y + dy].blocked:
            self.x += dx
            self.y += dy

    def draw(self):
        libtcod.console_set_default_foreground(self.con, self.color)
        libtcod.console_put_char(self.con, self.x, self.y, self.char, libtcod.BKGND_NONE)

    def clear(self):
        libtcod.console_put_char(self.con, self.x, self.y, ' ', libtcod.BKGND_NONE)

""" This file contains function and classes for the Artificial Intelligence used in the game.
"""

import math
from collections import defaultdict, deque

import pymunk
from pymunk import Vec2d
import gameobjects
import maps
import sounds

# NOTE: use only 'map0' during development!

MIN_ANGLE_DIF = math.radians(3)   # 3 degrees, a bit more than we can turn each tick


def angle_between_vectors(vec1, vec2):
    """ Since Vec2d operates in a cartesian coordinate space we have to
        convert the resulting vector to get the correct angle for our space.
    """
    vec = vec1 - vec2
    vec = vec.perpendicular()
    return vec.angle


def periodic_difference_of_angles(angle1, angle2):
    """ Compute the difference between two angles.
    """
    return (angle1 % (2 * math.pi)) - (angle2 % (2 * math.pi))


class Ai:
    """ A simple ai that finds the shortest path to the target using
    a breadth first search. Also capable of shooting other tanks and or wooden
    boxes. """

    def __init__(self, tank, game_objects_list, tanks_list, space, currentmap):
        self.tank = tank
        self.game_objects_list = game_objects_list
        self.tanks_list = tanks_list
        self.space = space
        self.currentmap = currentmap
        self.flag = None
        self.max_x = currentmap.width - 1
        self.max_y = currentmap.height - 1

        self.path = deque()
        self.move_cycle = self.move_cycle_gen()
        self.update_grid_pos()

        self.previous_distance = 0
        self.current_distance = 0

        self.allow_metal = False

    def update_grid_pos(self):
        """ This should only be called in the beginning, or at the end of a move_cycle. """
        self.grid_pos = self.get_tile_of_position(self.tank.body.position)

    def decide(self):
        """ Main decision function that gets called on every tick of the game.
        """
        if not self.tank.recent_shot:
            self.maybe_shoot()
        next(self.move_cycle)

    def maybe_shoot(self):
        """ Cast a ray in the direction the tank is facing. If another tank or a wooden box is found, shoot. """
        tank_angle = self.tank.body.angle + math.pi / 2
        # Start and end of the ray
        start_distance = 0.51
        end_distance = max(self.currentmap.width, self.currentmap.height)

        start_x = self.tank.body.position.x + start_distance * math.cos(tank_angle)
        start_y = self.tank.body.position.y + start_distance * math.sin(tank_angle)
        start = Vec2d(start_x, start_y)

        end_x = self.tank.body.position.x + end_distance * math.cos(tank_angle)
        end_y = self.tank.body.position.y + end_distance * math.sin(tank_angle)
        end = Vec2d(end_x, end_y)

        ray = self.space.segment_query_first(start, end, 0, pymunk.ShapeFilter())

        if ray and hasattr(ray, 'shape') and hasattr(ray.shape, 'parent'):
            # Check if the shape belongs to a tank or a wooden box
            obj = ray.shape.parent
            if isinstance(obj, gameobjects.Tank) or (isinstance(obj, gameobjects.Box) and obj.destructable):
                self.game_objects_list.append(self.tank.shoot(self.space))  # Shoot if it's a valid target
                sounds.shoot_sfx.play()

    def move_cycle_gen(self):
        """ A generator that iteratively goes through all the required steps
            to move to our goal.
        """
        while True:
            self.path = self.find_shortest_path()
            if not self.path:
                self.allow_metal = True
                self.path = self.find_shortest_path()  # allow metalboxes during search
                self.allow_metal = False
                yield
            if not self.path:
                yield
                continue
            next_coord = self.path.popleft()
            self.previous_distance = 100  # set previous to higher than possible current
            yield
            while not self.correct_angle(next_coord):
                self.turn(next_coord)
                yield
            self.tank.stop_turning()
            self.tank.accelerate()
            while not self.correct_pos(next_coord):
                yield
            self.tank.stop_moving()

            self.update_grid_pos()

    def turn(self, next_position):
        """Used to make ai turn itself into the right position"""
        next_position = self.center_vec2d(next_position)

        target_angle = angle_between_vectors(self.tank.body.position, next_position)
        angle_diff = periodic_difference_of_angles(target_angle, self.tank.body.angle)

        if abs(angle_diff) >= MIN_ANGLE_DIF:
            if angle_diff < -math.pi:
                self.tank.turn_right()
            elif 0 < angle_diff < math.pi:
                self.tank.turn_right()
            else:
                self.tank.turn_left()
        else:
            self.tank.stop_turning()

    def correct_angle(self, next_position):
        next_position = self.center_vec2d(next_position)
        """Check if the tank's angle is within MIN_ANGLE_DIF of the target angle."""
        target_angle = angle_between_vectors(self.tank.body.position, next_position)
        angle_diff = periodic_difference_of_angles(target_angle, self.tank.body.angle)

        return abs(angle_diff) <= MIN_ANGLE_DIF

    def correct_pos(self, next_tile):
        """
        Check if the tank has moved past the optimal position.
        If the current distance is greater than the previous distance,
        we are as close as possible to the target.
        """
        self.current_distance = self.tank.body.position.get_distance(self.center_vec2d(next_tile))
        # If the tank's distance to the target has increased, it's as close as it can get
        if self.current_distance > self.previous_distance:
            return True  # Stop moving
        else:
            self.previous_distance = self.current_distance
            return False  # Keep moving

    def center_vec2d(self, vec2d):
        """Finds the center of a tile"""
        x = (int(vec2d.x) + 0.5)
        y = (int(vec2d.y) + 0.5)
        return Vec2d(x, y)

    def find_shortest_path(self):
        """Finds the shortest path to flag/base using BFS"""
        self.path.clear()

        visited = set()
        flag_pos = self.get_target_tile()
        tank_pos = self.get_tile_of_position(self.tank.body.position)

        self.path.append((tank_pos, []))
        visited.add(tank_pos.int_tuple)

        while self.path:
            current, path = self.path.popleft()

            if current == flag_pos:
                return deque(path)

            for neighbor in self.get_tile_neighbors(current):
                if neighbor.int_tuple not in visited:
                    visited.add(neighbor.int_tuple)
                    self.path.append((neighbor, path + [neighbor]))

        return deque()

    def get_target_tile(self):
        """ Returns position of the flag if we don't have it. If we do have the flag,
            return the position of our home base.
        """
        if self.tank.flag is not None:
            x, y = self.tank.start_position
        else:
            self.get_flag()
            self.get_flag()  # Ensure that we have initialized it.
            x, y = self.flag.x, self.flag.y
        return Vec2d(int(x), int(y))

    def get_flag(self):
        """ This has to be called to get the flag, since we don't know
            where it is when the Ai object is initialized.
        """
        if self.flag is None:
            # Find the flag in the game objects list
            for obj in self.game_objects_list:
                if isinstance(obj, gameobjects.Flag):
                    self.flag = obj
                    break
        return self.flag

    def get_tile_of_position(self, position_vector):
        """ Converts and returns the float position of our tank to an integer position. """
        x, y = position_vector
        return Vec2d(int(x), int(y))

    def get_tile_neighbors(self, coord_vec):
        """ Returns all bordering grid squares of the input coordinate.
            A bordering square is only considered accessible i it is grass
            or a wooden box.
        """

        neighbors = [coord_vec + Vec2d(0, 1), coord_vec + Vec2d(1, 0),
                     coord_vec + Vec2d(-1, 0), coord_vec + Vec2d(0, -1)]

        return filter(self.filter_tile_neighbors, neighbors)

    def filter_tile_neighbors(self, coord):
        """ Used to filter the tile to check if it is a neighbor of the tank.
        """
        # If vector contains negative neighbor coords, then outside of map cant move there
        # Check for boxes on neighbors tiles, cant move there in that case
        if self.allow_metal:
            if coord.x in range(0, self.max_x + 1) and coord.y in range(0, self.max_y + 1) and (self.currentmap.boxAt(coord.x, coord.y)) != 1:
                return True
            else:
                return False
        else:
            if coord.x in range(0, self.max_x + 1) and coord.y in range(0, self.max_y + 1) and (self.currentmap.boxAt(coord.x, coord.y) == 0 or self.currentmap.boxAt(coord.x, coord.y) == 2):
                return True
            else:
                return False

    def reset_cycle(self):
        """Used to reset tanks cycle if it is killed or game is reset"""
        self.tank.stop_moving()
        self.tank.stop_turning()
        self.move_cycle.close()
        self.move_cycle = self.move_cycle_gen()

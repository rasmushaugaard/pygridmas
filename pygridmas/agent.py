from typing import List, Union
import math
import random

from pygridmas.vec2d import Vec2D
import pygridmas.colors as Colors
from pygridmas.world import World


class Agent:
    idx = None
    color = Colors.GREY50
    group_ids = set()
    group_collision_ids = set()
    world: World = None

    def __init__(self):
        # since set is a mutable data type, make sure that
        # each agent instance gets a new copy of the sets
        self.group_ids = set(self.group_ids)
        self.group_collision_ids = set(self.group_collision_ids)

    # handlers to be implemented in agents
    def initialize(self):
        pass

    def step(self):
        pass

    def receive_event(self, event_type, data):
        pass

    def cleanup(self):
        pass

    # util functions
    def pos(self) -> Vec2D:
        return self.world.agent_pos[self.idx]

    def move_to(self, pos) -> bool:
        return self.world.move_agent(self.idx, pos)

    def move_rel(self, rel_pos) -> bool:
        return self.world.move_agent_relative(self.idx, rel_pos)

    def move_in_dir(self, dir: Union[Vec2D, float]):
        if type(dir) == Vec2D:
            if dir.is_zero_vec():
                return self.move_rel(dir)
            dir = dir.angle()
        c, s = math.cos(dir), math.sin(dir)
        cabs, sabs = abs(c), abs(s)
        mi, ma = cabs, sabs
        c_is_max = cabs > sabs
        if c_is_max: mi, ma = ma, mi
        min_p = mi / ma if ma > 0 else 0
        move_min = random.random() < min_p
        dx, dy = -1 if c < 0 else 1, -1 if s < 0 else 1
        if not move_min:
            if c_is_max:
                dy = 0
            else:
                dx = 0
        return self.move_rel(Vec2D(dx, dy))

    def move_towards(self, pos: Vec2D):
        dir = self.vec_to(pos)
        return self.move_in_dir(dir)

    def move_away_from(self, pos: Vec2D):
        dir = self.world.shortest_way(pos, self.pos())
        if dir.is_zero_vec():
            return self.move_in_dir(Vec2D.random_grid_dir())
        else:
            return self.move_in_dir(dir)

    def box_scan(self, rng, group_id=None, sort=True):
        # type: (int, any, bool) -> List[Agent]
        agents = self.world.box_scan(self.pos(), rng=rng, group_id=group_id, sort=sort)
        if self in agents:
            agents.remove(self)
        return agents

    def emit_event(self, rng, event_type, data=None, group_id=None):
        agents = self.box_scan(rng, group_id, sort=False)
        self.world.emit_event(agents, event_type, data)

    def activate(self):
        self.world.active_agents[self.idx] = self

    def deactivate(self):
        self.world.active_agents.pop(self.idx, None)

    def vec_to(self, pos: Vec2D):
        return self.world.shortest_way(self.pos(), pos)

    def dist(self, pos: Vec2D):
        return self.vec_to(pos).magnitude()

    def inf_dist(self, pos: Vec2D):
        return self.vec_to(pos).inf_magnitude()

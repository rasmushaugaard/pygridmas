import itertools
from pygridmas.vec2d import Vec2D
import pygridmas.colors as Colors
import random
from typing import List


class World:
    def __init__(self, w, h, torus_enabled=False):
        self.w = w
        self.h = h
        self.m = [[[] for _ in range(w)] for _ in range(h)]
        self.torus_enabled = torus_enabled
        self.time = 0
        self.agents = {}
        self.active_agents = {}
        self.agent_pos = {}
        self.agent_counter = itertools.count()
        self.event_emit_queue = []

    def at(self, pos: Vec2D):
        return self.m[pos.y][pos.x]

    def random_pos(self):
        return Vec2D(random.randint(0, self.w - 1), random.randint(0, self.h - 1))

    def step(self):
        # call step on all active agents
        # the loop should allow the list to change hence the awkward loop
        for agent_id in list(self.active_agents.keys()):
            if agent_id in self.agents:
                self.agents[agent_id].step()
        # emit events after agent steps
        for agents, emit_pos, data in self.event_emit_queue:
            for agent in agents:
                if agent.idx in self.agents:
                    agent.receive_event(emit_pos, data)
        self.event_emit_queue.clear()
        self.time += 1

    def cleanup(self):
        for agent in self.agents.values():
            agent.cleanup()

    def add_agent(self, agent, pos: Vec2D = None):
        idx = agent.idx = next(self.agent_counter)
        if pos is None:
            pos = self.random_pos()
        if pos is not False:
            self.agent_pos[idx] = pos
        self.agents[idx] = agent
        self.active_agents[idx] = agent
        self.at(pos).append(agent)
        agent.world = self
        agent.initialize()

    def remove_agent(self, idx):
        agent = self.agents[idx]
        agent.cleanup()
        agent.world = None
        self.agents.pop(idx)
        self.active_agents.pop(idx, None)
        pos = self.agent_pos.pop(idx, None)
        if pos:
            self.at(pos).remove(agent)

    def move_agent(self, idx, pos):
        # Boundary check
        if not self.is_inside_world(pos):
            if self.torus_enabled:
                pos = self.torus(pos)
            else:
                return False

        # Collision check
        agent = self.agents[idx]
        if self.would_collide(pos, agent.group_collision_ids):
            return False

        # Do move
        old_pos = self.agent_pos[idx]
        self.at(old_pos).remove(agent)
        self.at(pos).append(agent)
        self.agent_pos[idx] = pos
        return True

    def move_agent_relative(self, idx, rel_pos):
        return self.move_agent(idx, self.agent_pos[idx] + rel_pos)

    def would_collide(self, pos: Vec2D, group_collision_ids):
        # TODO: possibly increase performance
        if len(group_collision_ids) == 0: return False
        for other_agent in self.at(pos):
            other_agent_group_ids = other_agent.group_ids
            for coll_id in group_collision_ids:
                if coll_id in other_agent_group_ids:
                    return True
        return False

    def torus(self, pos: Vec2D):
        return Vec2D(pos.x % self.w, pos.y % self.h)

    def is_inside_world(self, vec: Vec2D):
        return 0 < vec.x < self.w and 0 < vec.y < self.h

    def box_scan_no_torus(self, cx, cy, rng):
        agents, m = [], self.m
        xlo, xhi = max(cx - rng, 0), min(cx + rng, self.w - 1)
        ylo, yhi = max(cy - rng, 0), min(cy + rng, self.h - 1)
        for y in range(ylo, yhi + 1):
            for x in range(xlo, xhi + 1):
                agents += m[y][x]
        return agents

    def box_scan_torus(self, cx, cy, rng):
        agents, m = [], self.m
        xlo, xhi = cx - rng, cx + rng
        ylo, yhi = cy - rng, cy + rng
        x_ranges = [(xlo, xhi)]
        y_ranges = [(ylo, yhi)]
        if xlo < 0:
            x_ranges = [(xlo % self.w, self.w - 1), (0, xhi)]
        elif xhi >= self.w:
            x_ranges = [(xlo, self.w - 1), (0, xhi % self.w)]
        if ylo < 0:
            y_ranges = [(ylo % self.h, self.h - 1), (0, yhi)]
        elif yhi >= self.h:
            y_ranges = [(ylo, self.h - 1), (0, yhi % self.h)]
        for y_range in y_ranges:
            for x_range in x_ranges:
                for y in range(y_range[0], y_range[1] + 1):
                    for x in range(x_range[0], x_range[1] + 1):
                        agents += m[y][x]
        return agents

    def box_scan_sorted_no_torus(self, cx, cy, rng):
        agents, m = [], self.m
        agents += m[cy][cx]
        for d in range(1, rng + 1):
            xlo, xhi = cx - d, cx + d
            ylo, yhi = cy - d, cy + d
            _xlo, _xhi = max(0, xlo), min(self.w - 1, xhi)
            _ylo, _yhi = max(0, ylo), min(self.h - 1, yhi)
            if ylo >= 0:
                for x in range(_xlo, _xhi + 1):
                    agents += m[ylo][x]
            if yhi < self.h:
                for x in range(_xlo, _xhi + 1):
                    agents += m[yhi][x]
            if xlo >= 0:
                for y in range(_ylo + 1, _yhi):
                    agents += m[y][xlo]
            if xhi < self.w:
                for y in range(_ylo + 1, _yhi):
                    agents += m[y][xhi]
        return agents

    def box_scan_sorted_torus(self, cx, cy, rng):
        size = rng * 2 + 1
        assert (size <= self.w and size <= self.h)
        agents, m = [], self.m
        agents += m[cy][cx]
        for d in range(1, rng + 1):
            xlo, xhi = cx - d, cx + d
            ylo, yhi = cy - d, cy + d
            _xlo, _xhi = xlo % self.w, xhi % self.w
            _ylo, _yhi = ylo % self.h, yhi % self.h

            xrange = range(xlo, xhi + 1)
            if xlo != _xlo:
                xrange = itertools.chain(range(_xlo, self.w), range(xhi + 1))
            elif xhi != _xhi:
                xrange = itertools.chain(range(xlo, self.w), range(_xhi + 1))
            for x in xrange:
                agents += m[_ylo][x] + m[_yhi][x]

            yrange = range(ylo + 1, yhi)
            if ylo != _ylo:
                yrange = itertools.chain(range(_ylo + 1, self.h), range(yhi))
            elif yhi != _yhi:
                yrange = itertools.chain(range(ylo + 1, self.h), range(_yhi))
            for y in yrange:
                agents += m[y][_xlo] + m[y][_xhi]
        return agents

    @staticmethod
    def filter_agents_by_group_id(agents, group_id=None):
        if group_id is None:
            return agents
        return [agent for agent in agents if group_id in agent.group_ids]

    def box_scan(self, center_pos: Vec2D, rng, sort=True, group_id=None):
        if sort:
            if self.torus_enabled:
                f = self.box_scan_sorted_torus
            else:
                f = self.box_scan_sorted_no_torus
        else:
            if self.torus_enabled:
                f = self.box_scan_torus
            else:
                f = self.box_scan_no_torus
        agents = f(center_pos.x, center_pos.y, rng)
        return self.filter_agents_by_group_id(agents, group_id)

    def shortest_way(self, a: Vec2D, b: Vec2D):
        """shortest vector from a to b"""
        dx, dy = b.x - a.x, b.y - a.y
        if self.torus_enabled:
            if abs(dx) > self.w * 0.5:
                dx = dx - self.w if dx > 0 else dx + self.w
            if abs(dy) > self.h * 0.5:
                dy = dy - self.h if dy > 0 else dy + self.h
        return Vec2D(dx, dy)

    def emit_event(self, agents, emit_pos, data):
        self.event_emit_queue.append((agents, emit_pos, data))


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

    def receive_event(self, emitter_pos: Vec2D, data):
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

    def move_in_dir(self, dir: Vec2D):
        sign = dir.clamp_rng(1)
        xabs, yabs = abs(dir.x), abs(dir.y)
        mi, ma = xabs, yabs
        x_is_max = xabs > yabs
        if x_is_max: mi, ma = ma, mi
        min_p = mi / ma if ma > 0 else 0
        move_min = random.random() < min_p
        if not move_min:
            if x_is_max:
                sign.y = 0
            else:
                sign.x = 0
        return self.move_rel(sign)

    def move_towards(self, pos: Vec2D):
        dir = self.world.shortest_way(self.pos(), pos)
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

    def emit_event(self, rng, data, group_id=None):
        agents = self.box_scan(rng, group_id, sort=False)
        self.world.emit_event(agents, self.pos(), data)

    def activate(self):
        self.world.active_agents[self.idx] = self

    def deactivate(self):
        self.world.active_agents.pop(self.idx, None)

    def vec_to(self, pos: Vec2D):
        return self.world.shortest_way(pos, self.pos())

    def dist(self, pos: Vec2D):
        return self.vec_to(pos).magnitude()

    def inf_dist(self, pos: Vec2D):
        return self.vec_to(pos).inf_magnitude()

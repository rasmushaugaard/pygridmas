from pygridmas import World, Agent, Vec2D, Colors, Visualizer

size = 100
world = World(w=size, h=size, torus_enabled=True)


class Wall(Agent):
    color = Colors.WHITE
    start_active = False
    group_ids = (0,)


x1, x2 = round(size * 0.3), round(size * 0.7)
y1, y2 = round(size * 0.6), round(size * 0.8)

for x in (x1, x2):
    for y in range(y1 + 1):
        world.add_agent(Wall(), Vec2D(x, y))
    for y in range(y2, size):
        world.add_agent(Wall(), Vec2D(x, y))

for y in (y1, y2):
    for x in range(x1 + 1, x2):
        world.add_agent(Wall(), Vec2D(x, y))


class Mover(Agent):
    color = Colors.BLUE
    group_collision_ids = (0,)

    def step(self):
        self.move_rel(Vec2D.random_grid_dir())


for i in range(100):
    world.add_agent(Mover(), Vec2D(size // 2, size // 2))

vis = Visualizer(world, scale=3, target_speed=100)
vis.start()

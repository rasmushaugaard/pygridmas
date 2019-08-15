from pygridmas import World, Agent, Vec2D, Colors, Visualizer

size = 100
world = World(w=size, h=size, torus_enabled=True)


class Wall(Agent):
    color = Colors.WHITE
    group_ids = {0}  # A python set


class Mover(Agent):
    color = Colors.BLUE
    group_ids = {1}
    group_collision_ids = {0, 1}  # Not able to enter wall tiles or other Mover tiles

    def step(self):
        self.move_rel(Vec2D.random_grid_dir())


# Create walls
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

# Add Mover agents
for _ in range(200):
    world.add_agent(Mover(), Vec2D(size // 2, size // 4))

# Start and visualize simulation
vis = Visualizer(world, scale=3, target_speed=200)
vis.start()

from pygridmas import World, Agent, Vec2D, Colors, Visualizer
import random
import math

size = 200
world = World(w=size, h=size, torus_enabled=True)


class Repulser(Agent):
    color = Colors.YELLOW
    start_target: Vec2D = None
    reached_target = False

    def initialize(self):
        # Create a target a bit off center to view the torus effect
        # self.world is set on the agent when added to a world,
        # so the world can be accessed within the agent methods
        self.start_target = Vec2D(
            math.floor(self.world.w * 0.25),
            math.floor(self.world.h * 0.25)
        )

    def step(self):
        if not self.reached_target:
            self.move_towards(self.start_target)
            self.reached_target = self.pos() == self.start_target
        else:
            near_agents = self.box_scan(10)
            if len(near_agents) > 0:
                self.color = Colors.RED
                if random.random() < 0.2:
                    self.move_rel(Vec2D.random_grid_dir())
                else:
                    other_agent = random.choice(near_agents)
                    self.move_away_from(other_agent.pos())
            else:
                self.color = Colors.BLUE


# Add a number of Repulsers to the world
for i in range(size ** 2 // 155):
    world.add_agent(Repulser())

# Visualize the world. The visualizer will call world.step(),
# trying to maintain a certain target speed (steps per second)
vis = Visualizer(world, scale=2, target_speed=40)
vis.start()

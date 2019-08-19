# pygridmas
A python Multi Agent System grid world simulator for the MAS course on SDU
### install

```
$ git clone https://github.com/RasmusHaugaard/pygridmas.git
```
```
$ cd pygridmas
```
```
$ pip3 install -e .
```

### examples
See pygridmas/examples for examples

### usage
```python
from pygridmas import World, Agent, Vec2D, Visualizer

# create world, torus or not
world = World(w=100, h=100, torus_enabled=True)


# extend the base Agent class
class MyAgent(Agent):

    def initialize(self):
        # Called once when the agent enters a world.
        # After the agent is added to the world, a reference to the
        # world is stored in 'self.world'.
        pass

    def step(self):
        # Called in 'world.step()' (at every step of the simulation).
        pass

    def receive_event(self, event_type, data):
        # Handle events emitted from other agents.
        pass

    def cleanup(self):
        # Called when removed from the world,
        # or when the world ends: world.end()
        pass


# Add the agent to the world.
# If no position is provided, a random position on the map is chosen.
world.add_agent(MyAgent(), pos=Vec2D(x=20, y=20))

# The world proceeds by calling 'world.step()'
world.step()

# Often, it's nice to visualize the world.
# The visualizer calls 'world.step()' and tries to maintain
# a certain speed (world steps per second).
vis = Visualizer(world, target_speed=100)
vis.start()
```

### visualization hot keys
* `space` pause/resume simulation
* `escape` calls 'world.end()' and terminates the simulation
* `right arrow` step through simulation
* `up arrow` increase simulation target speed
* `down arrow` decrease simulation target speed
* `R` enable/disable rendering (often allows sim to run much faster)
* `P` enable/disable performance rendering (a bit faster)
* `L` enable/disable labels

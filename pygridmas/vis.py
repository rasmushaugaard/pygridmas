import pyglet
from pyglet.window import key
import time
import itertools
import math


class VisualizerBase(pyglet.window.Window):
    def __init__(self, world, scale=3):
        super(VisualizerBase, self).__init__()
        self.scale = scale
        self.width, self.height = world.w * scale, world.h * scale
        self.world = world
        self.labels = []
        # force draw first draw
        self.force_draw()

    def start(self):
        pyglet.app.run()

    def force_draw(self):
        self.switch_to()
        self.dispatch_event("on_draw")
        self.dispatch_events()
        self.flip()

    def on_draw(self):
        self.clear()
        positions = []
        colors = []
        for y, row in enumerate(self.world.m):
            yy = y * self.scale
            for x, agents in enumerate(row):
                xx = x * self.scale
                n = math.ceil(math.sqrt(len(agents)))
                if n == 0: continue
                d = self.scale / n
                for i, agent in enumerate(agents):
                    row = i // n
                    col = i - row * n
                    xlo, ylo = xx + d * col, yy + d * row
                    xhi, yhi = xlo + d, ylo + d
                    positions += [xlo, ylo, xhi, ylo, xhi, yhi, xlo, yhi]
                    colors += list(agent.color) * 4
        pyglet.graphics.draw(
            len(positions) // 2,
            pyglet.gl.GL_QUADS,
            ('v2f', positions),
            ('c3f', colors)
        )
        for label in self.labels:
            label.draw()


class Visualizer(VisualizerBase):
    def __init__(self, world, scale=3, start_paused=False, target_speed=10, target_fps=60, show_label=True):
        super(Visualizer, self).__init__(world, scale)
        self.pause = start_paused
        self.target_speed = target_speed
        self.target_fps = target_fps
        self.target_dt_frame = 1 / target_fps
        self.last_step = 0
        self.last_update = None
        self.speed = target_speed
        self.dt_frame = self.target_dt_frame
        pyglet.clock.schedule_interval(self.update, self.target_dt_frame)

        self.last_label_update = 0
        self.speed_label = pyglet.text.Label(
            '',
            font_size=10,
            x=2, y=1,
            anchor_x='left', anchor_y='bottom'
        )
        if show_label:
            self.labels.append(self.speed_label)

    def get_target_dt_step(self):
        return 1 / self.target_speed

    def update(self, dt):
        i = 0
        if not self.pause and self.get_target_dt_step() < time.time() - self.last_step:
            self.last_step = time.time()
            start_time = time.time()
            for i in itertools.count(1):
                self.world.step()
                if i >= self.target_speed / self.target_fps:
                    break
                if time.time() - start_time > self.target_dt_frame:
                    break

        t = time.time()
        if self.last_update is not None:
            dt = time.time() - self.last_update
        self.last_update = t

        self.dt_frame = self.dt_frame * 0.9 + 0.1 * dt
        self.speed = self.speed * 0.9 + 0.1 * i / self.dt_frame

        if t - self.last_label_update > 0.5:
            self.speed_label.text = 'speed: {:5.2f}, target: {:.2f}'.format(self.speed, self.target_speed)
            self.last_label_update = t

        if self.pause:
            self.speed_label.text = 'paused'
            self.last_label_update = 0

    def on_key_press(self, symbol, _):
        if symbol == key.SPACE:
            self.pause = not self.pause
            self.last_step = 0
        if symbol == key.RIGHT:
            self.pause = True
            self.world.step()
        if symbol == key.UP:
            self.pause = False
            self.target_speed *= 2.0
        if symbol == key.DOWN:
            self.pause = False
            self.target_speed *= 0.5

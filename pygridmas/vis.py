import pyglet
from pyglet.window import key
import time
import itertools
import math
from pygridmas import World


class VisualizerBase(pyglet.window.Window):
    def __init__(self, world, scale=3, performance=True, render_labels=True):
        super(VisualizerBase, self).__init__()
        self.scale = scale
        self.width, self.height = world.w * scale, world.h * scale
        self.world: World = world
        self.labels = []
        self.render_labels = render_labels
        self.do_render = True
        self.performance = performance
        self.no_render_label = pyglet.text.Label(
            'no render',
            font_size=10,
            x=self.world.w * 0.5 * self.scale, y=self.world.h * 0.5 * self.scale,
            anchor_x="center", anchor_y="center"
        )
        self.time_label = pyglet.text.Label(
            'time: 0', font_size=10, x=2, y=14,
            anchor_x='left', anchor_y='bottom'
        )
        self.labels.append(self.time_label)
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
        if self.do_render:
            s = self.scale
            if self.performance:
                for yy, row in enumerate(self.world.m):
                    yy *= s
                    for xx, agents in enumerate(row):
                        xx *= s
                        if agents:
                            positions += [xx, yy, xx + s, yy, xx + s, yy + s, xx, yy + s]
                            colors += list(agents[-1].color) * 4
            else:
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
        self.time_label.text = 'time: {}'.format(self.world.time)
        if self.render_labels:
            for label in self.labels:
                label.draw()
        if not self.do_render:
            self.no_render_label.draw()
        if self.world.ended:
            pyglet.app.exit()


class Visualizer(VisualizerBase):
    def __init__(self, world, scale=3, start_paused=False, target_speed=40, target_fps=30, render_labels=True,
                 performance=True):
        super(Visualizer, self).__init__(world, scale, performance, render_labels)
        self.pause = start_paused
        self.target_speed = target_speed
        self.target_fps = target_fps
        self.target_dt_frame = 1 / target_fps
        self.last_step = 0
        self.last_update = None
        self.last_update_end = time.time()
        self.speed = target_speed
        self.dt_frame = self.target_dt_frame
        pyglet.clock.schedule_interval(self.update, self.target_dt_frame)

        self.last_label_update = 0
        self.speed_label = pyglet.text.Label(
            '', font_size=10, x=2, y=1,
            anchor_x='left', anchor_y='bottom'
        )
        self.performance_label = pyglet.text.Label(
            '', font_size=10, x=2, y=28,
            anchor_x='left', anchor_y='bottom'
        )
        self.labels += [self.speed_label, self.performance_label]

    def get_target_dt_step(self):
        return 1 / self.target_speed

    def update(self, dt):
        t = time.time()
        i = 0
        if not self.pause and t - self.last_step > self.get_target_dt_step():
            self.last_step = t
            for i in itertools.count(1):
                self.world.step()
                if i >= self.target_speed / self.target_fps:
                    break
                if time.time() - t > self.target_dt_frame:
                    break

        self.dt_frame = self.dt_frame * 0.9 + 0.1 * dt
        self.speed = self.speed * 0.9 + 0.1 * i / self.dt_frame

        if t - self.last_label_update > 0.5:
            self.speed_label.text = 'speed: {:5.2f}, target: {:.2f}'.format(self.speed, self.target_speed)
            self.last_label_update = t

        if self.pause:
            self.speed_label.text = 'paused'
            self.last_label_update = 0
        self.no_render_label.text = '' if self.do_render else 'no render'
        self.performance_label.text = 'P' if self.performance else ''

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
        if symbol == key.R:
            self.do_render = not self.do_render
        if symbol == key.P:
            self.performance = not self.performance
        if symbol == key.L:
            self.render_labels = not self.render_labels
        if symbol == key.ESCAPE:
            self.world.end()

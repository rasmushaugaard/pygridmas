import math
import random


def clamp(val, mi, ma):
    if mi > val:
        val = mi
    elif ma < val:
        val = ma
    return val


class Vec2D:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __neg__(self):
        return Vec2D(-self.x, -self.y)

    def __sub__(self, other):
        return Vec2D(self.x - other.x, self.y - other.y)

    def __add__(self, other):
        return Vec2D(self.x + other.x, self.y + other.y)

    def __mul__(self, scalar):
        return Vec2D(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar):
        return Vec2D(self.x / scalar, self.y / scalar)

    def __floordiv__(self, i):
        return Vec2D(self.x // i, self.y // i)

    def __eq__(self, other):
        return type(other) == Vec2D and self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.x, self.y))

    def inf_magnitude(self):
        return max(abs(self.x), abs(self.y))

    def magnitude(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def magnitude_sqr(self):
        return self.x ** 2 + self.y ** 2

    def angle(self):
        return math.atan2(self.y, self.x)

    def clamp_rng(self, rng):
        return Vec2D(clamp(self.x, -rng, rng), clamp(self.y, -rng, rng))

    def is_zero_vec(self):
        return self.x == self.y == 0

    def round(self):
        return Vec2D(round(self.x), round(self.y))

    def normalize(self):
        return self / self.magnitude()

    @staticmethod
    def random_grid_dir():
        return Vec2D(random.randint(-1, 1), random.randint(-1, 1))

    @staticmethod
    def random_dir():
        angle = random.random() * math.pi * 2
        return Vec2D(math.cos(angle), math.sin(angle))

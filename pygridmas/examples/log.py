from pygridmas import Agent, World
import matplotlib.pyplot as plt
import random
import numpy as np


class AgentCountLogger:
    count = 0

    def bind(logger, agent_class):
        class CountLoggingAgentClass(agent_class):
            def initialize(self):
                super().initialize()
                logger.count += 1

            def cleanup(self):
                super().cleanup()
                logger.count -= 1

        return CountLoggingAgentClass


class RandomlyDyingAgent(Agent):
    def step(self):
        if random.random() < 0.01:
            self.world.remove_agent(self.idx)


def draw_sample(T):
    count_logger = AgentCountLogger()
    RandomlyDyingAgentLog = count_logger.bind(RandomlyDyingAgent)

    world = World(100, 100, max_steps=T)
    for _ in range(100):
        world.add_agent(RandomlyDyingAgentLog())

    agent_counts = []
    while not world.ended:
        agent_counts.append(count_logger.count)
        world.step()

    return agent_counts


def main():
    T = 500
    n = 100
    data = np.empty((n, T))
    for i in range(n):
        data[i] = draw_sample(T)
    mean = data.mean(axis=0)
    std = data.std(axis=0)

    t = list(range(T))
    plt.plot(t, mean, 'k', label='mean')
    plt.fill_between(t, mean - std, mean + std, label='+- 1 std')
    plt.xlabel('time')
    plt.ylabel('number of agents')
    plt.legend()
    plt.show()


if __name__ == '__main__':
    main()

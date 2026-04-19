"""
数据生成模块（Generator）
职责：在 simpy 环境中按照到达分布持续生成学生到达事件，并通过回调把事件交给引擎。
"""
import random
from typing import Callable


def run_gen(env, arrival_rate: float, spawn_callback: Callable[[str], None]):
    """
    在给定的 simpy 环境中按照指数到达（泊松过程）生成学生。

    :param env: simpy.Environment
    :param arrival_rate: 平均到达率（每分钟）
    :param spawn_callback: 每产生一个学生时的回调，接收学生名称，回调应在环境中启动学生进程
    """
    cnt = 0
    while True:
        # 指数分布间隔，lambda = arrival_rate
        interval = random.expovariate(arrival_rate) if arrival_rate > 0 else float("inf")
        yield env.timeout(interval)
        cnt += 1
        name = f"S{cnt}"
        # 回调负责在 env 中创建学生进程，例如: env.process(...)
        spawn_callback(name)


if __name__ == "__main__":
    # 简单演示无法单独运行，因为需要 simpy 环境和回调
    print("Generator module: use from Engine to drive it")

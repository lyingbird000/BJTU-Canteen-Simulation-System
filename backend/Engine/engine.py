"""
增强的仿真核心引擎（Engine）
功能：
 - 支持顾客耐心（超时离开/流失）
 - 支持动态开/关窗口（按平均队长阈值）
 - 收集基础统计（服务/流失/平均等待/窗口历史）
"""
from typing import Dict, List, Callable, Optional
import simpy
import random
from backend.Generator import generator as gen


class EngineSim:
    def __init__(
        self,
        min_windows: int = 1,
        max_windows: int = 10,
        arrival_rate: float = 2.0,
        open_threshold: float = 3.0,
        close_threshold: float = 0.5,
        check_interval: float = 1.0,
        patience_range: tuple = (2.0, 6.0),
    ):
        self.min_windows = max(1, int(min_windows))
        self.max_windows = max(self.min_windows, int(max_windows))
        self.arrival_rate = float(arrival_rate)
        self.open_threshold = float(open_threshold)
        self.close_threshold = float(close_threshold)
        self.check_interval = float(check_interval)
        self.patience_range = tuple(patience_range)

        self.env = simpy.Environment()

        # 每个窗口用一个 capacity=1 的 Resource 封装为 dict，便于扩展统计
        self.windows: List[Dict] = []
        for i in range(self.min_windows):
            self._add_window()

        # 统计
        self.served: List[Dict] = []
        self.abandoned: List[Dict] = []
        self.window_history: List[Dict] = []  # time、open_windows

    def _add_window(self):
        wid = len(self.windows) + 1
        res = simpy.Resource(self.env, capacity=1)
        self.windows.append({
            "id": wid,
            "resource": res,
            "total_busy": 0.0,
        })

    def _remove_window(self) -> bool:
        # 仅移除空闲窗口（没有队列且未被占用）
        for i in range(len(self.windows) - 1, -1, -1):
            w = self.windows[i]
            if len(w["resource"].queue) == 0 and getattr(w["resource"], "count", 0) == 0:
                self.windows.pop(i)
                return True
        return False

    def _pick_window_index(self) -> int:
        # 选择当前队列最短的窗口索引
        best_idx = 0
        best_load = float('inf')
        for i, w in enumerate(self.windows):
            load = len(w["resource"].queue) + getattr(w["resource"], "count", 0)
            if load < best_load:
                best_load = load
                best_idx = i
        return best_idx

    def student_process(self, name: str):
        arrival = self.env.now
        # 随机耐心（秒/分钟一致单位）
        pmin, pmax = self.patience_range
        patience = random.uniform(pmin, pmax)

        # 选择窗口并发出请求
        idx = self._pick_window_index()
        w = self.windows[idx]
        req = w["resource"].request()
        # 同时等待请求或者超时（耐心耗尽）
        result = yield req | self.env.timeout(patience)
        if req not in result:
            # 流失
            self.abandoned.append({"name": name, "arrival": arrival, "left_at": self.env.now, "patience": patience})
            return

        # 获得服务
        start_service = self.env.now
        wait_time = start_service - arrival
        service_duration = random.uniform(1.0, 3.0)
        yield self.env.timeout(service_duration)

        # 完成服务，释放资源会自动发生
        # 更新窗口繁忙时间
        w["total_busy"] += service_duration
        self.served.append({
            "name": name,
            "arrival": arrival,
            "start_service": start_service,
            "wait_time": wait_time,
            "service_time": service_duration,
            "window_id": w["id"],
        })

    def _generator_process(self):
        # 启动 generator，spawn_callback 在本对象中把名字转为 env.process
        def spawn(name: str):
            self.env.process(self.student_process(name))

        yield from gen.run_gen(self.env, self.arrival_rate, spawn)

    def _manager_process(self):
        # 周期性检查队长，决定开/关窗口
        while True:
            yield self.env.timeout(self.check_interval)
            if len(self.windows) == 0:
                continue
            total_queue = sum(len(w["resource"].queue) for w in self.windows)
            open_windows = len(self.windows)
            avg_q = total_queue / open_windows if open_windows > 0 else 0.0

            # 记录历史
            self.window_history.append({"time": self.env.now, "open_windows": open_windows, "total_queue": total_queue})

            if avg_q > self.open_threshold and open_windows < self.max_windows:
                self._add_window()
                self.window_history.append({"time": self.env.now, "action": "open", "open_windows": len(self.windows)})

            if avg_q < self.close_threshold and open_windows > self.min_windows:
                removed = self._remove_window()
                if removed:
                    self.window_history.append({"time": self.env.now, "action": "close", "open_windows": len(self.windows)})

    def run(self, until: float = 20.0) -> Dict:
        # 启动产生器与管理器
        self.env.process(self._generator_process())
        self.env.process(self._manager_process())
        # 运行仿真
        self.env.run(until=until)
        return self.metrics()

    def metrics(self) -> Dict:
        total_served = len(self.served)
        total_abandoned = len(self.abandoned)
        avg_wait = 0.0
        if total_served > 0:
            avg_wait = sum(s["wait_time"] for s in self.served) / total_served
        utilization = [
            {"window_id": w["id"], "total_busy": w["total_busy"]} for w in self.windows
        ]
        return {
            "total_served": total_served,
            "total_abandoned": total_abandoned,
            "avg_wait": avg_wait,
            "open_windows": len(self.windows),
            "utilization": utilization,
            "window_history": self.window_history,
        }


if __name__ == "__main__":
    sim = EngineSim(min_windows=2, max_windows=6, arrival_rate=2.5)
    res = sim.run(until=30)
    print(res)

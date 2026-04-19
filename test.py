from backend.Engine import EngineSim


if __name__ == "__main__":
    print("=== 北交大学活一楼仿真 (快速本地运行) ===")
    sim = EngineSim(num_windows=3, arrival_rate=2.0)
    res = sim.run(until=20)
    print("\n=== 仿真结束，统计结果 ===")
    print(res)
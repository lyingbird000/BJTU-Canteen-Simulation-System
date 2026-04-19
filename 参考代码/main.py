from fastapi import FastAPI
from pydantic import BaseModel
from backend.Engine import EngineSim

app = FastAPI(title="Canteen Simulation API")


class StartRequest(BaseModel):
	num_windows: int = 3
	arrival_rate: float = 2.0
	duration: float = 20.0


@app.post("/api/sim/start")
def start_sim(req: StartRequest):
	"""同步运行一次仿真（开发/调试用）。

	注意：生产环境建议改为后台任务或 WebSocket 推送结果。
	"""
	sim = EngineSim(num_windows=req.num_windows, arrival_rate=req.arrival_rate)
	result = sim.run(until=req.duration)
	return result


@app.get("/api/health")
def health():
	return {"status": "ok"}


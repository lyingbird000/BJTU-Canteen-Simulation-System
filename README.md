# 北交大 食堂排队仿真 (骨架实现)

这是一个根据规格草案搭建的最小可运行代码骨架，包含：

- `backend/Generator`：到达事件生成器
- `backend/Engine`：仿真引擎（基于 `simpy`）
- `backend/main.py`：FastAPI 后端骨架（提供同步启动仿真接口，用于开发/调试）
- `test.py`：快速本地运行示例

快速上手：

1. 创建并激活虚拟环境（你已经有 `.venv`）
2. 安装依赖：
```bash
pip install -r requirements.txt
```
3. 本地运行示例：
```bash
python test.py
```
4. 运行 API（开发）：
```bash
uvicorn backend.main:app --reload
```

后续工作：把同步仿真改为后台任务并通过 WebSocket 推送实时事件到前端，补充数据库持久化与前端交互。

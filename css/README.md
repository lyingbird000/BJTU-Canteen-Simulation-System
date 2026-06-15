# 北京交通大学智慧食堂实时监测系统 - 源代码说明文档

## 项目概述
这是一个基于Python Flask + SQLite + HTML/CSS/JS的智慧食堂实时监测系统，用于实时监控食堂窗口排队情况、餐桌占用状态以及提供统计数据。

## 项目架构
- **后端**: Python Flask + SQLite数据库
- **前端**: HTML + Tailwind CSS + JavaScript
- **部署**: Docker容器化部署

## 文件结构说明

### 1. server.py - 后端服务主程序
- **功能**: Flask Web服务器，提供RESTful API接口
- **主要模块**:
  - `/api/windows` - 获取窗口实时排队数据
  - `/api/tables` - 获取餐桌占用数据
  - `/api/statistics` - 获取食堂统计数据
  - `/api/menu` - 获取今日菜单信息
  - 随机生成模拟数据用于演示
- **技术特点**: 使用CORS跨域支持，SQLite数据库操作

### 2. init_database.py - 数据库初始化脚本
- **功能**: 创建SQLite数据库及表结构
- **包含表**:
  - `windows` - 窗口信息表（ID、名称、类别、排队数、等待时间、状态）
  - `tables` - 餐桌信息表（ID、占用状态、容量、当前人数）
  - `menu` - 菜单信息表（ID、菜名、价格、评分、销量）
  - `statistics` - 统计信息表（总桌数、占用桌数、总人数等）
- **初始化数据**: 插入默认窗口、餐桌、菜单数据

### 3. index.html - 前端页面
- **功能**: 用户界面，展示实时食堂状态
- **页面元素**:
  - 统计卡片区：总人数、用餐桌数、空闲桌数、平均等待时间
  - 窗口展示区：8个窗口的排队情况可视化
  - 餐桌布局图：8x10网格展示80张餐桌实时状态
- **交互特性**: 每3秒自动更新数据，动画效果展示排队人员

### 4. requirements.txt - 依赖包列表
- Flask==2.3.3
- flask-cors==4.0.0

### 5. Dockerfile - 容器构建配置
- 使用Python 3.9-slim基础镜像
- 安装依赖并复制代码
- 暴露3000端口运行服务

### 6. docker-compose.yml - 容器编排配置
- 定义canteen-monitor服务
- 端口映射3000:3000
- 自动重启策略

### 7. my.css - 样式文件
- 简单的颜色样式定义（粉色文字）

### 8. canteen.db - SQLite数据库文件
- 存储系统运行时的数据

## 系统设计思路

### 数据流设计
1. **数据初始化**: 通过init_database.py创建数据库表结构和初始数据
2. **数据处理**: server.py接收API请求，从数据库读取数据并实时更新
3. **数据展示**: index.html通过AJAX定期调用API获取最新数据并更新UI
4. **模拟数据**: server.py随机生成排队人数、餐桌占用等模拟数据

### 功能实现
- **窗口排队监控**: 实时显示各窗口排队人数和预估等待时间
- **餐桌占用热力图**: 可视化展示餐桌占用情况
- **数据统计**: 提供食堂运营关键指标统计
- **响应式UI**: 使用Tailwind CSS实现美观的用户界面

### 技术亮点
- 前后端分离架构，便于维护和扩展
- 模拟真实场景的随机数据生成算法
- 实时数据更新机制，提供流畅用户体验
- 容器化部署方案，便于环境部署和迁移

## 运行方式
1. 执行`pip install -r requirements.txt`安装依赖包
2. 执行`python init_database.py`初始化数据库
3. 执行`python server.py`启动后端服务
4. 访问`http://localhost:8888`查看前端界面
5. 或使用Docker Compose快速部署：
`docker-compose down`
`docker-compose build`
`docker-compose up`

## 扩展建议
- 集成真实的传感器数据源
- 添加用户预订功能
- 增加历史数据分析模块
- 实现管理员后台管理系统
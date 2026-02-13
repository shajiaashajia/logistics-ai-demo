# logistics-ai-demo

一个可运行的 **物流 AI 调度系统**（演示版），包含：

- 调度算法：优先级、距离、时效、载重利用率综合打分
- HTTP API：`/api/schedule` + `/api/health`
- Web 前端：输入订单/车辆 JSON、展示 KPI 与分配明细
- 单元测试：调度逻辑与 API 行为验证

## 快速开始

```bash
python3 server.py
```

打开：<http://localhost:8000>

## API 示例

```bash
curl -X POST http://localhost:8000/api/schedule \
  -H 'Content-Type: application/json' \
  -d '{
    "orders": [
      {"id":"O-1","pickup":[31.23,121.47],"dropoff":[31.30,121.55],"weight":120,"priority":5,"deadline_hour":3}
    ],
    "vehicles": [
      {"id":"V-1","location":[31.21,121.46],"capacity":300,"speed_kmph":45,"available_from_hour":0}
    ]
  }'
```

### 返回字段（核心）

- `assignments[]`: 每条订单的车辆分配结果，包含 ETA、里程、得分、是否超时
- `unassigned_orders[]`: 无法分配的订单 ID 列表
- `total_score`: 调度总得分
- `summary`: 总订单、已分配、未分配统计

## 测试

```bash
python3 -m unittest discover -s tests -v
```

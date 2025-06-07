# 股票分析筛选系统

基于 FastAPI 和 AKShare 的股票分析筛选系统，提供股票数据查询、筛选和可视化功能。

## 功能特点

- 股票数据获取和存储
- 财务指标筛选
- 数据可视化
- RESTful API 接口

## 技术栈

- 后端：FastAPI + PostgreSQL + Redis
- 数据源：AKShare
- 部署：Docker + Docker Compose

## 系统模块设计
### 1. 数据采集模块
* 定时任务：使用 APScheduler 定期从 AKShare 获取数据
* 数据清洗：处理异常值、缺失值
* 数据存储：将处理后的数据存入 PostgreSQL
### 2. API 服务模块
* 股票数据查询接口
* 筛选条件处理接口
* 数据可视化接口
* 用户管理接口（如果需要）
### 3. 数据处理模块
* 财务指标计算
* 数据聚合
* 数据转换（用于前端展示）
### 4.缓存管理模块
* 热点数据缓存
* 查询结果缓存
* 用户会话管理

## 开发环境设置

1. 克隆项目
```bash
git clone [项目地址]
cd stock-analyse
```

2. 启动开发环境
```bash
docker-compose up
```

3. 访问 API 文档
```
http://localhost:8000/docs
```

## 项目结构

```
stock-analyse/
├── backend/
│   ├── app/
│   │   ├── api/        # API 路由
│   │   ├── core/       # 核心配置
│   │   ├── db/         # 数据库
│   │   ├── models/     # 数据模型
│   │   ├── schemas/    # Pydantic 模型
│   │   ├── services/   # 业务逻辑
│   │   └── utils/      # 工具函数
│   ├── tests/          # 测试文件
│   ├── Dockerfile.dev  # 开发环境 Dockerfile
│   └── requirements.txt # Python 依赖
└── docker-compose.yml  # Docker 编排配置
```

## API 文档

启动服务后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 开发指南

1. 代码风格
- 使用 black 进行代码格式化
- 使用 flake8 进行代码检查

2. 测试
- 使用 pytest 运行测试
- 测试覆盖率报告

## 部署

1. 构建生产镜像
```bash
docker build -t stock-analyse:prod .
```

2. 运行生产环境
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 许可证

MIT 
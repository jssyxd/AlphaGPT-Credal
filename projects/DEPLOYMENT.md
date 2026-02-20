# AlphaGPT 部署指南

## 📋 目录
1. [前置条件](#前置条件)
2. [Supabase 数据库配置](#supabase-数据库配置)
3. [本地开发环境](#本地开发环境)
4. [NAS Docker 部署](#nas-docker-部署)
5. [Vercel 前端部署](#vercel-前端部署)
6. [运行与监控](#运行与监控)

---

## 前置条件

### 您已有的资源
| 资源 | 值 |
|------|-----|
| GitHub 仓库 | https://github.com/jssyxd/AlphaGPT |
| Supabase URL | https://avxcymgihbbqurymnhyo.supabase.co |
| Birdeye API | ✅ 已获取 |
| Solana 钱包 | ✅ 0.32 SOL |
| 飞牛 NAS | ✅ 支持 Docker |

### 需要获取的资源

#### 1. Supabase 数据库密码
1. 登录 https://supabase.com/dashboard
2. 进入项目 `AlphaGPT`
3. 点击左侧 **Project Settings** → **Database**
4. 找到 **Connection string** 部分
5. 复制 **Password**（不是 service role key）

**重要**：Supabase 数据库密码格式为：
```
postgres.[project-ref].[password]
```

您需要在 `.env` 文件中设置：
```
DB_PASSWORD=您的数据库密码
```

---

## Supabase 数据库配置

### 步骤 1：创建数据库表

1. 登录 Supabase Dashboard
2. 点击左侧 **SQL Editor**
3. 点击 **New query**
4. 复制粘贴 `init_db.sql` 文件内容
5. 点击 **Run** 执行

### 步骤 2：获取数据库连接信息

在 Supabase Dashboard 中：

| 配置项 | 路径 |
|--------|------|
| DB_HOST | Project Settings → Database → Host (`db.avxcymgihbbqurymnhyo.supabase.co`) |
| DB_PORT | 默认 `5432` |
| DB_NAME | 默认 `postgres` |
| DB_USER | 默认 `postgres` |
| DB_PASSWORD | Project Settings → Database → Connection string (URI) 中的密码部分 |

---

## 本地开发环境

### 步骤 1：克隆仓库

```bash
git clone https://github.com/jssyxd/AlphaGPT.git
cd AlphaGPT
```

### 步骤 2：创建虚拟环境

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
```

### 步骤 3：安装依赖

```bash
pip install -r requirements.txt
```

### 步骤 4：配置环境变量

复制 `.env` 文件，修改以下关键配置：

```env
# Supabase 数据库（必须修改密码）
DB_HOST=db.avxcymgihbbqurymnhyo.supabase.co
DB_PASSWORD=您的数据库密码

# Birdeye API
BIRDEYE_API_KEY=d96153f7d2b946debf9bf0c924c4d098

# Solana 钱包
SOLANA_PRIVATE_KEY=您的私钥
```

### 步骤 5：测试数据库连接

```bash
python test_db.py
```

如果成功，会显示：
```
✅ 数据库连接成功！
📊 已创建的表: ['tokens', 'ohlcv', 'strategies', ...]
```

### 步骤 6：拉取数据

```bash
python run_data_pipeline.py
```

---

## NAS Docker 部署

### 方法 A：Docker Compose（推荐）

#### 1. 准备文件

在 NAS 上创建目录并上传文件：
```
/your/path/AlphaGPT/
├── .env
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── best_meme_strategy.json
├── init_db.sql
└── src/  (所有 Python 源码)
```

#### 2. 修改 docker-compose.yml

```yaml
version: '3.8'

services:
  alphagpt:
    build: .
    container_name: alphagpt-backend
    restart: unless-stopped
    env_file:
      - .env
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
```

#### 3. 构建并启动

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

#### 4. 检查状态

```bash
docker ps
# 应该看到 alphagpt-backend 正在运行
```

### 方法 B：虚拟机运行

#### 1. 在 Ubuntu 虚拟机中

```bash
# 安装 Python
sudo apt update
sudo apt install python3 python3-pip python3-venv

# 克隆项目
git clone https://github.com/jssyxd/AlphaGPT.git
cd AlphaGPT

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置 .env
nano .env

# 运行
python run_data_pipeline.py  # 先拉取数据
python -m strategy_manager.runner  # 启动交易机器人
```

#### 2. 使用 systemd 保持运行

创建服务文件 `/etc/systemd/system/alphagpt.service`：

```ini
[Unit]
Description=AlphaGPT Trading Bot
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/AlphaGPT
ExecStart=/path/to/AlphaGPT/venv/bin/python -m strategy_manager.runner
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启用服务：
```bash
sudo systemctl daemon-reload
sudo systemctl enable alphagpt
sudo systemctl start alphagpt
sudo systemctl status alphagpt
```

---

## Vercel 前端部署

### 步骤 1：推送前端代码到 GitHub

```bash
cd frontend
git init
git add .
git commit -m "Add AlphaGPT dashboard"
git branch -M main
git remote add origin https://github.com/你的用户名/AlphaGPT-Dashboard.git
git push -u origin main
```

### 步骤 2：在 Vercel 部署

1. 登录 https://vercel.com
2. 点击 **Add New** → **Project**
3. 导入 GitHub 仓库
4. 设置环境变量：
   - `NEXT_PUBLIC_SUPABASE_URL`
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY`
5. 点击 **Deploy**

### 步骤 3：配置域名（可选）

在 Vercel 项目设置中：
- 添加自定义域名
- 配置 frp 转发（如果需要）

---

## 运行与监控

### 日常运行命令

```bash
# 拉取最新数据
python run_data_pipeline.py

# 启动交易机器人
python -m strategy_manager.runner

# 查看日志
tail -f logs/app.log
```

### Docker 运行命令

```bash
# 启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 重启
docker-compose restart

# 停止
docker-compose down
```

### 监控指标

1. **钱包余额**：确保有足够 SOL 支付 gas
2. **持仓状态**：检查 `positions` 表
3. **信号质量**：检查 `signals` 表
4. **交易日志**：检查 `trade_logs` 表

---

## 风险警告

⚠️ **重要提示**：

1. Meme 币交易具有极高风险，可能损失全部本金
2. 本系统仅供测试和学习目的，不构成投资建议
3. 建议先用 **paper 模式** 模拟交易至少 30 天
4. 私钥**绝对不能**上传到 GitHub 或泄露给任何人
5. 定期检查系统运行状态和日志

---

## 常见问题

### Q: 数据库连接失败
A: 检查 `.env` 中的 `DB_PASSWORD` 是否正确，确保 Supabase 项目未暂停

### Q: Birdeye API 返回 429
A: 免费 API 有速率限制，降低 `CONCURRENCY` 配置或升级付费计划

### Q: 交易失败
A: 检查钱包余额、RPC 节点状态、Jupiter 流动性

### Q: 前端无法连接后端
A: 确保 `NEXT_PUBLIC_API_URL` 配置正确，检查 frp 转发设置

---

## 联系支持

- GitHub Issues: https://github.com/jssyxd/AlphaGPT/issues
- QQ群: 1082630631

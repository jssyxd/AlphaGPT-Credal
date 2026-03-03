# AlphaGPT MVP 设计文档

**日期**: 2026-03-04
**版本**: v1.0

---

## 1. 项目概述

### 1.1 目标
构建个人自动化Solana量化交易MVP，先纸交易验证盈利后再实盘。

### 1.2 核心技术栈
- **LLM**: 小米MIMO-V2-Flash (API调用) 生成可解释Alpha因子
- **数据源**: Birdeye + DexScreener → Supabase
- **执行**: Jupiter (Solana) + OKX
- **信号**: Telegram Bot推送
- **部署**: Railway + Vercel
- **测试**: pytest + Playwright E2E

---

## 2. 架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                      AlphaGPT 系统架构                        │
├──────────────┬──────────────┬──────────────┬───────────────┤
│  Data Layer  │  Model Layer │  Risk Layer  │ Execution     │
│              │              │              │    Layer      │
├──────────────┼──────────────┼──────────────┼───────────────┤
│ Supabase DB  │   MIMO-V2-   │  Position    │   Jupiter     │
│ Birdeye API  │   Flash API  │   Sizing     │   DEX         │
│ DexScreener  │   Factor     │  Stop Loss   │   OKX         │
│              │   Generator   │  Telegram    │   Paper Trade │
└──────────────┴──────────────┴──────────────┴───────────────┘
```

---

## 3. 模块设计

### 3.1 数据管道 (Phase 1)

#### 3.1.1 数据获取
- **fetcher.py**: 从Birdeye/DexScreener获取meme币数据
- **processor.py**: 数据清洗和标准化
- **db_manager.py**: Supabase CRUD操作

#### 3.1.2 LLM因子生成
- **llm_factor_generator.py**: 调用MIMO-V2-Flash API
- 每天生成新因子公式（如 `fomo * liq_score > threshold`）
- 返回：formula + score + uncertainty

#### 3.1.3 数据库表结构（优化版）
```sql
-- tokens: 代币信息
tokens (
  address TEXT PRIMARY KEY,
  symbol TEXT,
  name TEXT,
  decimals INT,
  chain TEXT,
  liquidity REAL,
  holders INT,
  creator_percent REAL,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
)

-- ohlcv: K线数据
ohlcv (
  time TIMESTAMP NOT NULL,
  address TEXT NOT NULL,
  open REAL, high REAL, low REAL, close REAL,
  volume REAL, liquidity REAL, fdv REAL,
  source TEXT,
  PRIMARY KEY (time, address)
)

-- strategies: 策略/因子
strategies (
  id SERIAL PRIMARY KEY,
  name TEXT,
  formula TEXT,
  formula_json JSONB,
  score REAL,
  uncertainty REAL,
  backtest_result JSONB,
  status TEXT DEFAULT 'active',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
)

-- positions: 持仓
positions (
  id SERIAL PRIMARY KEY,
  token_address TEXT,
  symbol TEXT,
  entry_price REAL,
  entry_time TIMESTAMP,
  amount_sol REAL,
  amount_tokens REAL,
  status TEXT DEFAULT 'open',
  exit_price REAL,
  exit_time TIMESTAMP,
  pnl REAL,
  stop_loss_price REAL,
  take_profit_price REAL
)

-- trades: 交易记录
trades (
  id SERIAL PRIMARY KEY,
  token_address TEXT,
  symbol TEXT,
  action TEXT,
  amount_sol REAL,
  amount_tokens REAL,
  price REAL,
  fee REAL,
  tx_signature TEXT,
  mode TEXT,
  created_at TIMESTAMP DEFAULT NOW()
)

-- signals: 信号记录
signals (
  id SERIAL PRIMARY KEY,
  token_address TEXT,
  symbol TEXT,
  action TEXT,
  score REAL,
  uncertainty REAL,
  factors JSONB,
  reasons TEXT,
  sent_to_telegram BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT NOW()
)

-- daily_reports: 每日报告
daily_reports (
  id SERIAL PRIMARY KEY,
  date DATE UNIQUE,
  total_pnl REAL,
  trade_count INT,
  win_count INT,
  loss_count INT,
  active_positions INT,
  report_json JSONB,
  created_at TIMESTAMP DEFAULT NOW()
)
```

### 3.2 回测引擎 (Phase 2)

#### 3.2.1 功能
- Walk-forward optimization
- 80/20 OOS validation
- Sharpe ratio, win rate, max drawdown计算

#### 3.2.2 奖励迭代
- 基于回测结果自动调整因子权重
- 选择最优策略用于实盘

### 3.3 执行层 (Phase 3)

#### 3.3.1 Jupiter集成
- DEX聚合器交易
- 滑点模拟
- 最佳路径选择

#### 3.3.2 OKX集成
- 模拟交易模式
- 实盘交易（可选）
- 持仓同步

#### 3.3.3 Telegram Bot
- 买入/卖出信号 + 代币 + 价格
- 完整交易单（数量、风控理由、不确定性分数）
- 每日策略总结 + 持仓报告

### 3.4 部署 (Phase 4)

#### 3.4.1 Railway
- 后端API服务
- 定时任务（数据管道、因子生成）
- 环境变量管理

#### 3.4.2 Vercel
- Next.js前端
- 仪表板展示

#### 3.4.3 E2E测试
- Playwright测试仪表板
- pytest单元测试

---

## 4. 风控设计

### 4.1 仓位控制
- 每笔交易最大1%风险
- 最多3个并发持仓
- 最低保留0.1 SOL

### 4.2 安全过滤
- 最低流动性: $10,000
- 创建者持仓 < 20%
- 最少持有者: 50人

### 4.3 止损止盈
- 止损: 5%
- 止盈: 10%
- 移动止盈: 盈利8%后回撤5%触发

---

## 5. 测试策略

### 5.1 单元测试 (pytest)
- 数据管道测试
- LLM集成测试
- 风控逻辑测试

### 5.2 E2E测试 (Playwright)
- 仪表板加载测试
- 交互功能测试

### 5.3 工作流
```
每个Phase:
1. 编写测试 → 运行(应失败)
2. 实现功能 → 运行测试(应通过)
3. 提交 → PR
```

---

## 6. 实施计划

| Phase | 内容 | 测试 |
|-------|------|------|
| Phase 1 | 数据管道 + LLM因子生成 | pytest |
| Phase 2 | 回测 + 奖励迭代 | pytest |
| Phase 3 | OKX模拟执行 + Telegram信号 | pytest |
| Phase 4 | Railway部署 + 仪表板E2E | pytest + Playwright |
| Phase 5 | Credal不确定性 + 风控增强 | pytest |

---

## 7. 网络配置

- **代理**: http://192.168.1.5:7890
- **环境变量**: .env已配置

---

**文档结束**

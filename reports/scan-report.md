# AlphaGPT 项目扫描报告

**扫描日期**: 2026-03-04
**扫描工具**: Claude Code
**项目**: AlphaGPT-Credal (Solana量化交易系统)

---

## 1. 项目概述

### 1.1 项目目标
个人自动化Solana量化交易系统，使用小米MIMO-V2-Flash LLM生成可解释Alpha因子 + Credal不确定性 + Jupiter执行 + Telegram信号 + Railway部署。

### 1.2 技术栈
- **后端**: Python 3.10+, PyTorch 2.0+
- **数据库**: Supabase (PostgreSQL)
- **数据源**: Birdeye API, DexScreener API
- **区块链**: Solana, Jupiter Aggregator
- **前端**: Next.js + Streamlit
- **部署**: Railway, Vercel

---

## 2. 目录结构分析

```
AlphaGPT/
├── projects/                    # 主项目目录
│   ├── model_core/              # 核心模型模块
│   │   ├── credal_transformer.py    # Credal Transformer核心
│   │   ├── alphagpt.py              # AlphaGPT模型
│   │   ├── factors.py               # 因子生成
│   │   ├── engine.py                # 模型引擎
│   │   ├── backtest.py              # 回测模块
│   │   ├── data_loader.py           # 数据加载器
│   │   ├── ops.py                   # 操作函数
│   │   ├── config.py                # 配置
│   │   └── vm.py                    # 虚拟机
│   ├── data_pipeline/              # 数据管道
│   │   ├── fetcher.py               # 数据获取
│   │   ├── processor.py             # 数据处理
│   │   ├── data_manager.py          # 数据管理
│   │   ├── db_manager.py            # 数据库管理
│   │   ├── config.py                # 配置
│   │   ├── run_pipeline.py          # 管道入口
│   │   └── providers/               # 数据提供者
│   │       ├── base.py
│   │       ├── birdeye.py
│   │       └── dexscreener.py
│   ├── execution/                   # 执行模块
│   │   ├── paper_trader.py          # 纸交易
│   │   ├── trader.py
│   │   ├── jupiter.py               # 实盘交易 # Jupiter集成
│   │   ├── rpc_handler.py           # RPC处理
│   │   ├── config.py                # 配置
│   │   └── utils.py                 # 工具函数
│   ├── strategy_manager/            # 策略管理
│   │   ├── runner.py                # 策略运行器
│   │   ├── risk_enhanced.py         # 增强风控
│   │   ├── risk.py                  # 风控
│   │   ├── portfolio.py             # 投资组合
│   │   └── config.py                # 配置
│   ├── backtest/                    # 回测
│   │   └── engine.py                # 回测引擎
│   ├── dashboard/                   # 仪表板
│   │   ├── app.py                   # Streamlit应用
│   │   ├── data_service.py          # 数据服务
│   │   └── visualizer.py            # 可视化
│   ├── frontend/                    # Next.js前端
│   │   ├── src/app/                 # Next.js App Router
│   │   └── components/ui/           # UI组件
│   ├── requirements.txt             # 依赖
│   ├── requirements-optional.txt    # 可选依赖
│   ├── docker-compose.yml           # Docker编排
│   ├── Dockerfile                   # Docker配置
│   ├── README.md                    # 项目文档
│   ├── DEPLOYMENT.md               # 部署文档
│   └── run_data_pipeline.py        # 数据管道入口
├── DEVELOPMENT_REPORT.md            # 开发报告
├── AGENT_DEVELOPMENT_LOG.md         # 开发日志
└── (reports/)                       # 报告目录(待创建)
```

---

## 3. 核心模块状态评估

### 3.1 model_core/ (核心模型) - ⚠️ 需要验证
| 文件 | 状态 | 备注 |
|------|------|------|
| credal_transformer.py | ⚠️ 需测试 | Credal Transformer核心 |
| alphagpt.py | ⚠️ 需测试 | 主模型 |
| factors.py | ⚠️ 需测试 | 因子生成 |
| engine.py | ⚠️ 需测试 | 模型引擎 |
| backtest.py | ⚠️ 需测试 | 回测模块 |

### 3.2 data_pipeline/ (数据管道) - ⚠️ 需要实现
| 文件 | 状态 | 备注 |
|------|------|------|
| fetcher.py | ⚠️ 需完善 | 基础框架存在 |
| processor.py | ⚠️ 需完善 | 基础框架存在 |
| db_manager.py | ⚠️ 需完善 | 基础框架存在 |
| providers/birdeye.py | ⚠️ 需完善 | 需API Key |
| providers/dexscreener.py | ⚠️ 需完善 | 需API Key |

**需要**: LLM因子生成集成 (小米MIMO-V2-Flash)

### 3.3 execution/ (执行) - ⚠️ 需要完善
| 文件 | 状态 | 备注 |
|------|------|------|
| paper_trader.py | ✅ 基础完成 | 纸交易模拟 |
| trader.py | ⚠️ 需完善 | 实盘交易 |
| jupiter.py | ⚠️ 需完善 | DEX集成 |

**需要**: OKX模拟执行集成

### 3.4 strategy_manager/ (策略管理) - ✅ 基础完成
| 文件 | 状态 | 备注 |
|------|------|------|
| runner.py | ✅ | 策略运行器 |
| risk_enhanced.py | ✅ | 增强风控 |
| risk.py | ✅ | 基础风控 |
| portfolio.py | ✅ | 投资组合 |

### 3.5 dashboard/ (仪表板) - ⚠️ 需要E2E测试
| 文件 | 状态 | 备注 |
|------|------|------|
| app.py | ⚠️ 需完善 | Streamlit应用 |
| data_service.py | ⚠️ 需完善 | 数据服务 |
| visualizer.py | ⚠️ 需完善 | 可视化 |

**需要**: Playwright E2E测试

---

## 4. 缺失组件分析

### 4.1 Phase 1: 数据管道 + LLM因子生成
- [ ] 完整的数据获取流程
- [ ] 小米MIMO-V2-Flash LLM集成
- [ ] 因子生成与存储
- [ ] pytest单元测试
- [ ] E2E测试

### 4.2 Phase 2: 回测 + 奖励迭代
- [ ] 完整的回测框架
- [ ] 奖励迭代机制
- [ ] 策略评估指标

### 4.3 Phase 3: OKX模拟执行 + Telegram信号
- [ ] OKX API集成 (模拟/实盘)
- [ ] Telegram bot信号推送
- [ ] 交易通知系统
- [ ] 代理配置支持 (http://192.168.1.5:7890)

### 4.4 Phase 4: Railway一键部署 + 仪表板
- [ ] Railway部署配置
- [ ] 一键部署脚本
- [ ] Playwright E2E测试 (仪表板验证)
- [ ] Vercel前端部署

### 4.5 Phase 5: Credal Transformer不确定性 + 风控
- [ ] 不确定性量化
- [ ] 风控增强
- [ ] 决策弃权机制

---

## 5. 测试框架状态

### 5.1 现有测试
- `test_core_minimal.py` - 核心模块最小测试
- `test_db.py` - 数据库测试

### 5.2 需要添加
- [ ] pytest单元测试 (Phase 1)
- [ ] Playwright E2E测试 (Phase 4)
- [ ] 集成测试 (各Phase)

---

## 6. 部署状态

### 6.1 现有配置
- Dockerfile ✅
- docker-compose.yml ✅
- requirements.txt ✅
- Next.js前端 ✅

### 6.2 需要配置
- [ ] Railway配置
- [ ] 环境变量模板
- [ ] CI/CD流程

---

## 7. 建议实施计划

### 7.1 优先级排序
1. **Phase 1**: 数据管道 + LLM因子生成 (最优先)
2. **Phase 2**: 回测 + 奖励迭代
3. **Phase 3**: OKX模拟执行 + Telegram信号
4. **Phase 4**: Railway一键部署 + 仪表板
5. **Phase 5**: Credal Transformer不确定性 + 风控

### 7.2 TDD工作流
```
每个Phase:
1. 编写E2E测试/单元测试 → 运行(应失败)
2. 实现功能 → 运行测试(应通过)
3. 代码审查 → 提交 → PR
4. 下一个Phase
```

---

## 8. 风险与限制

1. **API限制**: Birdeye免费版30k请求/月
2. **网络环境**: 需要代理配置 (http://192.168.1.5:7890)
3. **Solana RPC**: 公共节点可能限流
4. **纸交易验证**: 需30天模拟才能实盘

---

**报告结束**

# AlphaGPT Credal Transformer 二次开发报告

**项目名称**: AlphaGPT Credal Transformer Customization
**开发日期**: 2026-02-20
**开发者**: Claude Code Multi-Agent Team
**原始项目**: https://github.com/imbue-bit/AlphaGPT
**二次开发仓库**: https://github.com/jssyxd/AlphaGPT-Credal

---

## 1. 项目概述

### 1.1 开发背景
本项目基于 imbue-bit/AlphaGPT 进行定制化二次开发，引入 Credal Transformer 技术（来自 arXiv 2510.12137），构建针对 Solana meme 币的量化交易系统。

### 1.2 核心创新
- **Credal Transformer**: 使用证据理论和 Dirichlet 分布替代传统 Softmax
- **不确定性感知**: 高不确定性时自动弃权，避免过度自信交易
- **可解释因子**: 生成人类可读的交易公式
- **低资金优化**: 针对 $50-500 资金量的风险控制

---

## 2. 技术架构

### 2.1 系统架构图
```
┌─────────────────────────────────────────────────────────────┐
│                    AlphaGPT 系统架构                         │
├──────────────┬──────────────┬──────────────┬───────────────┤
│  Data Layer  │  Model Layer │  Risk Layer  │ Execution     │
│              │              │              │    Layer      │
├──────────────┼──────────────┼──────────────┼───────────────┤
│ Supabase DB  │   Credal     │  Position    │   Jupiter     │
│ Birdeye API  │ Transformer  │   Sizing     │   DEX Aggreg. │
│ DexScreener  │   Factor     │  Stop Loss   │   Paper Trade │
│              │   Generator  │  Japan Tax   │   Live Trade  │
└──────────────┴──────────────┴──────────────┴───────────────┘
```

### 2.2 技术栈
- **后端**: Python 3.11+, PyTorch 2.0+
- **数据库**: Supabase (PostgreSQL)
- **数据源**: Birdeye API, DexScreener API
- **区块链**: Solana, Jupiter Aggregator
- **部署**: Vercel (Frontend), Railway/Render (Backend)

---

## 3. 核心模块开发

### 3.1 Credal Transformer 核心
**文件**: `model_core/credal_transformer.py`
**代码行数**: 452 行

#### 3.1.1 核心算法实现
```python
# 证据质量计算
α_ij = exp(s_ij) + 1

# 不确定性度量
U = L / sum(α)

# Dirichlet 分布归一化（替代 Softmax）
P = α / sum(α)
```

#### 3.1.2 关键类
- `EvidenceQualityLayer`: 将注意力分数转换为证据质量
- `CredalTransformer`: 不确定性感知的 Transformer 模型
- `FactorGenerator`: 使用 SymPy 生成可解释因子
- `UncertaintyAwareStrategy`: 不确定性感知交易策略

#### 3.1.3 特性
- 自动弃权机制（不确定性 > 阈值时）
- 可解释的因子公式生成
- 复杂度惩罚防止过拟合

### 3.2 回测引擎
**文件**: `backtest/engine.py`
**代码行数**: 475 行

#### 3.2.1 验证方法
- **Walk-forward Optimization**: 滚动训练/测试窗口
- **80/20 OOS Validation**: 样本外验证防过拟合
- **Sharpe Ratio Calculation**: 夏普比率计算

#### 3.2.2 日本税务合规
```python
# 自动税率计算
def calculate_japan_tax(profit_jpy):
    if profit_jpy <= 200000: return 0      # 免税额
    elif profit_jpy <= 1950000: return 0.05  # 5%
    elif profit_jpy <= 3300000: return 0.10  # 10%
    # ... 最高 45%
```

#### 3.2.3 性能指标
- 总收益率
- 夏普比率
- 胜率
- 最大回撤
- 盈亏比

### 3.3 风控模块
**文件**: `strategy_manager/risk_enhanced.py`
**代码行数**: 365 行

#### 3.3.1 仓位控制
```python
class RiskConfig:
    max_position_size_pct = 0.01  # 每笔 1%
    max_positions = 3              # 最多 3 个持仓
    min_balance_sol = 0.1          # 保留 0.1 SOL
```

#### 3.3.2 安全过滤
- 最低流动性: $10,000
- 创建者持仓 < 20%（反欺诈）
- 最少持有者: 50 人
- 止损: 5%
- 止盈: 10%
- 移动止盈: 盈利 8% 后回撤 5% 触发

#### 3.3.3 税务提醒
- 盈利超 5 万日元自动提醒
- 申报截止日期提醒（3月15日）
- 预估税额计算

### 3.4 纸交易模块
**文件**: `execution/paper_trader.py`
**代码行数**: 385 行

#### 3.4.1 功能特性
- `PaperTrader`: 完整模拟交易环境
- `HybridTrader`: 纸/实盘自动切换
- 滑点和手续费模拟
- 交易历史记录和导出

#### 3.4.2 安全设计
- 默认 MODE=paper（安全第一）
- 真实交易需显式切换
- 完整的性能报告

---

## 4. 数据库设计

### 4.1 表结构
**文件**: `init_db.sql`

| 表名 | 用途 | 关键字段 |
|------|------|----------|
| tokens | 代币信息 | address, symbol, name, decimals |
| ohlcv | K线数据 | time, address, open, high, low, close, volume |
| strategies | 策略存储 | id, formula, score, uncertainty |
| positions | 持仓记录 | token, entry_price, amount, pnl |
| trade_logs | 交易日志 | action, price, amount, timestamp |
| signals | 交易信号 | token, action, confidence, timestamp |

### 4.2 Supabase 集成
- 替代本地 PostgreSQL
- 云端托管，免费额度充足
- 与 Vercel 无缝集成

---

## 5. 开发过程

### 5.1 开发团队
采用多 Agent 并行开发模式：

| Agent | 职责 | 产出 |
|-------|------|------|
| Data Agent | 数据管道 | init_db.sql |
| Model Agent | Credal Transformer | credal_transformer.py |
| Risk Agent | 风控回测 | engine.py + risk_enhanced.py |
| Execution Agent | 交易执行 | paper_trader.py |
| UI Agent | 部署文档 | DEPLOYMENT.md |
| Reviewer Agent | 代码审查 | test_core_minimal.py |

### 5.2 开发时间线
- **Phase 1**: 基础设施搭建（1天）
- **Phase 2**: 核心模块开发（2天）
- **Phase 3**: 集成测试（1天）
- **Phase 4**: 文档编写和部署（1天）

---

## 6. 测试结果

### 6.1 模块测试
```
[测试1] 环境配置文件检查... ✅
[测试2] 数据库初始化脚本检查... ✅ (6/6表)
[测试3] 核心模块文件检查... ✅ (4/4模块)
[测试4] 部署文档检查... ✅
[测试5] 关键代码结构检查... ✅ (4/4特性)
[测试6] 风控模块功能检查... ✅ (4/4特性)
[测试7] 回测引擎功能检查... ✅ (4/4特性)
```

### 6.2 代码统计
| 模块 | 文件 | 代码行数 |
|------|------|----------|
| Credal Transformer | credal_transformer.py | 452 |
| 回测引擎 | engine.py | 475 |
| 风控模块 | risk_enhanced.py | 365 |
| 纸交易 | paper_trader.py | 385 |
| **总计** | **4个核心文件** | **1,677行** |

---

## 7. 部署方案

### 7.1 本地开发
```bash
pip install -r requirements.txt
python run_data_pipeline.py
MODE=paper python -m strategy_manager.runner
```

### 7.2 生产部署
- **前端**: Vercel (Streamlit Dashboard)
- **后端**: Railway/Render (Trading Bot)
- **数据库**: Supabase (PostgreSQL)

---

## 8. 第一性原理对齐

### 8.1 Edge（优势）
- ✅ Credal Transformer 不确定性感知
- ✅ 可解释因子公式
- ✅ 目标胜率 >55%，夏普 >1.5

### 8.2 Risk Control（风险控制）
- ✅ 1% 仓位规则
- ✅ 流动性过滤（$10k）
- ✅ 反欺诈检测
- ✅ 日本税务合规

### 8.3 Execution（执行）
- ✅ 纸交易优先（30天验证）
- ✅ Solana 低费用执行
- ✅ MODE=paper 默认安全

---

## 9. 二次开发改动清单

### 9.1 新增文件
```
model_core/credal_transformer.py    # 452行 - Credal Transformer核心
backtest/engine.py                  # 475行 - 回测引擎
strategy_manager/risk_enhanced.py   # 365行 - 增强风控
execution/paper_trader.py           # 385行 - 纸交易模块
init_db.sql                         # 数据库初始化
DEPLOYMENT.md                       # 部署指南
README.md                           # 双语README
AGENT_DEVELOPMENT_LOG.md            # 开发日志
TASK_STATUS.md                      # 任务状态
QUICK_START.md                      # 快速启动
```

### 9.2 修改文件
```
.gitignore                          # 添加忽略规则
requirements.txt                    # 依赖更新（如有）
```

### 9.3 删除/排除文件
- 测试临时文件
- venv 虚拟环境
- __pycache__ 缓存
- .env 敏感配置

---

## 10. 已知限制

1. **PyTorch 依赖**: 较重，可能需要优化
2. **Birdeye API 限制**: 免费版 30k 请求/月
3. **Solana RPC**: 公共节点可能限流
4. **纸交易精度**: 价格模拟非 100% 准确

---

## 11. 未来优化方向

1. **模型优化**: 轻量化 Credal Transformer
2. **数据源扩展**: 集成更多 DEX 数据源
3. **策略优化**: 强化学习优化因子权重
4. **UI 增强**: 实时交易监控大屏
5. **多链支持**: 扩展至 Ethereum、Base 等

---

## 12. 参考资料

- **原始项目**: https://github.com/imbue-bit/AlphaGPT
- **Credal Transformer**: arXiv 2510.12137
- **Supabase**: https://supabase.com
- **Birdeye API**: https://birdeye.so
- **Jupiter**: https://jup.ag

---

## 13. 许可证

本项目基于 MIT 许可证开源，二次开发代码同样遵循 MIT 许可证。

---

**报告生成时间**: 2026-02-20
**报告版本**: v1.0
**开发者**: Claude Code Multi-Agent Team

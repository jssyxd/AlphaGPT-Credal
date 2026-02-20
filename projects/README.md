# AlphaGPT - Credal Transformer Quantitative Trading System

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-red.svg)](https://pytorch.org/)
[![Solana](https://img.shields.io/badge/Solana-Blockchain-purple.svg)](https://solana.com/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

> **⚠️ Risk Warning**: Cryptocurrency trading carries high risks. This system is for educational purposes only and does not constitute investment advice. Please use `MODE=paper` for at least 30 days of testing before any live trading.

[中文版本](#alphagpt-基于证据理论的量化交易系统)

## 🎯 Overview

AlphaGPT is a Solana-based meme coin quantitative trading framework enhanced with **Credal Transformer** (from arXiv 2510.12137). It uses evidence theory and Dirichlet distributions instead of Softmax to generate uncertainty-aware, interpretable trading factor formulas.

### Key Features

- **🧠 Credal Transformer**: Uncertainty-aware factor generation using evidence theory + Dirichlet distribution
- **📊 Interpretable Factors**: Human-readable formulas like `"fomo * liq_score > threshold"`
- **🛡️ Risk Control**: 1% position sizing, stop-loss (5%), take-profit (10%), anti-rug detection
- **📈 Backtesting**: Walk-forward optimization, 80/20 OOS validation, Sharpe ratio calculation
- **💰 Paper Trading**: Safe simulation mode before live trading
- **🇯🇵 Japan Tax**: Automatic tax calculation and filing reminders

## 🏗️ Architecture

```
AlphaGPT/
├── model_core/
│   ├── credal_transformer.py    # Credal Transformer core
│   ├── alphagpt.py              # AlphaGPT model
│   └── factors.py               # Factor generation
├── backtest/
│   └── engine.py                # Backtesting engine
├── strategy_manager/
│   ├── runner.py                # Strategy runner
│   ├── risk_enhanced.py         # Risk management
│   └── portfolio.py             # Portfolio management
├── execution/
│   ├── paper_trader.py          # Paper trading simulator
│   ├── trader.py                # Live trading
│   └── jupiter.py               # Jupiter DEX integration
├── data_pipeline/
│   ├── fetcher.py               # Birdeye/DexScreener data fetcher
│   └── db_manager.py            # Supabase database manager
└── dashboard/
    └── app.py                   # Streamlit dashboard
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Git
- Supabase account (free tier)
- Birdeye API key (free tier: 30k requests/month)
- Solana wallet (for live trading)

### Installation

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/AlphaGPT.git
cd AlphaGPT/projects

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys and configuration
```

### Configuration

Create `.env` file:

```env
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key

# Database Configuration
DB_HOST=db.your-project.supabase.co
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=your-password

# API Keys
BIRDEYE_API_KEY=your-birdeye-api-key

# Solana Configuration
SOLANA_RPC=https://api.mainnet-beta.solana.com
WALLET_PRIVATE_KEY=your-base58-private-key

# Trading Mode
MODE=paper  # paper for simulation, live for real trading
```

### Database Setup

1. Go to Supabase Dashboard → SQL Editor
2. Run the contents of `init_db.sql`
3. Verify tables are created: tokens, ohlcv, strategies, positions, trade_logs, signals

### Running the System

```bash
# 1. Fetch market data
python run_data_pipeline.py

# 2. Run backtest
python backtest/engine.py

# 3. Start paper trading (SAFE MODE)
MODE=paper python -m strategy_manager.runner

# 4. Launch dashboard
streamlit run dashboard/app.py
```

## 🧪 Testing

```bash
# Run minimal core test
python test_core_minimal.py

# Run setup wizard
python setup_auto.py
```

## 📊 Performance Metrics

Target metrics for strategy validation:
- **Win Rate**: > 55%
- **Sharpe Ratio**: > 1.5
- **Max Drawdown**: < 20%

## 🛡️ Risk Management

### Position Sizing
- Maximum 1% risk per trade
- Maximum 3 concurrent positions
- Minimum 0.1 SOL balance reserve

### Safety Filters
- Minimum $10k liquidity
- Anti-rug detection (creator holdings < 20%)
- Minimum 50 holders
- Stop-loss at 5%
- Trailing stop after 8% profit

## 📝 Tax Compliance (Japan)

The system includes Japanese tax calculation:
- Automatic profit tracking in JPY
- Estimated tax rate calculation (5%-45%)
- Filing deadline reminders (March 15)
- Tax filing requirement alerts (>200,000 JPY)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Original AlphaGPT by [imbue-bit](https://github.com/imbue-bit/AlphaGPT)
- Credal Transformer paper (arXiv 2510.12137)
- Birdeye API for market data
- Jupiter Aggregator for DEX integration

## ⚠️ Disclaimer

This software is for educational purposes only. Cryptocurrency trading involves substantial risk of loss. The authors assume no responsibility for your trading results. Always do your own research and never trade with money you cannot afford to lose.

---

# AlphaGPT - 基于证据理论的量化交易系统

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-red.svg)](https://pytorch.org/)
[![Solana](https://img.shields.io/badge/Solana-区块链-purple.svg)](https://solana.com/)
[![许可证](https://img.shields.io/badge/许可证-MIT-green.svg)](LICENSE)

> **⚠️ 风险提示**: 加密货币交易具有高风险。本系统仅供教育目的，不构成投资建议。实盘交易前请使用 `MODE=paper` 模式测试至少30天。

[English Version](#alphagpt---credal-transformer-quantitative-trading-system)

## 🎯 项目概述

AlphaGPT 是一个基于 Solana 的 meme 币量化交易框架，采用 **Credal Transformer**（来自 arXiv 2510.12137）技术。它使用证据理论和 Dirichlet 分布替代 Softmax，生成具有不确定性感知的、可解释的交易因子公式。

### 核心特性

- **🧠 Credal Transformer**: 使用证据理论 + Dirichlet 分布的不确定性感知因子生成
- **📊 可解释因子**: 人类可读的公式，如 `"fomo * liq_score > threshold"`
- **🛡️ 风险控制**: 1%仓位控制、止损(5%)、止盈(10%)、反欺诈检测
- **📈 回测框架**: Walk-forward 优化、80/20 样本外验证、夏普比率计算
- **💰 纸交易**: 实盘前的安全模拟模式
- **🇯🇵 日本税务**: 自动税务计算和申报提醒

## 🏗️ 系统架构

```
AlphaGPT/
├── model_core/
│   ├── credal_transformer.py    # Credal Transformer 核心
│   ├── alphagpt.py              # AlphaGPT 模型
│   └── factors.py               # 因子生成
├── backtest/
│   └── engine.py                # 回测引擎
├── strategy_manager/
│   ├── runner.py                # 策略运行器
│   ├── risk_enhanced.py         # 风险管理
│   └── portfolio.py             # 投资组合管理
├── execution/
│   ├── paper_trader.py          # 纸交易模拟器
│   ├── trader.py                # 实盘交易
│   └── jupiter.py               # Jupiter DEX 集成
├── data_pipeline/
│   ├── fetcher.py               # Birdeye/DexScreener 数据获取
│   └── db_manager.py            # Supabase 数据库管理
└── dashboard/
    └── app.py                   # Streamlit 仪表板
```

## 🚀 快速开始

### 环境要求

- Python 3.10+
- Git
- Supabase 账户（免费版）
- Birdeye API 密钥（免费版：每月3万次请求）
- Solana 钱包（用于实盘交易）

### 安装步骤

```bash
# 克隆仓库
git clone https://github.com/YOUR_USERNAME/AlphaGPT.git
cd AlphaGPT/projects

# 安装依赖
pip install -r requirements.txt

# 配置环境
cp .env.example .env
# 编辑 .env 填入您的 API 密钥和配置
```

### 配置说明

创建 `.env` 文件：

```env
# Supabase 配置
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key

# 数据库配置
DB_HOST=db.your-project.supabase.co
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=your-password

# API 密钥
BIRDEYE_API_KEY=your-birdeye-api-key

# Solana 配置
SOLANA_RPC=https://api.mainnet-beta.solana.com
WALLET_PRIVATE_KEY=your-base58-private-key

# 交易模式
MODE=paper  # paper=模拟交易，live=实盘交易
```

### 数据库设置

1. 进入 Supabase 控制台 → SQL Editor
2. 运行 `init_db.sql` 文件内容
3. 验证表已创建：tokens, ohlcv, strategies, positions, trade_logs, signals

### 运行系统

```bash
# 1. 获取市场数据
python run_data_pipeline.py

# 2. 运行回测
python backtest/engine.py

# 3. 启动纸交易（安全模式）
MODE=paper python -m strategy_manager.runner

# 4. 启动仪表板
streamlit run dashboard/app.py
```

## 🧪 测试

```bash
# 运行最小化核心测试
python test_core_minimal.py

# 运行配置向导
python setup_auto.py
```

## 📊 性能指标

策略验证目标指标：
- **胜率**: > 55%
- **夏普比率**: > 1.5
- **最大回撤**: < 20%

## 🛡️ 风险管理

### 仓位控制
- 每笔交易最大 1% 风险
- 最多 3 个并发持仓
- 最低保留 0.1 SOL 余额

### 安全过滤
- 最低 $10k 流动性
- 反欺诈检测（创建者持仓 < 20%）
- 最少 50 个持有者
- 5% 止损
- 盈利 8% 后启用移动止盈

## 📝 税务合规（日本）

系统包含日本税务计算：
- 自动日元利润追踪
- 预估税率计算（5%-45%）
- 申报截止日期提醒（3月15日）
- 税务申报要求提醒（>20万日元）

## 🤝 贡献

欢迎贡献！请随时提交 Pull Request。

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

- 原作者 [imbue-bit](https://github.com/imbue-bit/AlphaGPT)
- Credal Transformer 论文 (arXiv 2510.12137)
- Birdeye API 提供市场数据
- Jupiter Aggregator 提供 DEX 集成

## ⚠️ 免责声明

本软件仅供教育目的。加密货币交易涉及重大损失风险。作者不对您的交易结果承担任何责任。请始终进行自己的研究，切勿使用无法承受损失的资金进行交易。

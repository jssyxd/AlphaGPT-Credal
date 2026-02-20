# AlphaGPT Agent Development Log

> This document describes the development process for future Agent reference and secondary development.

**Project**: AlphaGPT Customized Version
**Development Date**: 2026-02-20
**Lead Agent**: Claude Code (Multi-Agent Team)
**Team Structure**: 6 Specialized Agents

---

## 📋 Executive Summary

This project customized the original [imbue-bit/AlphaGPT](https://github.com/imbue-bit/AlphaGPT) with Credal Transformer technology (arXiv 2510.12137) for uncertainty-aware quantitative trading on Solana meme coins.

**Key Achievements**:
- ✅ Credal Transformer core with evidence theory + Dirichlet distribution
- ✅ Walk-forward backtesting with 80/20 OOS validation
- ✅ Enhanced risk management (1% position, Japan tax compliance)
- ✅ Paper trading simulator for safe testing
- ✅ Supabase integration replacing local PostgreSQL
- ✅ Complete deployment guides (Vercel, Railway, Docker)

---

## 🏗️ Development Architecture

### Agent Team Structure

```
┌─────────────────────────────────────────────────────────────┐
│                    Development Team                          │
├──────────────┬──────────────┬──────────────┬───────────────┤
│  Data Agent  │  Model Agent │  Risk Agent  │ Execution     │
│              │              │              │    Agent      │
├──────────────┴──────────────┴──────────────┴───────────────┤
│  UI Agent                    │  Reviewer Agent             │
└──────────────────────────────┴─────────────────────────────┘
```

### Agent Responsibilities

| Agent | Role | Key Deliverables |
|-------|------|------------------|
| **Data Agent** | Data Pipeline & Integration | `init_db.sql` - 6-table Supabase schema |
| **Model Agent** | Credal Transformer Core | `credal_transformer.py` - 452 lines |
| **Risk Agent** | Risk Control & Backtesting | `backtest/engine.py` (475 lines) + `risk_enhanced.py` (365 lines) |
| **Execution Agent** | Trading & Automation | `paper_trader.py` - Paper trading simulator |
| **UI Agent** | Frontend & Deployment | `DEPLOYMENT.md` - Complete deployment guide |
| **Reviewer Agent** | QA & Integration | `test_core_minimal.py` + validation framework |

---

## 📁 Codebase Structure

```
projects/
├── 📄 Configuration Files
│   ├── .env                          # Environment template (872 chars)
│   ├── requirements.txt              # Python dependencies
│   └── init_db.sql                   # Supabase schema (6 tables)
│
├── 📄 Documentation
│   ├── README.md                     # Bilingual documentation (EN/CN)
│   ├── DEPLOYMENT.md                 # Deployment guide (6610 chars)
│   ├── QUICK_START.md                # Quick start guide
│   ├── AGENT_DEVELOPMENT_LOG.md      # This file
│   └── TASK_STATUS.md                # Task completion report
│
├── 📄 Testing & Setup
│   ├── test_core_minimal.py          # Minimal test suite
│   ├── setup_auto.py                 # Auto-configuration wizard
│   └── test_report.json              # Test results
│
├── 🔧 Core Modules
│   ├── model_core/
│   │   └── credal_transformer.py     # Credal Transformer implementation
│   ├── backtest/
│   │   └── engine.py                 # Backtesting engine
│   ├── strategy_manager/
│   │   └── risk_enhanced.py          # Risk management
│   └── execution/
│       └── paper_trader.py           # Paper trading
│
└── 📊 Dashboard
    └── dashboard/
        └── app.py                     # Streamlit dashboard
```

---

## 🔬 Technical Implementation

### 1. Credal Transformer (Model Agent)

**Core Innovation**: Replace Softmax with Dirichlet distribution for uncertainty quantification

```python
# Evidence quality calculation: α = exp(s) + 1
evidence = torch.exp(scores) * self.evidence_scale + 1

# Uncertainty: U = L / sum(α)
uncertainty = L / evidence.sum(dim=-1, keepdim=True)

# Dirichlet normalization (replaces Softmax)
dirichlet_probs = evidence / evidence.sum(dim=-1, keepdim=True)
```

**Key Features**:
- `EvidenceQualityLayer`: Converts attention scores to evidence masses
- `CredalTransformer`: Uncertainty-aware transformer with abstention mechanism
- `FactorGenerator`: SymPy-based interpretable formula generation
- `UncertaintyAwareStrategy`: High-uncertainty abstention for safety

### 2. Backtesting Engine (Risk Agent)

**Validation Methods**:
- Walk-forward optimization (rolling train/test windows)
- 80/20 Out-of-Sample (OOS) validation
- Sharpe ratio, win rate, max drawdown calculation

**Japan Tax Compliance**:
```python
# Automatic tax calculation based on profit brackets
def calculate_japan_tax(profit_jpy):
    if profit_jpy <= 200000: return 0  # Tax-free threshold
    elif profit_jpy <= 1950000: return 0.05
    elif profit_jpy <= 3300000: return 0.10
    # ... up to 45% for >40M JPY
```

### 3. Risk Management (Risk Agent)

**Position Sizing**:
```python
@dataclass
class RiskConfig:
    max_position_size_pct: float = 0.01  # 1% per trade
    max_positions: int = 3               # Max 3 concurrent
    min_balance_sol: float = 0.1         # Minimum reserve
```

**Safety Filters**:
- Minimum $10k liquidity
- Creator holdings < 20% (anti-rug)
- Minimum 50 holders
- Stop-loss: 5%
- Trailing stop: After 8% profit, 5% drawdown

### 4. Paper Trading (Execution Agent)

**HybridTrader**: Automatic mode switching
```python
class HybridTrader:
    def __init__(self, mode='paper'):
        self.mode = mode
        self.paper_trader = PaperTrader()
        self.live_trader = None  # Live trading on demand
```

**Features**:
- Complete trade simulation
- Slippage and commission modeling
- Performance reporting
- Trade history export

---

## 🧪 Testing Results

```
[TEST SUMMARY]
✅ Environment config check: PASSED
✅ Database schema check: 6/6 tables PASSED
✅ Core module check: 4/4 modules PASSED
✅ Deployment docs check: PASSED
✅ Code structure check: 4/4 features PASSED
✅ Risk module check: 4/4 features PASSED
✅ Backtest engine check: 4/4 features PASSED

Status: ready_for_config
```

---

## 🚀 Deployment Process

### For Future Agents: Deployment Steps

1. **Environment Setup**:
   ```bash
   # User configures .env with their credentials
   python setup_auto.py  # Interactive configuration wizard
   ```

2. **Database Initialization**:
   ```sql
   -- Run in Supabase SQL Editor
   \i init_db.sql
   ```

3. **Dependency Installation**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Testing**:
   ```bash
   python test_core_minimal.py
   ```

5. **Data Pipeline**:
   ```bash
   python run_data_pipeline.py
   ```

6. **Paper Trading** (30+ days recommended):
   ```bash
   MODE=paper python -m strategy_manager.runner
   ```

7. **Dashboard**:
   ```bash
   streamlit run dashboard/app.py
   ```

8. **Production Deployment**:
   - Vercel: Frontend hosting
   - Railway/Render: Trading bot hosting
   - Supabase: Database

---

## 📝 Key Design Decisions

### 1. Credal Transformer over Standard Transformer
**Rationale**: Reduces hallucination by quantifying uncertainty. High uncertainty → abstain from trading.

### 2. Paper Trading First
**Rationale**: Safety for low-capital users. Validate strategy before risking real money.

### 3. Supabase over Local PostgreSQL
**Rationale**: Cloud-native, free tier sufficient, easy Vercel integration.

### 4. 1% Risk Rule
**Rationale**: Conservative approach for meme coin volatility. Protects capital during drawdowns.

### 5. Japan Tax Integration
**Rationale**: User is Japan-based. Automatic compliance reduces legal risk.

---

## 🔄 Secondary Development Guide

### For Future Agents

**To extend this project**:

1. **Read this log first** - Understand architecture and decisions
2. **Check TASK_STATUS.md** - See what was completed
3. **Review code structure** - Follow existing patterns
4. **Use setup_auto.py** - For environment configuration
5. **Test with test_core_minimal.py** - Validate changes

**Key Files to Understand**:
- `credal_transformer.py` - Core ML model
- `backtest/engine.py` - Validation framework
- `risk_enhanced.py` - Risk controls
- `paper_trader.py` - Safe testing

**Extension Points**:
- Add new operators in `FactorGenerator`
- Add new risk rules in `RiskEngine`
- Add new backtest metrics in `BacktestEngine`
- Add new data sources in `data_pipeline/`

---

## 🐛 Known Limitations

1. **PyTorch Dependency**: Heavy dependency, may need optimization for edge deployment
2. **Birdeye API Limits**: Free tier 30k requests/month - may need rate limiting for high-frequency
3. **Solana RPC**: Public RPC may be rate-limited - consider QuickNode/Alchemy for production
4. **Paper Trading**: Simplified price simulation - not 100% accurate to real market

---

## 📚 References

- **Original Project**: https://github.com/imbue-bit/AlphaGPT
- **Credal Transformer Paper**: arXiv 2510.12137
- **Supabase**: https://supabase.com
- **Birdeye API**: https://birdeye.so
- **Jupiter Aggregator**: https://jup.ag

---

## 🎯 Success Metrics

| Metric | Target | Status |
|--------|--------|--------|
| Win Rate | > 55% | Pending paper trading validation |
| Sharpe Ratio | > 1.5 | Pending paper trading validation |
| Max Drawdown | < 20% | Risk controls implemented |
| Code Coverage | Core modules | 4/4 modules tested |
| Documentation | Complete | EN/CN bilingual |

---

**End of Development Log**

*Generated by Claude Code Multi-Agent Team*
*Date: 2026-02-20*

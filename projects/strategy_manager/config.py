class StrategyConfig:
    # 仓位管理（适配 0.32 SOL 小资金）
    MAX_OPEN_POSITIONS = 2          # 最多同时持有 2 个仓位
    ENTRY_AMOUNT_SOL = 0.1          # 每次买入 0.1 SOL（保留费用）
    
    # 止损止盈
    STOP_LOSS_PCT = -0.15           # 止损 -15%（meme币波动大）
    TAKE_PROFIT_Target1 = 0.30      # 止盈 +30%
    TP_Target1_Ratio = 0.5          # 止盈卖出 50%
    
    # 移动止损
    TRAILING_ACTIVATION = 0.15      # 盈利 15% 后激活
    TRAILING_DROP = 0.10            # 回撤 10% 触发卖出
    
    # AI 信号阈值
    BUY_THRESHOLD = 0.80            # 买入信号阈值（0-1）
    SELL_THRESHOLD = 0.40           # 卖出信号阈值（0-1）
    
    # 扫描间隔
    SCAN_INTERVAL_SECONDS = 60      # 扫描间隔（秒）
    DATA_SYNC_INTERVAL_SECONDS = 900  # 数据同步间隔（15分钟）

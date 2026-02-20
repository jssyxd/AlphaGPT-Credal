#!/bin/bash
# AlphaGPT 启动脚本

set -e

echo "=========================================="
echo "  AlphaGPT Trading Bot - 启动脚本"
echo "=========================================="

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo "❌ 错误: .env 文件不存在"
    echo "请先创建 .env 文件并配置所有必要的环境变量"
    exit 1
fi

# 检查策略文件
if [ ! -f "best_meme_strategy.json" ]; then
    echo "⚠️  警告: best_meme_strategy.json 不存在，使用默认策略"
fi

# 创建必要的目录
mkdir -p data logs

# 激活虚拟环境（如果存在）
if [ -d "venv" ]; then
    echo "激活虚拟环境..."
    source venv/bin/activate
fi

# 显示配置信息
echo ""
echo "📋 配置信息:"
echo "  - 模式: $(grep MODE .env | cut -d'=' -f2)"
echo "  - 数据库: $(grep DB_HOST .env | cut -d'=' -f2)"
echo "  - RPC: $(grep SOLANA_RPC .env | cut -d'=' -f2)"
echo ""

# 启动交易机器人
echo "🚀 启动 AlphaGPT 交易机器人..."
python -m strategy_manager.runner

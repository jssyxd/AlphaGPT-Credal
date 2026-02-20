import torch
import os
from dotenv import load_dotenv

load_dotenv()

class ModelConfig:
    DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # 数据库配置（使用 Supabase）
    DB_URL = f"postgresql://{os.getenv('DB_USER','postgres')}:{os.getenv('DB_PASSWORD','password')}@{os.getenv('DB_HOST','localhost')}:{os.getenv('DB_PORT','5432')}/{os.getenv('DB_NAME','postgres')}"
    
    # 训练配置
    BATCH_SIZE = 4096
    TRAIN_STEPS = 500
    MAX_FORMULA_LEN = 10
    
    # 交易配置
    TRADE_SIZE_USD = 15.0          # 约 0.1 SOL
    MIN_LIQUIDITY = 30000.0        # 最低流动性 $30k
    BASE_FEE = 0.01                # 基础费率 1%（Solana 很低）
    INPUT_DIM = 6
    
    # 运行模式
    MODE = os.getenv("MODE", "paper")

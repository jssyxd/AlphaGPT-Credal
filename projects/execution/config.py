import os
from dotenv import load_dotenv
from solders.keypair import Keypair
import base58

load_dotenv()

class ExecutionConfig:
    # RPC 配置
    RPC_URL = os.getenv("SOLANA_RPC", "https://api.mainnet-beta.solana.com")
    
    # 私钥配置
    _PRIV_KEY_STR = os.getenv("SOLANA_PRIVATE_KEY", "")

    if not _PRIV_KEY_STR:
        raise ValueError("Missing SOLANA_PRIVATE_KEY in .env")
    
    try:
        # 尝试 Base58 格式
        PAYER_KEYPAIR = Keypair.from_base58_string(_PRIV_KEY_STR)
    except Exception:
        # 尝试 JSON 数组格式
        import json
        PAYER_KEYPAIR = Keypair.from_bytes(json.loads(_PRIV_KEY_STR))

    WALLET_ADDRESS = str(PAYER_KEYPAIR.pubkey())

    # 交易配置
    DEFAULT_SLIPPAGE_BPS = 500  # 5% 滑点（meme币波动大）
    PRIORITY_LEVEL = "High" 
    
    # 代币地址
    SOL_MINT = "So11111111111111111111111111111111111111112"
    USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
    
    # 运行模式
    MODE = os.getenv("MODE", "paper")
    IS_PAPER_MODE = MODE == "paper"

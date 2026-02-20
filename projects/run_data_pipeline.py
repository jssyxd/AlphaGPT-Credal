#!/usr/bin/env python3
"""
AlphaGPT 数据拉取脚本
从 Birdeye API 拉取 Solana meme 币数据并存入 Supabase
"""
import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from loguru import logger
from data_pipeline.data_manager import DataManager
from data_pipeline.db_manager import DBManager

load_dotenv()


async def main():
    logger.info("=" * 50)
    logger.info("AlphaGPT 数据管线启动")
    logger.info("=" * 50)
    
    # 检查环境变量
    required_vars = ['DB_HOST', 'DB_PASSWORD', 'BIRDEYE_API_KEY']
    missing = [v for v in required_vars if not os.getenv(v)]
    if missing:
        logger.error(f"缺少必要的环境变量: {missing}")
        logger.info("请在 .env 文件中配置以下变量:")
        for v in missing:
            logger.info(f"  - {v}")
        return
    
    # 初始化数据库管理器
    db = DBManager()
    try:
        logger.info("连接数据库...")
        await db.connect()
        
        logger.info("初始化数据库表结构...")
        await db.init_schema()
        
        # 初始化数据管理器
        data_mgr = DataManager()
        
        logger.info("开始拉取数据...")
        await data_mgr.pipeline_sync_daily()
        
        logger.success("数据同步完成！")
        
    except Exception as e:
        logger.exception(f"数据拉取失败: {e}")
    finally:
        await db.close()


if __name__ == "__main__":
    asyncio.run(main())

"""
AlphaGPT 数据库连接测试脚本
运行此脚本验证 Supabase 连接
"""
import asyncio
import asyncpg
from dotenv import load_dotenv
import os

load_dotenv()

async def test_connection():
    print("=" * 50)
    print("AlphaGPT Supabase 连接测试")
    print("=" * 50)
    
    # 显示配置信息
    print(f"\n数据库主机: {os.getenv('DB_HOST')}")
    print(f"数据库端口: {os.getenv('DB_PORT')}")
    print(f"数据库名称: {os.getenv('DB_NAME')}")
    print(f"数据库用户: {os.getenv('DB_USER')}")
    
    dsn = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    
    try:
        print("\n正在连接数据库...")
        pool = await asyncpg.create_pool(dsn=dsn, ssl='require')
        print("✅ 数据库连接成功！")
        
        async with pool.acquire() as conn:
            # 检查表是否存在
            tables = await conn.fetch("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            print(f"\n📊 已创建的表: {[t['table_name'] for t in tables]}")
            
            # 检查 ohlcv 数据量
            if any(t['table_name'] == 'ohlcv' for t in tables):
                count = await conn.fetchval("SELECT COUNT(*) FROM ohlcv")
                print(f"📈 OHLCV 数据条数: {count}")
        
        await pool.close()
        print("\n✅ 所有测试通过！")
        return True
        
    except Exception as e:
        print(f"\n❌ 连接失败: {e}")
        print("\n请检查:")
        print("1. DB_HOST 是否正确（应为 db.xxx.supabase.co）")
        print("2. DB_PASSWORD 是否正确（需要在 Supabase 控制台获取）")
        print("3. 是否已运行 init_db.sql 创建表结构")
        return False

if __name__ == "__main__":
    asyncio.run(test_connection())

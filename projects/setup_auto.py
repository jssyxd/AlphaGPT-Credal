#!/usr/bin/env python3
"""
AlphaGPT 自动化配置脚本
帮助用户快速完成环境配置
"""

import os
import json
from pathlib import Path

print("=" * 60)
print("AlphaGPT 自动化配置向导")
print("=" * 60)

# 读取现有.env（如果有）
env_path = Path('.env')
env_vars = {}

if env_path.exists():
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key] = value

print("\n请提供以下配置信息（按Enter跳过保持当前值）：\n")

# 配置项列表
configs = [
    ('SUPABASE_URL', 'Supabase项目URL', 'https://xxxxx.supabase.co'),
    ('SUPABASE_ANON_KEY', 'Supabase Anon Key', 'eyJ...'),
    ('SUPABASE_SERVICE_KEY', 'Supabase Service Role Key (可选)', 'eyJ...'),
    ('DB_HOST', '数据库主机', 'db.xxxxx.supabase.co'),
    ('DB_PASSWORD', '数据库密码', 'your-password'),
    ('BIRDEYE_API_KEY', 'Birdeye API Key', 'your-api-key'),
    ('WALLET_PRIVATE_KEY', 'Solana钱包私钥 (base58)', 'your-private-key'),
]

new_values = {}

for key, description, default in configs:
    current = env_vars.get(key, '')
    if '密码' in description or '私钥' in description:
        display_current = '*' * len(current) if current else '未设置'
    else:
        display_current = current if current else '未设置'

    print(f"{description}:")
    print(f"  当前值: {display_current}")
    value = input(f"  新值 (按Enter保持不变): ").strip()

    if value:
        new_values[key] = value
        print(f"  ✅ 已更新")
    else:
        print(f"  ⏭️  保持不变")
    print()

# 更新.env文件
if new_values:
    env_lines = []
    with open(env_path, 'r') as f:
        env_content = f.read()

    # 更新现有变量
    for line in env_content.split('\n'):
        if line.startswith('#') or '=' not in line:
            env_lines.append(line)
        else:
            key = line.split('=')[0]
            if key in new_values:
                env_lines.append(f"{key}={new_values[key]}")
            else:
                env_lines.append(line)

    # 写入文件
    with open(env_path, 'w') as f:
        f.write('\n'.join(env_lines))

    print("✅ .env文件已更新")
else:
    print("⏭️  .env文件未更改")

# 生成配置摘要
print("\n" + "=" * 60)
print("配置摘要")
print("=" * 60)

required_configs = ['SUPABASE_URL', 'BIRDEYE_API_KEY', 'WALLET_PRIVATE_KEY']
missing = []

with open(env_path, 'r') as f:
    env_content = f.read()

for key in required_configs:
    if key in env_content and '你的' not in env_content and 'your' not in env_content.lower():
        print(f"✅ {key}: 已配置")
    else:
        print(f"❌ {key}: 未配置")
        missing.append(key)

if missing:
    print("\n⚠️  以下配置项尚未完成:")
    for key in missing:
        print(f"   - {key}")
    print("\n请编辑 .env 文件完成配置")
else:
    print("\n🎉 所有必需配置已完成！")
    print("\n下一步:")
    print("1. 在Supabase SQL Editor中运行: init_db.sql")
    print("2. 安装依赖: pip install -r requirements.txt")
    print("3. 运行测试: python run_data_pipeline.py")

# 保存配置状态
config_status = {
    "setup_completed": len(missing) == 0,
    "missing_configs": missing,
    "timestamp": str(os.path.getmtime(env_path))
}

with open('config_status.json', 'w') as f:
    json.dump(config_status, f, indent=2)

print("\n📄 配置状态已保存到 config_status.json")

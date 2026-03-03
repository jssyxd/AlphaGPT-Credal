"""
AlphaGPT Data Pipeline - Strategy Storage
Stores and retrieves LLM-generated trading strategies/factors
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, List, Optional
from data_pipeline.db import get_db_manager


def save_strategy(strategy: Dict) -> Dict:
    """Save a new strategy to database"""
    db = get_db_manager()
    supabase = db.supabase

    data = {
        "name": strategy.get("name"),
        "description": strategy.get("reasons", ""),
        "formula": strategy.get("formula"),
        "formula_json": {
            "raw": strategy.get("formula"),
            "metrics": strategy.get("metrics", [])
        },
        "score": strategy.get("score", 0),
        "uncertainty": strategy.get("uncertainty", 1.0),
        "status": "active",
        "created_at": "now()",
        "updated_at": "now()"
    }

    response = supabase.table("strategies").insert(data).execute()

    if response.data:
        return response.data[0]
    return {}


def get_active_strategies(limit: int = 10) -> List[Dict]:
    """Get active strategies ordered by score"""
    db = get_db_manager()
    supabase = db.supabase

    response = supabase.table("strategies").select("*").eq("status", "active").order("score", desc=True).limit(limit).execute()

    return response.data


def get_strategy_by_id(strategy_id: int) -> Optional[Dict]:
    """Get strategy by ID"""
    db = get_db_manager()
    supabase = db.supabase

    response = supabase.table("strategies").select("*").eq("id", strategy_id).execute()

    if response.data:
        return response.data[0]
    return None


def update_strategy_status(strategy_id: int, status: str) -> bool:
    """Update strategy status"""
    db = get_db_manager()
    supabase = db.supabase

    response = supabase.table("strategies").update({"status": status, "updated_at": "now()"}).eq("id", strategy_id).execute()

    return len(response.data) > 0


def archive_strategy(strategy_id: int) -> bool:
    """Archive a strategy"""
    return update_strategy_status(strategy_id, "archived")


def save_llm_log(prompt: str, response: str, model: str, tokens_used: int, cost: float, status: str = "success", error: str = None):
    """Save LLM API call log"""
    db = get_db_manager()
    supabase = db.supabase

    data = {
        "prompt": prompt,
        "response": response,
        "model": model,
        "tokens_used": tokens_used,
        "cost": cost,
        "status": status,
        "error": error
    }

    supabase.table("llm_logs").insert(data).execute()

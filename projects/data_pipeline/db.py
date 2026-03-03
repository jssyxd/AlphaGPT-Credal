"""
AlphaGPT Data Pipeline Database Module
"""
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()


class DatabaseManager:
    """Database manager for Supabase operations"""

    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_ANON_KEY")
        self.client: Client = None

    def connect(self):
        """Connect to Supabase"""
        if not self.client:
            if not self.supabase_url or not self.supabase_key:
                raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set in environment")
            self.client = create_client(self.supabase_url, self.supabase_key)
        return self.client

    @property
    def supabase(self):
        """Get Supabase client"""
        return self.connect()

    def get_settings(self):
        """Get all settings as dict"""
        response = self.supabase.table("settings").select("key, value").execute()
        return {row["key"]: row["value"] for row in response.data}

    def get_setting(self, key: str, default=None):
        """Get single setting"""
        response = self.supabase.table("settings").select("value").eq("key", key).execute()
        if response.data:
            return response.data[0]["value"]
        return default

    def set_setting(self, key: str, value: str):
        """Set a setting"""
        self.supabase.table("settings").upsert({"key": key, "value": value}).execute()

    def get_mode(self) -> str:
        """Get current trading mode (paper or live)"""
        return self.get_setting("mode", "paper")

    def is_paper_mode(self) -> bool:
        """Check if running in paper trading mode"""
        return self.get_mode() == "paper"


# Singleton
_db_manager = None


def get_db_manager() -> DatabaseManager:
    """Get database manager singleton"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager

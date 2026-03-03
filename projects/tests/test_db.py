"""
Tests for database module
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from unittest.mock import Mock, patch, MagicMock


def test_db_manager_init():
    """Test DatabaseManager initialization"""
    from data_pipeline.db import DatabaseManager

    with patch.dict('os.environ', {
        'SUPABASE_URL': 'https://test.supabase.co',
        'SUPABASE_ANON_KEY': 'test-key'
    }):
        db = DatabaseManager()
        assert db.supabase_url == 'https://test.supabase.co'
        assert db.supabase_key == 'test-key'


def test_get_db_manager_singleton():
    """Test get_db_manager returns singleton"""
    from data_pipeline.db import get_db_manager, DatabaseManager

    # Reset singleton for test
    import data_pipeline.db
    data_pipeline.db._db_manager = None

    with patch.dict('os.environ', {
        'SUPABASE_URL': 'https://test.supabase.co',
        'SUPABASE_ANON_KEY': 'test-key'
    }):
        db1 = get_db_manager()
        db2 = get_db_manager()
        assert db1 is db2
        assert isinstance(db1, DatabaseManager)


def test_get_mode_default():
    """Test get_mode returns paper by default"""
    from data_pipeline.db import DatabaseManager

    # Build proper mock chain
    mock_execute = MagicMock()
    mock_execute.data = [{"value": "paper"}]

    mock_select = MagicMock()
    mock_select.execute.return_value = mock_execute
    mock_select.eq.return_value = mock_select

    mock_table = MagicMock()
    mock_table.select.return_value = mock_select

    mock_client = MagicMock()
    mock_client.table.return_value = mock_table

    with patch.dict('os.environ', {
        'SUPABASE_URL': 'https://test.supabase.co',
        'SUPABASE_ANON_KEY': 'test-key'
    }):
        with patch('data_pipeline.db.create_client', return_value=mock_client):
            db = DatabaseManager()
            db.client = mock_client
            mode = db.get_mode()
            assert mode == "paper"


def test_is_paper_mode():
    """Test is_paper_mode returns correct value"""
    from data_pipeline.db import DatabaseManager

    # Build proper mock chain
    mock_execute = MagicMock()
    mock_execute.data = [{"value": "paper"}]

    mock_select = MagicMock()
    mock_select.execute.return_value = mock_execute
    mock_select.eq.return_value = mock_select

    mock_table = MagicMock()
    mock_table.select.return_value = mock_select

    mock_client = MagicMock()
    mock_client.table.return_value = mock_table

    with patch.dict('os.environ', {
        'SUPABASE_URL': 'https://test.supabase.co',
        'SUPABASE_ANON_KEY': 'test-key'
    }):
        with patch('data_pipeline.db.create_client', return_value=mock_client):
            db = DatabaseManager()
            db.client = mock_client
            assert db.is_paper_mode() is True


def test_get_setting_default():
    """Test get_setting returns default when not found"""
    from data_pipeline.db import DatabaseManager

    # Build proper mock chain with empty data
    mock_execute = MagicMock()
    mock_execute.data = []

    mock_select = MagicMock()
    mock_select.execute.return_value = mock_execute
    mock_select.eq.return_value = mock_select

    mock_table = MagicMock()
    mock_table.select.return_value = mock_select

    mock_client = MagicMock()
    mock_client.table.return_value = mock_table

    with patch.dict('os.environ', {
        'SUPABASE_URL': 'https://test.supabase.co',
        'SUPABASE_ANON_KEY': 'test-key'
    }):
        with patch('data_pipeline.db.create_client', return_value=mock_client):
            db = DatabaseManager()
            db.client = mock_client
            value = db.get_setting("nonexistent", "default_value")
            assert value == "default_value"


def test_set_setting():
    """Test set_setting calls upsert"""
    from data_pipeline.db import DatabaseManager

    mock_table = MagicMock()
    mock_client = MagicMock()
    mock_client.table.return_value = mock_table

    with patch.dict('os.environ', {
        'SUPABASE_URL': 'https://test.supabase.co',
        'SUPABASE_ANON_KEY': 'test-key'
    }):
        with patch('data_pipeline.db.create_client', return_value=mock_client):
            db = DatabaseManager()
            db.client = mock_client
            db.set_setting("test_key", "test_value")

            # Verify upsert was called
            mock_table.upsert.assert_called_once()
            call_args = mock_table.upsert.call_args
            assert call_args[0][0] == {"key": "test_key", "value": "test_value"}

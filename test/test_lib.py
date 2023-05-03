import os
from unittest.mock import patch, MagicMock

import pytest
import asyncpg

from postgresgpt.lib import create_pool, get_schema, gpt_tables, gpt
import openai


@pytest.fixture
def mock_dsn(monkeypatch):
    monkeypatch.setenv('DATABASE_URL', 'postgres://user:password@localhost:5432/dbname')


@pytest.mark.asyncio
async def test_create_pool_success(mock_dsn):
    with patch('asyncpg.create_pool') as mock_create_pool:
        mock_create_pool.return_value = 'mock pool'
        pool = await create_pool()
        assert pool == 'mock pool'
        mock_create_pool.assert_called_once_with('postgres://user:password@localhost:5432/dbname')


@pytest.mark.asyncio
async def test_create_pool_failure(mock_dsn):
    with patch('asyncpg.create_pool') as mock_create_pool:
        mock_create_pool.side_effect = asyncpg.exceptions.PostgresConnectionError('Unable to connect to database')
        with pytest.raises(asyncpg.exceptions.PostgresConnectionError):
            await create_pool()
        mock_create_pool.assert_called_once_with('postgres://user:password@localhost:5432/dbname')
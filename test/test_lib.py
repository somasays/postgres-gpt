import os
from unittest.mock import patch, MagicMock

import pytest
import asyncpg

from postgresgpt.lib import create_pool, get_schema, gpt_tables, gpt


@pytest.mark.asyncio
async def test_create_pool():
    pool = await create_pool()
    assert isinstance(pool, asyncpg.pool.Pool)


@pytest.mark.asyncio
async def test_get_schema():
    pool = MagicMock()
    pool.fetchval.return_value = '{"table_name": {"column_name": "data_type"}}'
    schema = await get_schema(pool, 'my_table')
    assert schema == '{"table_name": {"column_name": "data_type"}}'


@pytest.mark.asyncio
async def test_get_schema_error():
    pool = MagicMock()
    pool.fetchval.side_effect = asyncpg.exceptions.UndefinedTableError('Table does not exist')
    schema = await get_schema(pool, 'my_table')
    assert schema is None


@pytest.mark.asyncio
async def test_gpt_tables():
    openai.api_key = 'mock_key'
    with patch('asyncpg.create_pool') as create_pool_mock, \
            patch('asyncpg.pool.Pool.acquire') as acquire_mock, \
            patch('openai.ChatCompletion.create') as chat_completion_mock:
        # Mock the database connection and schema query
        conn_mock = MagicMock()
        conn_mock.fetchval.return_value = '{"table_name": {"column_name": "data_type"}}'
        acquire_mock.return_value.__aenter__.return_value = conn_mock
        create_pool_mock.return_value = MagicMock()

        # Mock the OpenAI API response
        message_mock = MagicMock()
        message_mock.choices[0].message.content = 'SELECT * FROM my_table;'
        chat_completion_mock.return_value = message_mock

        result = await gpt_tables('my_table', 'What is the average value of column_name?')
        assert result == 'SELECT * FROM my_table;'


@pytest.mark.asyncio
async def test_gpt():
    openai.api_key = 'mock_key'
    with patch('my_module.gpt_tables') as gpt_tables_mock:
        gpt_tables_mock.return_value = 'SELECT * FROM my_table;'
        result = await gpt('What is the average value of column_name?')
        assert result == 'SELECT * FROM my_table;'

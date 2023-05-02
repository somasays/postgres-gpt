import os
import json
import asyncio
from typing import Optional

import asyncpg
from asyncpg.pool import Pool
from asyncpg.exceptions import UndefinedTableError, InvalidTableDefinitionError
import openai


async def create_pool() -> Pool:
    dsn = os.environ.get('DATABASE_URL')
    return await asyncpg.create_pool(dsn)


async def get_schema(pool: Pool, table_pattern: str) -> Optional[str]:
    sql = f"""SELECT json_object_agg(table_name, columns)::text
              FROM (
                SELECT table_name, json_object_agg(column_name, data_type) AS columns
                FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name LIKE '{table_pattern}' AND table_name NOT LIKE '_pg%'
                GROUP BY table_name
              ) subquery;"""
    try:
        async with pool.acquire() as conn:
            schema = await conn.fetchval(sql)
            if schema is None:
                raise ValueError("No result")
            if len(schema) > 10000:
                # If results are too long, take out the data types
                sql = f"""SELECT json_object_agg(table_name, columns)::text
                          FROM (
                            SELECT table_name, json_agg(column_name) AS columns
                            FROM information_schema.columns
                            WHERE table_schema = 'public' AND table_name LIKE '{table_pattern}' AND table_name NOT LIKE '_pg%'
                            GROUP BY table_name
                          ) subquery;"""
                schema = await conn.fetchval(sql)
                if schema is None:
                    raise ValueError("No result")
            return schema
    except (UndefinedTableError, InvalidTableDefinitionError):
        return None


async def gpt_tables(table_pattern: str, input_str: str) -> str:
    openai_key = os.environ.get('OPENAI_KEY')
    if openai_key is not None:
        openai.api_key = openai_key
    else:
        open_ai_key_sql = "SELECT current_setting('openai.key');"
        async with create_pool() as pool:
            open_ai_key = await pool.fetchval(open_ai_key_sql)
            if open_ai_key is None:
                raise ValueError("openai.key not set")
            openai.api_key = openai_key
    schema = await get_schema(create_pool(), table_pattern)
    chat_completion = await openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a SQL assistant that helps translate questions into SQL.", "name": None},
            {"role": "user", "content": f"Here is a schema for the database in json format: {schema}", "name": None},
            {"role": "user", "content": f"Please return an SQL statement as a single string for the following question. You must respond ONLY with SQL, nothing else. Do NOT use any tables other than the ones provided. The question is: {input_str}", "name": None},
        ]
    )
    returned_message = chat_completion.choices[0].message
    return returned_message.content


async def gpt(input_str: str) -> str:
    return await gpt_tables("%", input_str)

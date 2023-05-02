# PostgresGPT

PostgresGPT is a Python library that enables the creation of SQL queries from natural language for PostgreSQL databases. It uses OpenAI's GPT-3.5 language model to understand the natural language and convert it to SQL statements.

## Installation

You can install PostgresGPT using pip:

```bash
pip install postgresgpt
```

## Usage

PostgresGPT consists of a single function, `gpt`, that takes a natural language query as input and returns a SQL statement as output.

```python
import postgresgpt

result = await postgresgpt.gpt('What are the top 10 most viewed posts in the last week?')
```

The above example will return the following SQL statement:

```sql
SELECT *
FROM posts
WHERE created_at > now() - interval '1 week'
ORDER BY views DESC
LIMIT 10;
```

You can also pass a table pattern to `gpt_tables` function to search for the schema in a specific table:

```python
result = await postgresgpt.gpt_tables('hackernews_%', 'list top HN stories for the past week that had something to do with ChatGPT. Show only the score and title.')
```

## Technical Details

PostgresGPT uses the `asyncpg` library to connect to a PostgreSQL database and the `openai` library to interact with the GPT-3.5 language model. It supports Python 3.6 and higher.

To test the library, we use `pytest` and `unittest.mock`. We also use `tox` to test against multiple Python versions.

## Contributing

If you'd like to contribute to PostgresGPT, please feel free to open an issue or a pull request on the GitHub repository: https://github.com/username/postgresgpt

## License

PostgresGPT is licensed under the MIT License. See the LICENSE file for more information.
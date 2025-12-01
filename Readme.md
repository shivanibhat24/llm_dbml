# LLM-DBML: Natural Language to Database Schema Compiler

Convert natural language descriptions into complete database schemas with DBML, SQL migrations, test data, and visualizations.

## Features

- 🗣️ **Natural Language Parsing**: Describe your database schema in plain English
- 📊 **DBML Export**: Generate industry-standard DBML format
- 🔄 **SQL Migrations**: Create DDL statements for PostgreSQL, MySQL, SQLite
- 🧪 **Test Data Generation**: Automatic realistic test data
- 📈 **Visualizations**: ASCII, Mermaid, and HTML table diagrams
- ✅ **Schema Validation**: Verify referential integrity and constraints

## Installation

```bash
pip install llm-dbml
```

## Quick Start

```python
from llm_dbml import DBSchemaCompiler

# Create compiler instance
compiler = DBSchemaCompiler()

# Define your schema in natural language
nl_description = """
Create a users table with username, email, and created_at timestamp.
Create a posts table with title, content text, and published_at.
Posts belongs to users.
"""

# Compile the schema
compiler.compile(nl_description, schema_name="blog_db")

# Validate the schema
is_valid, errors = compiler.validate()
print(f"Valid: {is_valid}")

# Export to DBML
print(compiler.to_dbml())

# Generate SQL migration
print(compiler.generate_migration("postgresql"))

# Generate test data
data = compiler.generate_test_data(num_rows=5)
print(data)

# Visualize
print(compiler.visualize_ascii())
```

## Supported Data Types

- `integer`, `bigint`, `number`
- `string`, `varchar`, `text`
- `boolean`, `bool`, `flag`
- `date`, `datetime`, `timestamp`
- `decimal`, `money`, `price`, `float`
- `json`, `uuid`

## Natural Language Examples

### Simple Table
```python
"Create a products table with name, price decimal, and description text."
```

### Relationships
```python
"""
Create a users table with username and email.
Create a orders table with total_amount and order_date.
Orders belongs to users.
"""
```

### Complex Schema
```python
"""
Create a users table with username string required, email string, 
password_hash text, and is_active boolean.

Create a categories table with name string and slug string unique.

Create a posts table with title string, content text, 
published_at timestamp, and view_count integer.
Posts belongs to users.
Posts belongs to categories.
"""
```

## API Reference

### DBSchemaCompiler

Main compiler class for natural language to schema conversion.

**Methods:**

- `compile(nl_description: str, schema_name: str = "database")` - Compile NL to schema
- `load_schema(schema: Schema)` - Load existing schema object
- `to_dbml() -> str` - Export to DBML format
- `validate() -> Tuple[bool, List[str]]` - Validate schema integrity
- `generate_migration(dialect: str = "postgresql") -> str` - Generate SQL
- `generate_test_data(num_rows: int = 10) -> Dict` - Generate test data
- `visualize_ascii() -> str` - ASCII ERD visualization
- `visualize_mermaid() -> str` - Mermaid diagram code
- `visualize_html() -> str` - HTML table visualization
- `get_schema() -> Schema` - Get schema object
- `summary() -> Dict` - Get schema statistics

## Manual Schema Construction

You can also build schemas programmatically:

```python
from llm_dbml import Schema, Table, Column, DataType, Relationship, RelationType

schema = Schema("my_database")

# Create users table
users = Table("users")
users.add_column(Column("id", DataType.INTEGER, primary_key=True, nullable=False))
users.add_column(Column("username", DataType.VARCHAR, length=50, nullable=False))
users.add_column(Column("email", DataType.VARCHAR, length=255))

schema.add_table(users)

# Use with compiler
compiler = DBSchemaCompiler()
compiler.load_schema(schema)
```

## Testing

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=llm_dbml --cov-report=html
```

## Development

```bash
# Clone repository
git clone https://github.com/yourusername/llm-dbml.git
cd llm-dbml

# Install in editable mode
pip install -e ".[dev]"

# Format code
black llm_dbml tests

# Type checking
mypy llm_dbml
```

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

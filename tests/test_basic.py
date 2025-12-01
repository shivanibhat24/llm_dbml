"""Basic tests for llm_dbml"""

import pytest
from llm_dbml import DBSchemaCompiler, Schema, Table, Column, DataType


def test_compiler_initialization():
    """Test compiler initialization"""
    compiler = DBSchemaCompiler()
    assert compiler.schema is None


def test_simple_compilation():
    """Test basic natural language compilation"""
    compiler = DBSchemaCompiler()
    
    nl = """
    Create a users table with name, email, and age.
    Create a posts table with title and content.
    Posts references users.
    """
    
    compiler.compile(nl, "blog_db")
    
    assert compiler.schema is not None
    assert compiler.schema.name == "blog_db"
    assert "users" in compiler.schema.tables
    assert "posts" in compiler.schema.tables


def test_validation():
    """Test schema validation"""
    compiler = DBSchemaCompiler()
    
    nl = "Create a users table with name and email."
    compiler.compile(nl)
    
    is_valid, errors = compiler.validate()
    assert is_valid
    assert len(errors) == 0


def test_dbml_export():
    """Test DBML export"""
    compiler = DBSchemaCompiler()
    
    nl = "Create a users table with name string and email string."
    compiler.compile(nl)
    
    dbml = compiler.to_dbml()
    assert "Table users" in dbml
    assert "name" in dbml
    assert "email" in dbml


def test_sql_generation():
    """Test SQL migration generation"""
    compiler = DBSchemaCompiler()
    
    nl = "Create a products table with name, price decimal, and description text."
    compiler.compile(nl)
    
    sql = compiler.generate_migration("postgresql")
    assert "CREATE TABLE products" in sql
    assert "name" in sql
    assert "price" in sql


def test_test_data_generation():
    """Test data generation"""
    compiler = DBSchemaCompiler()
    
    nl = "Create a users table with name and email."
    compiler.compile(nl)
    
    data = compiler.generate_test_data(num_rows=5)
    assert "users" in data
    assert len(data["users"]) == 5
    assert all("name" in row for row in data["users"])


def test_summary():
    """Test schema summary"""
    compiler = DBSchemaCompiler()
    
    nl = """
    Create a users table with name and email.
    Create a posts table with title.
    Posts references users.
    """
    compiler.compile(nl)
    
    summary = compiler.summary()
    assert summary["num_tables"] == 2
    assert "users" in summary["tables"]
    assert "posts" in summary["tables"]


def test_manual_schema_creation():
    """Test manual schema creation"""
    schema = Schema("test_db")
    
    users = Table("users")
    users.add_column(Column("id", DataType.INTEGER, primary_key=True, nullable=False))
    users.add_column(Column("name", DataType.VARCHAR, length=100))
    users.add_column(Column("email", DataType.VARCHAR, length=255))
    
    schema.add_table(users)
    
    compiler = DBSchemaCompiler()
    compiler.load_schema(schema)
    
    assert compiler.schema.name == "test_db"
    assert "users" in compiler.schema.tables


def test_relationship_parsing():
    """Test relationship detection"""
    compiler = DBSchemaCompiler()
    
    nl = """
    Create a users table.
    Create a orders table.
    Orders belongs to users.
    """
    compiler.compile(nl)
    
    assert len(compiler.schema.relationships) > 0
    rel = compiler.schema.relationships[0]
    assert rel.from_table == "orders"
    assert rel.to_table == "users"


def test_mermaid_visualization():
    """Test Mermaid diagram generation"""
    compiler = DBSchemaCompiler()
    
    nl = "Create a users table with name. Create a posts table. Posts references users."
    compiler.compile(nl)
    
    mermaid = compiler.visualize_mermaid()
    assert "erDiagram" in mermaid
    assert "users" in mermaid
    assert "posts" in mermaid


def test_ascii_visualization():
    """Test ASCII visualization"""
    compiler = DBSchemaCompiler()
    
    nl = "Create a products table with name and price."
    compiler.compile(nl)
    
    ascii_vis = compiler.visualize_ascii()
    assert "products" in ascii_vis
    assert "name" in ascii_vis


def test_complex_schema():
    """Test a more complex schema"""
    compiler = DBSchemaCompiler()
    
    nl = """
    Create a users table with username string required, email string, 
    created_at timestamp, and is_active boolean.
    
    Create a categories table with name string and description text.
    
    Create a posts table with title string, content text, 
    published_at timestamp, and view_count integer.
    Posts belongs to users.
    Posts belongs to categories.
    
    Create a comments table with content text and created_at timestamp.
    Comments belongs to users.
    Comments belongs to posts.
    """
    
    compiler.compile(nl, "blog_system")
    
    summary = compiler.summary()
    assert summary["num_tables"] == 4
    assert summary["num_relationships"] >= 4
    
    is_valid, errors = compiler.validate()
    assert is_valid, f"Validation errors: {errors}"


"""SQL Migration Generator"""

from typing import Dict, Callable
from .models import Schema, Table, Column, DataType


class MigrationGenerator:
    """Generate SQL migrations from schema"""
    
    @staticmethod
    def generate_sql(schema: Schema, dialect: str = "postgresql") -> str:
        """Generate SQL CREATE statements"""
        statements = []
        
        # Create tables
        for table in schema.tables.values():
            statements.append(MigrationGenerator._create_table_sql(table, dialect))
        
        # Create indexes for foreign keys
        for table in schema.tables.values():
            for col in table.columns:
                if col.references and not col.primary_key:
                    statements.append(
                        f"CREATE INDEX idx_{table.name}_{col.name} ON {table.name}({col.name});"
                    )
        
        return "\n\n".join(statements)
    
    @staticmethod
    def _create_table_sql(table: Table, dialect: str) -> str:
        """Generate CREATE TABLE statement"""
        lines = [f"CREATE TABLE {table.name} ("]
        
        col_defs = []
        for col in table.columns:
            col_def = f"  {col.name} {MigrationGenerator._sql_type(col, dialect)}"
            
            if col.primary_key:
                if dialect == "postgresql":
                    col_def = f"  {col.name} SERIAL PRIMARY KEY"
                else:
                    col_def += " PRIMARY KEY AUTO_INCREMENT"
            else:
                if not col.nullable:
                    col_def += " NOT NULL"
                if col.unique:
                    col_def += " UNIQUE"
                if col.default:
                    col_def += f" DEFAULT {col.default}"
                if col.references:
                    col_def += f" REFERENCES {col.references[0]}({col.references[1]})"
            
            col_defs.append(col_def)
        
        lines.append(",\n".join(col_defs))
        lines.append(");")
        
        return "\n".join(lines)
    
    @staticmethod
    def _sql_type(col: Column, dialect: str) -> str:
        """Convert data type to SQL type"""
        if col.primary_key and col.data_type == DataType.INTEGER:
            return "SERIAL" if dialect == "postgresql" else "INTEGER"
        
        type_map = {
            DataType.INTEGER: "INTEGER",
            DataType.BIGINT: "BIGINT",
            DataType.VARCHAR: f"VARCHAR({col.length or 255})",
            DataType.TEXT: "TEXT",
            DataType.BOOLEAN: "BOOLEAN" if dialect == "postgresql" else "TINYINT(1)",
            DataType.DATE: "DATE",
            DataType.DATETIME: "TIMESTAMP",
            DataType.TIMESTAMP: "TIMESTAMP",
            DataType.DECIMAL: "DECIMAL(10,2)",
            DataType.FLOAT: "FLOAT",
            DataType.JSON: "JSON" if dialect == "postgresql" else "TEXT",
            DataType.UUID: "UUID" if dialect == "postgresql" else "VARCHAR(36)",
        }
        return type_map.get(col.data_type, "TEXT")


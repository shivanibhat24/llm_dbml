"""Core data models for database schema representation"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Tuple, Dict


class DataType(Enum):
    """Supported database data types"""
    INTEGER = "integer"
    BIGINT = "bigint"
    VARCHAR = "varchar"
    TEXT = "text"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    TIMESTAMP = "timestamp"
    DECIMAL = "decimal"
    FLOAT = "float"
    JSON = "json"
    UUID = "uuid"


class RelationType(Enum):
    """Database relationship types"""
    ONE_TO_ONE = "1:1"
    ONE_TO_MANY = "1:n"
    MANY_TO_ONE = "n:1"
    MANY_TO_MANY = "n:m"


@dataclass
class Column:
    """Represents a database column"""
    name: str
    data_type: DataType
    nullable: bool = True
    primary_key: bool = False
    unique: bool = False
    default: Optional[str] = None
    length: Optional[int] = None
    references: Optional[Tuple[str, str]] = None  # (table, column)
    
    def to_dbml(self) -> str:
        """Convert column to DBML format"""
        parts = [self.name, self.data_type.value]
        
        if self.length:
            parts[1] = f"{self.data_type.value}({self.length})"
        
        attrs = []
        if self.primary_key:
            attrs.append("pk")
        if not self.nullable:
            attrs.append("not null")
        if self.unique:
            attrs.append("unique")
        if self.default:
            attrs.append(f"default: {self.default}")
        if self.references:
            attrs.append(f"ref: > {self.references[0]}.{self.references[1]}")
        
        if attrs:
            parts.append(f"[{', '.join(attrs)}]")
        
        return " ".join(parts)


@dataclass
class Table:
    """Represents a database table"""
    name: str
    columns: List[Column] = field(default_factory=list)
    note: Optional[str] = None
    
    def add_column(self, column: Column):
        """Add a column to the table"""
        self.columns.append(column)
    
    def get_primary_keys(self) -> List[Column]:
        """Get all primary key columns"""
        return [col for col in self.columns if col.primary_key]
    
    def get_column(self, name: str) -> Optional[Column]:
        """Get a column by name"""
        for col in self.columns:
            if col.name == name:
                return col
        return None
    
    def to_dbml(self) -> str:
        """Convert table to DBML format"""
        lines = [f"Table {self.name} {{"]
        for col in self.columns:
            lines.append(f"  {col.to_dbml()}")
        if self.note:
            lines.append(f"  Note: '{self.note}'")
        lines.append("}")
        return "\n".join(lines)


@dataclass
class Relationship:
    """Represents a relationship between tables"""
    from_table: str
    from_column: str
    to_table: str
    to_column: str
    rel_type: RelationType
    
    def to_dbml(self) -> str:
        """Convert relationship to DBML format"""
        return f"Ref: {self.from_table}.{self.from_column} {self.rel_type.value} {self.to_table}.{self.to_column}"


class Schema:
    """Represents a complete database schema"""
    
    def __init__(self, name: str = "database"):
        self.name = name
        self.tables: Dict[str, Table] = {}
        self.relationships: List[Relationship] = []
    
    def add_table(self, table: Table):
        """Add a table to the schema"""
        self.tables[table.name] = table
    
    def get_table(self, name: str) -> Optional[Table]:
        """Get a table by name"""
        return self.tables.get(name)
    
    def add_relationship(self, rel: Relationship):
        """Add a relationship"""
        self.relationships.append(rel)
    
    def to_dbml(self) -> str:
        """Convert entire schema to DBML"""
        lines = [f"// Database: {self.name}", ""]
        
        for table in self.tables.values():
            lines.append(table.to_dbml())
            lines.append("")
        
        if self.relationships:
            lines.append("// Relationships")
            for rel in self.relationships:
                lines.append(rel.to_dbml())
        
        return "\n".join(lines)
    
    def validate(self) -> List[str]:
        """Validate relational integrity"""
        errors = []
        
        # Check for tables without primary keys
        for table_name, table in self.tables.items():
            pks = table.get_primary_keys()
            if not pks:
                errors.append(f"Table '{table_name}' has no primary key")
        
        # Validate foreign key references
        for table_name, table in self.tables.items():
            for col in table.columns:
                if col.references:
                    ref_table, ref_col = col.references
                    if ref_table not in self.tables:
                        errors.append(
                            f"Table '{table_name}.{col.name}' references "
                            f"non-existent table '{ref_table}'"
                        )
                    elif ref_col not in [c.name for c in self.tables[ref_table].columns]:
                        errors.append(
                            f"Table '{table_name}.{col.name}' references "
                            f"non-existent column '{ref_table}.{ref_col}'"
                        )
        
        # Check for duplicate column names in tables
        for table_name, table in self.tables.items():
            col_names = [col.name for col in table.columns]
            duplicates = [name for name in col_names if col_names.count(name) > 1]
            if duplicates:
                errors.append(
                    f"Table '{table_name}' has duplicate column names: {set(duplicates)}"
                )
        
        # Validate relationship integrity
        for rel in self.relationships:
            if rel.from_table not in self.tables:
                errors.append(
                    f"Relationship references non-existent table '{rel.from_table}'"
                )
            if rel.to_table not in self.tables:
                errors.append(
                    f"Relationship references non-existent table '{rel.to_table}'"
                )
        
        return errors

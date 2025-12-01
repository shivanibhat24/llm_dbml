"""Main compiler interface"""

from typing import Tuple, List, Dict, Any, Optional
from .models import Schema
from .parser import NLParser
from .migration import MigrationGenerator
from .test_data import TestDataGenerator
from .visualizer import ERDVisualizer


class DBSchemaCompiler:
    """Main compiler interface for NL to Database Schema"""
    
    def __init__(self):
        self.schema: Optional[Schema] = None
    
    def compile(self, nl_description: str, schema_name: str = "database") -> 'DBSchemaCompiler':
        """
        Compile natural language to schema
        
        Args:
            nl_description: Natural language description of the schema
            schema_name: Name for the schema (default: "database")
            
        Returns:
            Self for method chaining
        """
        self.schema = NLParser.parse(nl_description)
        self.schema.name = schema_name
        return self
    
    def load_schema(self, schema: Schema) -> 'DBSchemaCompiler':
        """Load an existing schema object"""
        self.schema = schema
        return self
    
    def to_dbml(self) -> str:
        """Export to DBML format"""
        if not self.schema:
            raise ValueError("No schema compiled. Call compile() first.")
        return self.schema.to_dbml()
    
    def validate(self) -> Tuple[bool, List[str]]:
        """
        Validate schema integrity
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        if not self.schema:
            raise ValueError("No schema compiled. Call compile() first.")
        errors = self.schema.validate()
        return len(errors) == 0, errors
    
    def generate_migration(self, dialect: str = "postgresql") -> str:
        """
        Generate SQL migration
        
        Args:
            dialect: SQL dialect (postgresql, mysql, sqlite)
            
        Returns:
            SQL migration script
        """
        if not self.schema:
            raise ValueError("No schema compiled. Call compile() first.")
        return MigrationGenerator.generate_sql(self.schema, dialect)
    
    def generate_test_data(self, num_rows: int = 10) -> Dict[str, List[Dict[str, Any]]]:
        """
        Generate test data
        
        Args:
            num_rows: Number of rows per table
            
        Returns:
            Dictionary mapping table names to lists of row dictionaries
        """
        if not self.schema:
            raise ValueError("No schema compiled. Call compile() first.")
        return TestDataGenerator.generate(self.schema, num_rows)
    
    def visualize_ascii(self) -> str:
        """Generate ASCII ERD visualization"""
        if not self.schema:
            raise ValueError("No schema compiled. Call compile() first.")
        return ERDVisualizer.to_ascii(self.schema)
   def visualize_mermaid(self) -> str:
        """Generate Mermaid diagram code"""
        if not self.schema:
            raise ValueError("No schema compiled. Call compile() first.")
        return ERDVisualizer.to_mermaid(self.schema)
    
    def visualize_html(self) -> str:
        """Generate HTML table visualization"""
        if not self.schema:
            raise ValueError("No schema compiled. Call compile() first.")
        return ERDVisualizer.to_html_table(self.schema)
    
    def get_schema(self) -> Schema:
        """Get the compiled schema object"""
        if not self.schema:
            raise ValueError("No schema compiled. Call compile() first.")
        return self.schema
    
    def summary(self) -> Dict[str, Any]:
        """Get summary statistics about the schema"""
        if not self.schema:
            raise ValueError("No schema compiled. Call compile() first.")
        
        total_columns = sum(len(table.columns) for table in self.schema.tables.values())
        total_pks = sum(len(table.get_primary_keys()) for table in self.schema.tables.values())
        total_fks = sum(
            1 for table in self.schema.tables.values() 
            for col in table.columns if col.references
        )
        
        return {
            "schema_name": self.schema.name,
            "num_tables": len(self.schema.tables),
            "num_relationships": len(self.schema.relationships),
            "total_columns": total_columns,
            "total_primary_keys": total_pks,
            "total_foreign_keys": total_fks,
            "tables": list(self.schema.tables.keys())
        }

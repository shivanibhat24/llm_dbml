"""Test Data Generator"""

import random
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
from .models import Schema, Table, Column, DataType


class TestDataGenerator:
    """Generate realistic test data for schemas"""
    
    FIRST_NAMES = ["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Grace", "Henry"]
    LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller"]
    
    @staticmethod
    def generate(schema: Schema, num_rows: int = 10) -> Dict[str, List[Dict[str, Any]]]:
        """Generate test data for all tables"""
        data = {}
        
        # Generate in order respecting foreign keys
        generated_tables = set()
        
        while len(generated_tables) < len(schema.tables):
            for table_name, table in schema.tables.items():
                if table_name in generated_tables:
                    continue
                
                # Check if all referenced tables are generated
                can_generate = True
                for col in table.columns:
                    if col.references:
                        ref_table = col.references[0]
                        if ref_table not in generated_tables and ref_table != table_name:
                            can_generate = False
                            break
                
                if can_generate:
                    data[table_name] = TestDataGenerator._generate_table_data(
                        table, num_rows, data
                    )
                    generated_tables.add(table_name)
        
        return data
    
    @staticmethod
    def _generate_table_data(
        table: Table, 
        num_rows: int, 
        existing_data: Dict[str, List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """Generate test data for a single table"""
        rows = []
        
        for i in range(num_rows):
            row = {}
            for col in table.columns:
                if col.primary_key and col.data_type == DataType.INTEGER:
                    row[col.name] = i + 1
                elif col.references:
                    # Get a random id from referenced table
                    ref_table, ref_col = col.references
                    if ref_table in existing_data and existing_data[ref_table]:
                        ref_row = random.choice(existing_data[ref_table])
                        row[col.name] = ref_row.get(ref_col)
                    else:
                        row[col.name] = None
                else:
                    row[col.name] = TestDataGenerator._generate_value(col, i)
            rows.append(row)
        
        return rows
    
    @staticmethod
    def _generate_value(col: Column, index: int) -> Any:
        """Generate a single value based on column type"""
        if col.nullable and random.random() < 0.1:
            return None
        
        if col.data_type == DataType.INTEGER:
            return random.randint(1, 1000)
        elif col.data_type == DataType.BIGINT:
            return random.randint(1000000, 9999999999)
        elif col.data_type == DataType.VARCHAR:
            if 'email' in col.name.lower():
                return f"user{index}@example.com"
            elif 'first' in col.name.lower() and 'name' in col.name.lower():
                return random.choice(TestDataGenerator.FIRST_NAMES)
            elif 'last' in col.name.lower() and 'name' in col.name.lower():
                return random.choice(TestDataGenerator.LAST_NAMES)
            elif 'name' in col.name.lower():
                first = random.choice(TestDataGenerator.FIRST_NAMES)
                last = random.choice(TestDataGenerator.LAST_NAMES)
                return f"{first} {last}"
            elif 'phone' in col.name.lower():
                return f"+1-555-{random.randint(100,999)}-{random.randint(1000,9999)}"
            elif 'title' in col.name.lower():
                return f"Title {index + 1}"
            else:
                return f"value_{index}"
        elif col.data_type == DataType.TEXT:
            return f"This is sample text content for row {index}. Lorem ipsum dolor sit amet."
        elif col.data_type == DataType.BOOLEAN:
            return random.choice([True, False])
        elif col.data_type == DataType.DATE:
            date = datetime.now() - timedelta(days=random.randint(0, 365))
            return date.date().isoformat()
        elif col.data_type == DataType.DATETIME or col.data_type == DataType.TIMESTAMP:
            dt = datetime.now() - timedelta(hours=random.randint(0, 8760))
            return dt.isoformat()
        elif col.data_type == DataType.DECIMAL or col.data_type == DataType.FLOAT:
            return round(random.uniform(10, 1000), 2)
        elif col.data_type == DataType.JSON:
            return json.dumps({"key": f"value_{index}", "index": index})
        elif col.data_type == DataType.UUID:
            hex_str = f"{random.randint(0, 0xffffffff):08x}"
            return f"{hex_str[:8]}-{hex_str[8:12]}-4000-8000-{random.randint(0, 0xffffffffffff):012x}"
        
        return None

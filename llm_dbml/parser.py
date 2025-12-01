"""Natural Language Parser for database schemas"""

import re
from typing import List, Optional
from .models import Schema, Table, Column, Relationship, DataType, RelationType


class NLParser:
    """Natural Language Parser for database schemas"""
    
    # Keyword mappings
    TYPE_KEYWORDS = {
        'integer': DataType.INTEGER, 'int': DataType.INTEGER, 'number': DataType.INTEGER,
        'bigint': DataType.BIGINT, 'big integer': DataType.BIGINT,
        'string': DataType.VARCHAR, 'varchar': DataType.VARCHAR, 'text': DataType.TEXT,
        'boolean': DataType.BOOLEAN, 'bool': DataType.BOOLEAN, 'flag': DataType.BOOLEAN,
        'date': DataType.DATE, 'datetime': DataType.DATETIME, 'timestamp': DataType.TIMESTAMP,
        'decimal': DataType.DECIMAL, 'money': DataType.DECIMAL, 'price': DataType.DECIMAL,
        'float': DataType.FLOAT, 'double': DataType.FLOAT,
        'json': DataType.JSON, 'uuid': DataType.UUID, 'email': DataType.VARCHAR,
    }
    
    @staticmethod
    def parse(nl_description: str) -> Schema:
        """Parse natural language description into a schema"""
        schema = Schema()
        
        # Split into sentences
        sentences = re.split(r'[.!;\n]', nl_description)
        
        current_table = None
        
        for sentence in sentences:
            sentence = sentence.strip().lower()
            if not sentence:
                continue
            
            # Detect table creation
            if any(keyword in sentence for keyword in ['table', 'entity', 'create']):
                table_name = NLParser._extract_table_name(sentence)
                if table_name:
                    current_table = Table(name=table_name)
                    schema.add_table(current_table)
                    
                    # Check if columns are defined in same sentence
                    if any(kw in sentence for kw in ['has', 'with', 'contains', 'field', 'column']):
                        columns = NLParser._extract_columns(sentence)
                        for col in columns:
                            current_table.add_column(col)
            
            # Detect column definitions for current table
            elif current_table and any(kw in sentence for kw in ['has', 'with', 'contains', 'field', 'column']):
                columns = NLParser._extract_columns(sentence)
                for col in columns:
                    current_table.add_column(col)
            
            # Detect relationships
            elif any(kw in sentence for kw in ['references', 'links to', 'belongs to', 'has many', 'has one']):
                rel = NLParser._extract_relationship(sentence, schema)
                if rel:
                    schema.add_relationship(rel)
        
        # Add default id columns if missing and setup foreign keys
        for table in schema.tables.values():
            if not table.get_primary_keys():
                table.columns.insert(0, Column(
                    name="id",
                    data_type=DataType.INTEGER,
                    primary_key=True,
                    nullable=False
                ))
        
        # Add foreign key columns based on relationships
        for rel in schema.relationships:
            from_table = schema.get_table(rel.from_table)
            to_table = schema.get_table(rel.to_table)
            
            if from_table and to_table:
                # Check if foreign key column exists
                fk_col = from_table.get_column(rel.from_column)
                if not fk_col:
                    # Add foreign key column
                    from_table.add_column(Column(
                        name=rel.from_column,
                        data_type=DataType.INTEGER,
                        nullable=True,
                        references=(rel.to_table, rel.to_column)
                    ))
        
        return schema
    
    @staticmethod
    def _extract_table_name(sentence: str) -> Optional[str]:
        """Extract table name from sentence"""
        patterns = [
            r'(?:table|entity|create)\s+(?:called\s+)?["\']?(\w+)["\']?',
            r'(\w+)\s+(?:table|entity)',
            r'create\s+(\w+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, sentence)
            if match:
                name = match.group(1)
                # Filter out common words
                if name not in ['a', 'an', 'the', 'with', 'has']:
                    return name
        return None
    
    @staticmethod
    def _extract_columns(sentence: str) -> List[Column]:
        """Extract column definitions from sentence"""
        columns = []
        
        # Remove common phrases
        sentence = re.sub(r'(has|with|contains|field|column|called|named)\s+', '', sentence)
        
        # Split by common separators
        parts = re.split(r',|\sand\s', sentence)
        
        for part in parts:
            part = part.strip()
            if not part or len(part) < 2:
                continue
            
            words = part.split()
            if not words:
                continue
            
            # First word is likely the column name
            col_name = words[0].strip(',:;')
            
            # Skip if it's a common word
            if col_name in ['a', 'an', 'the', 'table', 'entity']:
                continue
            
            # Look for type keyword
            data_type = DataType.VARCHAR  # default
            nullable = True
            length = None
            
            for word in words[1:]:
                word = word.strip(',:;')
                if word in NLParser.TYPE_KEYWORDS:
                    data_type = NLParser.TYPE_KEYWORDS[word]
                    break
            
            # Check for constraints
            if 'required' in part or 'not null' in part or 'mandatory' in part:
                nullable = False
            
            # Set length for varchar
            if data_type == DataType.VARCHAR:
                if 'email' in col_name or 'email' in part:
                    length = 255
                elif 'phone' in col_name:
                    length = 20
                else:
                    length = 255
            
            columns.append(Column(
                name=col_name,
                data_type=data_type,
                nullable=nullable,
                length=length
            ))
        
        return columns
    
    @staticmethod
    def _extract_relationship(sentence: str, schema: Schema) -> Optional[Relationship]:
        """Extract relationship from sentence"""
        words = sentence.split()
        table_names = list(schema.tables.keys())
        
        # Find tables mentioned in sentence
        mentioned_tables = [word.strip(',:;') for word in words if word.strip(',:;') in table_names]
        
        if len(mentioned_tables) >= 2:
            from_table = mentioned_tables[0]
            to_table = mentioned_tables[1]
            
            # Determine relationship type
            rel_type = RelationType.MANY_TO_ONE
            if 'has many' in sentence:
                rel_type = RelationType.ONE_TO_MANY
            elif 'has one' in sentence:
                rel_type = RelationType.ONE_TO_ONE
            elif 'many to many' in sentence:
                rel_type = RelationType.MANY_TO_MANY
            
            return Relationship(
                from_table=from_table,
                from_column=f"{to_table}_id",
                to_table=to_table,
                to_column="id",
                rel_type=rel_type
            )
        
        return None


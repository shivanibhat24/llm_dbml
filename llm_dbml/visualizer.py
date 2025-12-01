"""ERD Visualization Tools"""

from .models import Schema, RelationType


class ERDVisualizer:
    """Generate ERD visualizations"""
    
    @staticmethod
    def to_mermaid(schema: Schema) -> str:
        """Generate Mermaid ER diagram"""
        lines = ["erDiagram"]
        
        # Add tables with columns
        for table in schema.tables.values():
            lines.append(f"  {table.name} {{")
            for col in table.columns:
                key = ""
                if col.primary_key:
                    key = "PK"
                elif col.references:
                    key = "FK"
                
                type_str = col.data_type.value
                if col.length:
                    type_str += f"({col.length})"
                
                lines.append(f"    {type_str} {col.name} {key}")
            lines.append("  }")
        
        # Add relationships
        for rel in schema.relationships:
            if rel.rel_type == RelationType.ONE_TO_ONE:
                symbol = "||--||"
            elif rel.rel_type == RelationType.ONE_TO_MANY:
                symbol = "||--o{"
            elif rel.rel_type == RelationType.MANY_TO_ONE:
                symbol = "}o--||"
            else:  # MANY_TO_MANY
                symbol = "}o--o{"
            
            lines.append(f"  {rel.from_table} {symbol} {rel.to_table} : \"\"")
        
        return "\n".join(lines)
    
    @staticmethod
    def to_ascii(schema: Schema) -> str:
        """Generate simple ASCII representation"""
        lines = []
        
        for table in schema.tables.values():
            lines.append(f"\n┌─ {table.name} " + "─" * max(0, 30 - len(table.name)))
            for col in table.columns:
                marker = "🔑" if col.primary_key else "  "
                fk = f" → {col.references[0]}" if col.references else ""
                type_info = f"{col.data_type.value}"
                lines.append(f"│ {marker} {col.name}: {type_info}{fk}")
            lines.append("└" + "─" * 40)
        
        return "\n".join(lines)
    
    @staticmethod
    def to_html_table(schema: Schema) -> str:
        """Generate HTML table representation"""
        html = ["<div class='schema-visualization'>"]
        
        for table in schema.tables.values():
            html.append(f"<h3>{table.name}</h3>")
            html.append("<table border='1' cellpadding='5'>")
            html.append("<tr><th>Column</th><th>Type</th><th>Constraints</th></tr>")
            
            for col in table.columns:
                constraints = []
                if col.primary_key:
                    constraints.append("PK")
                if not col.nullable:
                    constraints.append("NOT NULL")
                if col.unique:
                    constraints.append("UNIQUE")
                if col.references:
                    constraints.append(f"FK → {col.references[0]}")
                
                type_str = col.data_type.value
                if col.length:
                    type_str += f"({col.length})"
                
                html.append(
                    f"<tr><td>{col.name}</td><td>{type_str}</td>"
                    f"<td>{', '.join(constraints)}</td></tr>"
                )
            
            html.append("</table><br>")
        
        html.append("</div>")
        return "\n".join(html)

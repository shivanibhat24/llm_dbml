"""Basic usage examples for llm-dbml"""

from llm_dbml import DBSchemaCompiler


def example_blog_schema():
    """Example: Blog database schema"""
    compiler = DBSchemaCompiler()
    
    nl_description = """
    Create a users table with username string required, email string, 
    password_hash text, created_at timestamp, and is_active boolean.
    
    Create a posts table with title string, content text, 
    published_at timestamp, and view_count integer.
    Posts belongs to users.
    
    Create a comments table with content text and created_at timestamp.
    Comments belongs to users.
    Comments belongs to posts.
    """
    
    compiler.compile(nl_description, "blog_database")
    
    print("=== Schema Summary ===")
    print(compiler.summary())
    
    print("\n=== DBML Output ===")
    print(compiler.to_dbml())
    
    print("\n=== PostgreSQL Migration ===")
    print(compiler.generate_migration("postgresql"))
    
    print("\n=== ASCII Visualization ===")
    print(compiler.visualize_ascii())
    
    print("\n=== Test Data ===")
    data = compiler.generate_test_data(num_rows=3)
    for table_name, rows in data.items():
        print(f"\n{table_name}:")
        for row in rows:
            print(f"  {row}")


def example_ecommerce_schema():
    """Example: E-commerce database schema"""
    compiler = DBSchemaCompiler()
    
    nl_description = """
    Create a customers table with first_name, last_name, email, and phone.
    
    Create a products table with name, description text, price decimal, 
    stock_quantity integer, and sku string.
    
    Create a orders table with order_number, order_date, total_amount decimal, 
    and status string.
    Orders belongs to customers.
    
    Create a order_items table with quantity integer, unit_price decimal.
    Order_items belongs to orders.
    Order_items belongs to products.
    """
    
    compiler.compile(nl_description, "ecommerce_db")
    
    # Validate
    is_valid, errors = compiler.validate()
    print(f"Schema valid: {is_valid}")
    if errors:
        print(f"Errors: {errors}")
    
    # Export Mermaid diagram
    print("\n=== Mermaid Diagram ===")
    print(compiler.visualize_mermaid())


if __name__ == "__main__":
    print("=" * 60)
    print("BLOG SCHEMA EXAMPLE")
    print("=" * 60)
    example_blog_schema()
    
    print("\n\n" + "=" * 60)
    print("E-COMMERCE SCHEMA EXAMPLE")
    print("=" * 60)
    example_ecommerce_schema()

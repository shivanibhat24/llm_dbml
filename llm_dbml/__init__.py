"""
LLM-DBML: Natural Language to Database Schema Compiler
A comprehensive library for converting natural language descriptions to database schemas
"""

from .compiler import DBSchemaCompiler
from .models import Schema, Table, Column, Relationship, DataType, RelationType
from .parser import NLParser
from .migration import MigrationGenerator
from .test_data import TestDataGenerator
from .visualizer import ERDVisualizer

__version__ = "0.1.0"
__author__ = "Your Name"
__all__ = [
    "DBSchemaCompiler",
    "Schema",
    "Table", 
    "Column",
    "Relationship",
    "DataType",
    "RelationType",
    "NLParser",
    "MigrationGenerator",
    "TestDataGenerator",
    "ERDVisualizer",
]

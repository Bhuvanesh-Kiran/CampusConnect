from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, inspect
engine=create_engine('mysql+pymysql://root:Bhuvi%40123@localhost/college_connect')
inspector=inspect(engine)
tables=inspector.get_table_names()
print("Tables: ",tables)
for table in tables:
    columns=inspector.get_columns(table)
    print(f"\nTable: {table}")
    for column in columns:
        print(f"Column: {column['name']} | Type: {column['type']} | Nullable: {column['nullable']}")

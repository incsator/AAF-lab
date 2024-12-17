import os
import json
from tabulate import tabulate
import bisect
from bisect import bisect_left, bisect_right
import time

DATABASE_FILE = "database.json"

def display_table(table):
    print(tabulate(table['rows'], headers=table['columns'], tablefmt="grid"))

def print_tables():
    try:
        with open(DATABASE_FILE, 'r') as db_file:
            database = json.load(db_file)

        if not database:
            print("DB is empty")
            return

        for table in database:
            print(f"\nTable: {table['table']}")
            display_table(table)

    except FileNotFoundError:
        print(f"file '{DATABASE_FILE}' not found!")

# Add column indexing
def create(command):
    # {'action': 'CREATE', 'table': 'Students', 'columns': ['name', 'group', 'age', 'city'], 'indexed_columns': ['name', 'age']}
    table_name = command['table']
    columns = command['columns']
    indexed_columns = command.get('indexed_columns', [])

    table_structure = {
        'table': table_name,
        'columns': columns,
        'rows': [],
        'indexes': {col: {} for col in indexed_columns}  # Инициализация индексов
    }

    if not os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, 'w') as db:
            json.dump([], db)

    with open(DATABASE_FILE, 'r') as db:
        database = json.load(db)

    for table in database:
        if table['table'] == table_name:
            print(f"Table '{table_name}' already exists!")
            return

    database.append(table_structure)

    with open(DATABASE_FILE, 'w') as db:
        json.dump(database, db, indent=4)

    print(f"Table '{table_name}' has been created successfully!")

def insert(command):
    table_name = command['table']
    values = command['values']

    with open(DATABASE_FILE, 'r') as db:
        database = json.load(db)

    for table in database:
        if table['table'] == table_name:
            if len(values) != len(table['columns']):
                print("Error: wrong amount of columns in command!")
                return

            table['rows'].append(values)

            for idx, col in enumerate(table['columns']):
                if col in table['indexes']:
                    index = table['indexes'][col]
                    value = values[idx]
                    if value not in index:
                        index[value] = []
                    row_index = len(table['rows']) - 1

                    bisect.insort(index[value], row_index)

            for col, index in table['indexes'].items():
                sorted_index = dict(sorted(index.items()))
                table['indexes'][col] = sorted_index

            with open(DATABASE_FILE, 'w') as db:
                json.dump(database, db, indent=4)

            print(f"Data successfully inserted into '{table_name}'!")
            return

    print(f"Table '{table_name}' not found!")

def binary_search(index, key):
    keys = list(index.keys())
    values = list(index.values())

    pos = bisect_left(keys, key)
    if pos < len(keys) and keys[pos] == key:
        return values[pos]
    return []

def select(command):
    # {'action': 'SELECT', 'table': 'Students', 'join': None, 'where': None}
    # {'action': 'SELECT', 'table': 'Students', 'join': {'table': 'Points', 'on': ('s_group', 'p_group')}, 'where': ['points', '>', '80']}

    with open(DATABASE_FILE, 'r') as db_file:
        database = json.load(db_file)
    tables = {item["table"]: item for item in database}

    table_1_name = command['table']
    join = command['join']
    where = command['where']

    start_time = time.time()

    if table_1_name in tables: 
        
        table_1 = tables[table_1_name]

        result = {
                "columns": table_1["columns"],
                "rows": table_1["rows"],
                "indexes": table_1["indexes"]
            }

        table_1_columns = table_1['columns']
        
        if join is None and where is None:
            return display_table(result)

        if join:
            table_2_name = join['table']

            if table_2_name not in tables:
                return print(f'Table {table_2_name} not found!')
            
            table_2 = tables[table_2_name]

            result = {
                "columns": table_1["columns"] + table_2["columns"],
                "rows": [],
                "indexes" : {}
            }
            
            table_2_columns = table_2['columns']
            
            rows_1 = table_1['rows']
            rows_2 = table_2['rows']

            if join['on'] is None:
                for row1 in rows_1:
                    for row2 in rows_2:
                        result["rows"].append(row1 + row2)
         
            else:
                col1, col2 = join['on']
                
                if col1 in table_1_columns:
                    if col2 in table_2_columns:
                        col1_idx = table_1["columns"].index(col1)
                        col2_idx = table_2["columns"].index(col2)

                        if col1 in table_1['indexes'] and col2 in table_2['indexes']:
                            index_1 = table_1['indexes'][col1]
                            index_2 = table_2['indexes'][col2]

                            for key in index_1:
                                if key in index_2:
                                    for row1_index in index_1[key]:
                                        for row2_index in index_2[key]:
                                            result["rows"].append(rows_1[row1_index] + rows_2[row2_index])
                            
                            result["indexes"] = table_1["indexes"] | table_2["indexes"]

                        elif col1 in table_1['indexes']:
                            index_1 = table_1['indexes'][col1]

                            for row2 in rows_2:
                                col2_value = row2[col2_idx]
                                if col2_value in index_1:
                                    for row1_index in index_1[col2_value]:
                                        result["rows"].append(rows_1[row1_index] + row2)
                            
                            result["indexes"] = table_1["indexes"]

                        elif col2 in table_2['indexes']:
                            index_2 = table_2['indexes'][col2]

                            for row1 in rows_1:
                                col1_value = row1[col1_idx]
                                if col1_value in index_2:
                                    for row2_index in index_2[col1_value]:
                                        result["rows"].append(row1 + rows_2[row2_index])
                            
                            result["indexes"] = table_2["indexes"]

                        else:
                            for row1 in rows_1:
                                for row2 in rows_2:
                                    if row1[col1_idx] == row2[col2_idx]:
                                        result["rows"].append(row1 + row2)

                    else:
                        return print(f'column {col2} not found')
                else:
                    if col2 in table_2_columns:
                        return print(f'column {col1} not found')
                    else:
                        return print(f'columns {col1} and {col2} not found')

        if where:
            col, operator, value = where

            if col not in result['columns']:
                return print(f'Column {col} not found')

            operators = {
                "=": lambda x, y: x == y,
                "!=": lambda x, y: x != y,
                ">": lambda x, y: x > y,
                "<": lambda x, y: x < y,
                "<=": lambda x, y: x <= y,
                ">=": lambda x, y: x >= y
            }

            operator_func = operators.get(operator)
            if not operator_func:
                return print(f"Invalid operator {operator}")

            value = str(value)
            col_idx = result['columns'].index(col)

            if col in result.get('indexes', {}):
                index = result['indexes'][col]
                keys = list(index.keys())

                matching_keys = []
                if operator == "=":
                    if value in index:
                        matching_keys = [value]
                elif operator == "!=":
                    matching_keys = [key for key in keys if key != value]
                elif operator == ">":
                    matching_keys = keys[bisect_right(keys, value):]
                elif operator == "<":
                    matching_keys = keys[:bisect_left(keys, value)]
                elif operator == ">=":
                    matching_keys = keys[bisect_left(keys, value):]
                elif operator == "<=":
                    matching_keys = keys[:bisect_right(keys, value)]

                filtered_rows = []
                for key in matching_keys:
                    for row_idx in index[key]:
                        if row_idx < len(result['rows']):
                            filtered_rows.append((row_idx, result['rows'][row_idx]))

                filtered_rows.sort(key=lambda x: x[0])

                result['rows'] = [row for _, row in filtered_rows]

            else:
                filtered_rows = []
                for row in result['rows']:
                    cell_val = str(row[col_idx])
                    if operator_func(cell_val, value):
                        filtered_rows.append(row)

                result['rows'] = filtered_rows

    else:
        if join:
            table_2_name = join['table']
            if table_2_name not in tables:
                return print(f'Tables {table_1_name} and {table_2_name} not found!')
        else:
            return print(f'Table {table_1_name} not found!')

    end_time = time.time()
    execution_time = (end_time - start_time) * 1e9 
    display_table(result)
    print(f"Время выполнения: {execution_time:.0f} наносекунд")
    return 


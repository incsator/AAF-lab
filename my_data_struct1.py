import os
import json
from tabulate import tabulate

DATABASE_FILE = "database.json"
 
# add colunm indexing

def create(command):
    # {'action': 'CREATE', 'table': 'Students', 'columns': ['name', 'group', 'age', 'city'], 'indexed_columns': ['name', 'age']}

    table_name = command['table'] 
    columns = command['columns']
    indexed_columns = command['indexed_columns']

    table_structure = {'table': table_name}
    table_structure.update({col: [] for col in columns})

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
    # {'action': 'INSERT', 'table': 'Students', 'values': ['Elizaveta', 'FB-25', '19', 'Donetsk']}
    table_name = command['table']
    values = command['values']

    with open(DATABASE_FILE, 'r') as db:
        database = json.load(db)

    for table in database:
        if table['table'] == table_name:
            if len(values) != len(table) - 1:
                print(f"Error: wrong amount of columns in command!")
                return

            column_names = [col for col in table if col != 'table']
            for i, value in enumerate(values):
                table[column_names[i]].append(value)

            with open(DATABASE_FILE, 'w') as db:
                json.dump(database, db, indent=4)

            print(f"Data successfully inserted into '{table_name}'!")
            return

    print(f"Table'{table_name}' not found!")
    return

def display_table(table):
    columns = [key for key in table.keys() if key != "table"]

    max_rows = len(table[columns[0]])
    formatted_rows = []
    for i in range(max_rows):
        row = {col: table[col][i] if i < len(table[col]) else None for col in columns}
        formatted_rows.append(row)

    print(tabulate(formatted_rows, headers="keys", tablefmt="grid"))

def print_tables():
    with open(DATABASE_FILE, 'r') as db_file:
        database = json.load(db_file)
    for table in database:
        table_name = table["table"]
        print(f"\nTable: {table_name}")
        display_table(table)

def select(command):
    # {'action': 'SELECT', 'table': 'Students', 'join': None, 'where': None}
    # {'action': 'SELECT', 'table': 'Students', 'join': {'table': 'Points', 'on': ('s_group', 'p_group')}, 'where': ['points', '>', '80']}

    with open(DATABASE_FILE, 'r') as db_file:
        database = json.load(db_file)
    tables = {item["table"]: item for item in database}

    table_1_name = command['table']
    join = command['join']
    where = command['where']

    if table_1_name in tables:
        table_1 = tables[table_1_name] 

        result = {key: values[:] for key, values in table_1.items() if key != "table"}
        
        if join is None and where is None:
            return display_table(result)

        if join:
            table_2_name = join['table']

            if table_2_name not in tables:
                return print(f'Table {table_2_name} not found!')
            
            table_2 = tables[table_2_name]
            
            table_1_columns = [key for key in table_1.keys() if key != "table"]
            table_2_columns = [key for key in table_2.keys() if key != "table"]

            result = {col: [] for col in table_1_columns + table_2_columns}

            rows_1 = len(table_1[table_1_columns[0]])  
            rows_2 = len(table_2[table_2_columns[0]])

            if join['on'] is None:
                for i in range(rows_1):
                    for j in range(rows_2):
                        for col in table_1_columns:
                            result[col].append(table_1[col][i])
                        for col in table_2_columns:
                            result[col].append(table_2[col][j])
                    
            else:
                col_1, col_2 = join['on']

                if col_1 in table_1_columns:
                    if col_2 in table_2_columns:

                        for i in range(rows_1):
                            for j in range(rows_2):
                                if table_1[col_1][i] == table_2[col_2][j]:
                                    for col in table_1_columns:
                                        result[col].append(table_1[col][i])
                                    for col in table_2_columns:
                                        result[col].append(table_2[col][j])
                    else:
                        return print(f'column {col_2} not found')
                else:
                    if col_2 in table_2_columns:
                        return print(f'column {col_1} not found')
                    else:
                        return print(f'columns {col_1} and {col_2} not found')

        if where:
            col, operator, value = where

            table_columns = [key for key in result.keys()]
            if col not in table_columns:
                return print(f'column {col} not found')

            result_filtered = {key: [] for key in result}
            value = str(value)

            operators = {
            "=": lambda x, y: x == y,
            "!=": lambda x, y: x != y,
            ">": lambda x, y: x > y,
            "<": lambda x, y: x < y,
            "<=": lambda x, y: x <= y,
            ">=": lambda x, y: x >= y
            }

            operator_func = operators[operator]

            if operator_func:
                for i in range(len(result[col])):
                    cell_val = str(result[col][i])
                    if operator_func(cell_val, value):
                        for key in result:
                            result_filtered[key].append(result[key][i])   

            result = result_filtered
    else:
        if join:
            table_2_name = join['table']
            if table_2_name not in tables:
                return print(f'Tables {table_1_name} and {table_2_name} not found!')
        else:
            return print(f'Table {table_1_name} not found!')

    return display_table(result)


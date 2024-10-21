import re

def valid_name(name):
    name_pattern = r'^[a-zA-Z][a-zA-Z0-9_]*$'
    if re.match(name_pattern, name):
        return True
    else:
        return False

def parse_create_table(query):
    create_table_pattern = re.compile(r"CREATE\s+(\w+)\s*\(\s*(.*?)\s*\)\s*;", re.IGNORECASE | re.DOTALL)

    match = create_table_pattern.match(query)
    if match:
        invalid_names = []
        table_name = match.group(1)
        if not valid_name(table_name):
            invalid_names.append(table_name)
        columns_definition = match.group(2)

        columns = [col.strip() for col in re.split(r'\s*,\s*', columns_definition)]

        parsed_columns = []
        indexed_columns = []

        for col in columns:
            col_parts = re.split(r'\s+', col)
            column_name = col_parts[0]
            if not valid_name(column_name):
                invalid_names.append(column_name)
            if invalid_names:
               return invalid_names

            if len(col_parts) > 1 and col_parts[1].upper() == 'INDEXED':
                indexed_columns.append(column_name)
            parsed_columns.append(column_name)


        return {
            "action": "CREATE",
            "table": table_name,
            "columns": parsed_columns,
            "indexed_columns": indexed_columns
        }
    return None

def parse_insert(query):
    insert_pattern = re.compile(r"INSERT\s+(INTO\s*)?(\w+)\s*\((.*?)\)\s*;", re.IGNORECASE | re.DOTALL)
    query = query.replace("“", '').replace("”", '').replace('"', '')

    match = insert_pattern.match(query.strip())

    if match:
        table_name = match.group(2) 
        values = match.group(3).strip() 
        values_list = [val.strip() for val in re.split(r'\s*,\s*', values)]

        action = "INSERT INTO" if match.group(1) else "INSERT"

        return {
            "action": action,
            "table": table_name,
            "values": values_list
        }
    return None

def parse_select(query):
    select_pattern = re.compile(r"SELECT\s+FROM\s+(\w+)\s*(?:WHERE\s+(.*?))?(?:\s+JOIN\s+(\w+)\s+ON\s+(\w+)\s*=\s*(\w+))?\s*;", re.IGNORECASE | re.DOTALL)
    query = query.replace("“", '"').replace("”", '"')

    match = select_pattern.match(query.strip())
    if match:
        table_name = match.group(1)
        where_cond = match.group(2) if match.group(2) else None
        if where_cond != None:
            cond = re.compile(r'(\w+)\s*(>=|<=|!=|>|<|=)\s*\"([^\"]+)\"')
            check_cond = cond.match(where_cond)
            if not check_cond:
                return "Invalid condition format or missing quotes"
            else:
                column_name, operation, value = check_cond.groups()

        join_table = match.group(3) if match.group(3) else None
        join_condition = (match.group(4), match.group(5)) if match.group(4) and match.group(5) else None

        return {
            "action": "SELECT",
            "table": table_name,
            "where": [column_name, operation, value],
            "join": {
                "table": join_table,
                "condition": join_condition
            } if join_table else None
        }

    return None

def parse_sql(query):
    query = query.strip()

    create_result = parse_create_table(query)
    if create_result:
        return create_result
    
    insert_result = parse_insert(query)
    if insert_result:
        return insert_result
    
    select_result = parse_select(query)
    if select_result:
        return select_result
    
    return "wrong SQL command"

def parsed_command(comnd):
    result = parse_sql(comnd)

    print(f"Query: {comnd}")
    print('-' * 50)
    if isinstance(result, dict):
        for key, value in result.items():
            print(f"{key}: {value}")
    elif isinstance(result, list):
        print('Found invalid names:')
        for value in result:
            print(value)            
    else:
        print(result)
    
    print('=' * 50)
    print()

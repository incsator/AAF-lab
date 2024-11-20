#!/usr/bin/python3
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.lexers import PygmentsLexer
from pygments.lexers.sql import SqlLexer
from prompt_toolkit.key_binding import KeyBindings
import my_parser 
import my_data_structure

console = Console()
session = PromptSession(history=InMemoryHistory(), lexer=PygmentsLexer(SqlLexer))
bindings = KeyBindings()

@bindings.add('tab')
def _(event):
    event.app.current_buffer.insert_text('    ') 

def input_handle():
    comnd = []
    first_line = session.prompt('> ', key_bindings=bindings)  
    comnd.append(first_line)
    while True:
        line = session.prompt('... ', key_bindings=bindings)
        if line == '':
            break
        comnd.append(line)
    full_command = '\n'.join(comnd)
    return full_command

def input_command():
    console.print("[bold green]Input your command: [/bold green]")
    comnd = input_handle()

    # print(my_parser.parse_sql(comnd))

    parsed = my_parser.parse_sql(comnd)

    if isinstance(parsed, dict):
        if parsed['action'] == 'CREATE':
            my_data_structure.create(parsed)
        elif parsed['action'] == 'INSERT':
            my_data_structure.insert(parsed)
        elif parsed['action'] == 'SELECT':
            my_data_structure.select(parsed)

    elif isinstance(parsed, list):
        print('Found invalid names:')
        for value in parsed:
            print(value)            
    else:
        print(parsed)

def show_tables():
    console.print("[bold green]Showing table...[/bold green]")
    my_data_structure.print_tables()

def exit_menu():
    console.print("[bold red]Exiting...[/bold red]")
    exit()

def show_menu():
    menu_table = Table(title="Main Menu")
    menu_table.add_column("Option", style="cyan", no_wrap=True)
    menu_table.add_column("Description", style="magenta")
    
    menu_table.add_row("1", "Input command")
    menu_table.add_row("2", "Show table")
    menu_table.add_row("3", "Exit")
    
    console.print(Panel(menu_table, title="Select an Option", subtitle="Use the number keys"))

def main():
    while True:
        show_menu()
        option = Prompt.ask("[bold yellow]Enter your choice[/bold yellow]")
        
        if option == '1':
            input_command()
        elif option == '2':
            show_tables()
        elif option == '3':
            exit_menu()
        else:
            console.print("[bold red]Invalid option, please try again![/bold red]")

if __name__ == "__main__":
    main()



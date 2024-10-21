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
    my_parser.parsed_command(comnd)

def show_tables():
    console.print("[bold green]Showing table...[/bold green]")
    print('''
    Here will be displayed tables like that 
    (in the next versions of this app)

        +---------+---------------+-----------+-----------+-------------+------------+
        | cat_id  | cat_owner_id  | cat_name  | owner_id  | owner_name  | owner_age  |
        +---------+---------------+-----------+-----------+-------------+------------+
        |   10    |       1       |  Murzik   |     1     |    Vasya    |     30     |
        |   20    |       1       |  Pushok   |     1     |    Vasya    |     30     |
        +---------+---------------+-----------+-----------+-------------+------------+

     ''')

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



class Folder:
    def __init__(self, name, content=""):
        self.name = name
        self.content = content

class UltraComplexScriptInterpreter:
    def __init__(self):
        self.variables = {}
        self.folders = {}

    def evaluate_expression(self, expression):
        try:
            for var, val in self.variables.items():
                expression = expression.replace(var, str(val))
            return eval(expression)
        except ZeroDivisionError:
            raise ZeroDivisionError("Division by zero")
        except Exception as e:
            raise SyntaxError(f"Invalid expression: {expression}")

    def parse_statement(self, statement):
        if '=' in statement:
            self.parse_assignment(statement)
        elif statement.startswith("print"):
            self.parse_print(statement)
        elif statement.startswith("input"):
            self.parse_input(statement)
        elif statement.startswith("folder create"):
            self.parse_create_folder(statement)
        elif statement.startswith("folder list"):
            self.parse_list_folders()
        elif statement.startswith("folder open"):
            self.parse_open_folder(statement)
        elif statement.startswith("folder delete"):
            self.parse_delete_folder(statement)
        elif statement.startswith("if"):
            self.parse_if(statement)
        else:
            raise SyntaxError("Invalid statement: " + statement)

    def parse_assignment(self, statement):
        tokens = statement.split('=')
        if len(tokens) != 2:
            raise SyntaxError("Invalid assignment statement")

        variable_name = tokens[0].strip()
        expression = tokens[1].strip()
        if not variable_name.replace('_', '').isalnum() or not variable_name[0].isalpha():
            raise SyntaxError("Variable name must start with a letter and consist of alphanumeric characters and underscores only")

        self.variables[variable_name] = self.evaluate_expression(expression)

    def parse_print(self, statement):
        expression = statement[len("print"):].strip()
        print(self.evaluate_expression(expression))

    def parse_input(self, statement):
        variable_name = statement[len("input"):].strip()
        if not variable_name.replace('_', '').isalnum() or not variable_name[0].isalpha():
            raise SyntaxError("Variable name must start with a letter and consist of alphanumeric characters and underscores only")

        user_input = input(f"Enter value for {variable_name}: ")
        try:
            user_input = eval(user_input)
        except:
            pass
        self.variables[variable_name] = user_input

    def parse_create_folder(self, statement):
        tokens = statement.split()
        if len(tokens) < 3:
            raise SyntaxError("Invalid folder creation statement")

        folder_name = tokens[2].strip()

        print(f"Enter content for folder '{folder_name}' (End input with a single dot '.'): ")
        content_lines = []
        while True:
            line = input()
            if line.strip() == '.':
                break
            content_lines.append(line)

        content = '\n'.join(content_lines)
        self.folders[folder_name] = Folder(folder_name, content)
        print(f"Folder '{folder_name}' created successfully with content: {content}")

    def parse_open_folder(self, statement):
        tokens = statement.split()
        if len(tokens) != 3:
            raise SyntaxError("Invalid open folder statement")

        folder_name = tokens[2].strip()
        if folder_name not in self.folders:
            print(f"Folder '{folder_name}' does not exist.")
            return

        folder = self.folders[folder_name]
        print(f"Content of folder '{folder_name}':")
        self.interpret(folder.content.replace('\n', ','))

    def parse_list_folders(self):
        if not self.folders:
            print("No folders created yet.")
        else:
            print("List of folders:")
            for folder_name, folder in self.folders.items():
                print(f"{folder.name}: {folder.content}")

    def parse_delete_folder(self, statement):
        tokens = statement.split()
        if len(tokens) != 3:
            raise SyntaxError("Invalid delete folder statement")

        folder_name = tokens[2].strip()
        if folder_name not in self.folders:
            print(f"Folder '{folder_name}' does not exist.")
            return

        del self.folders[folder_name]
        print(f"Folder '{folder_name}' deleted successfully.")

    def interpret(self, code):
        statements = code.split(',')
        for statement in statements:
            if statement:
                try:
                    self.parse_statement(statement.strip())
                except Exception as e:
                    print("Error:", e)

    def parse_if(self, statement):
        condition_body = statement[2:].strip().split(": ", 1)
        if len(condition_body) != 2:
            raise SyntaxError("Invalid if statement")
        
        condition = condition_body[0].strip()
        body = condition_body[1].strip()
        if_condition = condition.split("else", 1)[0].strip()
        else_body = ""
        if "else" in condition:
            if_condition, else_body = condition.split("else", 1)
        
        if self.evaluate_expression(if_condition.strip()):
            self.interpret(body)
        elif else_body:
            self.interpret(else_body.strip())

    def parse_help(self, command=None):
        if command is None:
            print("Available commands:")
            print("  - Assignment: var = expression")
            print("  - Print: print expression")
            print("  - Input: input variable_name")
            print("  - Folder Creation: folder create folder_name")
            print("  - List Folders: folder list")
            print("  - Open Folder: folder open folder_name")
            print("  - Delete Folder: folder delete folder_name")
            print("  - Conditional (if-else) Statement: if condition: body [else: else_body]")
            return

        command = command.lower()
        if command == "assignment":
            print("Assignment: var = expression")
            print("Example: x = 5 + 3")
        elif command == "print":
            print("Print: print expression")
            print("Example: print x")
        elif command == "input":
            print("Input: input variable_name")
            print("Example: input x")
        elif command == "folder creation":
            print("Folder Creation: folder create folder_name")
            print("Example: folder create documents")
        elif command == "list folders":
            print("List Folders: folder list")
            print("Example: folder list")
        elif command == "open folder":
            print("Open Folder: folder open folder_name")
            print("Example: folder open documents")
        elif command == "delete folder":
            print("Delete Folder: folder delete folder_name")
            print("Example: folder delete documents")
        elif command == "conditional":
            print("Conditional (if-else) Statement: if condition: body [else: else_body]")
            print("Example: if x > 0: print x else: print 'Negative'")
        else:
            print("Unknown command. Type 'help' for a list of available commands.")

if __name__ == "__main__":
    interpreter = UltraComplexScriptInterpreter()
    while True:
        code = input("PyPlex: ")
        if code.lower() == "exit":
            break
        elif code.lower() == "help":
            interpreter.parse_help()
        elif code.lower().startswith("help"):
            command = code.split(maxsplit=1)[1]
            interpreter.parse_help(command)
        else:
            try:
                interpreter.interpret(code)
            except Exception as e:
                print("Error:", e)

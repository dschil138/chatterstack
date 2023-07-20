
class CommandHandler:
    def __init__(self):
        self.command_map = {}

    def register_command(self, command_name, command_instance):
        self.command_map[command_name] = command_instance

    def execute_command(self, command_name, *args, **kwargs):
        if command_name in self.command_map:
            self.command_map[command_name].execute(*args, **kwargs)


# Commands must inherit from this class
# and must have the execute() method
class ICommand:
    def execute(self):
        pass


# Commands made using the ICommand class
class ExampleCommand(ICommand):
    def __init__(self, *args):
        self.args = args

    def execute(self):
        print("Example command called with arguments:", self.args)

class QuitCommand(ICommand):
    def execute(self):
        print("Quitting the program.")
        exit(0)

class SaveConversationCommand(ICommand):
    def __init__(self, chatterstack, file_name="conversation.txt"):
        self.chatterstack = chatterstack
        self.file_name = file_name

    def execute(self):
        print(f"Saving conversation to {self.file_name}")
        conversation_json = self.chatterstack.to_json()
        with open(self.file_name, "w") as file:
            file.write(conversation_json)
        print(f"Conversation saved to {self.file_name}")

# This command allows you to call any method of the Chatterstack class
# For instance, if you want to call the Chatterstack's add_system() method,
# you would call this command like this:
# [add_system("Hello, I am a system.")]
class CallMethodCommand(ICommand):
    def __init__(self, chatterstack, method_name, *args):
        self.chatterstack = chatterstack
        self.method_name = method_name
        self.args = args

    def execute(self):
        method = getattr(self.chatterstack, self.method_name, None)
        if method and callable(method):
            try:
                method(*self.args)
            except Exception as e:
                print(f"Error calling method '{self.method_name}': {e}")
        else:
            print(f"Error: No method named '{self.method_name}' found in Chatterstack class.")

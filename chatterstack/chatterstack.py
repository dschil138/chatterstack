import re
import openai
import json
import datetime
import os

class ICommand:
    def execute(self):
        pass

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

class CallMethodCommand(ICommand):
    def __init__(self, chatterstack, method_name):
        self.chatterstack = chatterstack
        self.method_name = method_name

    def execute(self):
        method = getattr(self.chatterstack, self.method_name, None)
        if method and callable(method):
            method()
        else:
            print(f"Error: No method named '{self.method_name}' found in Chatterstack class.")



class CommandHandler:
    def __init__(self):
        self.command_map = {}

    def register_command(self, command_name, command_instance):
        self.command_map[command_name] = command_instance

    # def execute_command(self, command_name):
    #     if command_name in self.command_map:
    #         self.command_map[command_name].execute()

    def execute_command(self, command_name, *args, **kwargs):
        if command_name in self.command_map:
            self.command_map[command_name].execute(*args, **kwargs)

class Chatterstack:
    
    def __init__(self, user_defaults=None, existing_list=None):
        """Initialize the Chatist class with optional user default values & existing list, if any."""
        self.config = {
            key: value
            for key, value in (user_defaults or {}).items()
            if key in {"MODEL", "TEMPERATURE", "TOP_P", "FREQUENCY_PENALTY", "PRESENCE_PENALTY", "MAX_TOKENS", "STOP", "STREAM", "LOGIT_BIAS"}
        }

        if existing_list is None:
            self.list = []
        else:
            self.list = existing_list


        self.command_manager = CommandHandler()
        self.command_manager.register_command('quit', QuitCommand())
        self.command_manager.register_command('save', SaveConversationCommand(self))
        # self.command_manager.register_command('call_method', CallMethodCommand(self))




        self.first_response_time = None
        self.last_response_time = None
        self.duration = None
        self.reminders = []
        self.timestamps = True

        self.open_command = "{"
        self.close_command = "}"
        
        self.last_call_prompt_tokens=0
        self.last_call_full_context_prompt_tokens=0
        self.last_call_assistant_tokens=0
        self.last_call_tokens_all=0

        self.prompt_tokens_total=0
        self.assistant_tokens_total=0
        self.tokens_total_all=0
    
    def __str__(self):
        """Return a string representation of the conversation."""
        return str(self.list)

    def __len__(self):
        """Return the number of messages in the conversation."""
        return len(self.list)

    def __getitem__(self, index):
        """Return the message at the specified index."""
        if index < 0 or index >= len(self.list):
            raise IndexError("Index out of range")
        return self.list[index]
    
    def add(self, role, content):
        if self.timestamps and role != "assistant":
            timestamp = datetime.datetime.now().strftime('%m/%d %H:%M')
            content = f"{timestamp} {content}"
        new_dict = {"role": role, "content": content}
        self.list.insert(len(self.list), new_dict)
    
    def add_system(self, content):
        """Add a system message with specified content to the end of the conversation."""
        self.add("system", content)

    def add_assistant(self, content):
        """Add an assistant message with specified content to the end of the conversation."""
        self.add("assistant", content)
        
    def add_user(self, content):
        """Add a user message with specified content to the end of the conversation."""
        self.add("user", content)
        
    def user_input(self, prefix="USER: ", parse=False):
        """Add a user message with specified content to the end of the conversation."""
        user_text = input(prefix)
        if parse:
            command, user_text = self.parse_message_for_commands(user_text)
        self.add_user(user_text)
        return command

    def move_system_to(self, index):
        system_index = -1
        system_count = 0
        for i, d in enumerate(self.list):
            if d["role"] == "system":
                system_count += 1
                if system_count > 1:
                    print("More than one 'system' dict found")
                    return

                system_index = i

        if system_index == -1:
            print("No 'system' dict found")
            return

        if index < 0 or index >= len(self.list):
            print("Index out of range")
            return

        system_dict = self.list.pop(system_index)
        self.list.insert(index, system_dict)

    def move_system_to_end(self, minus=0):
        if minus < 0:
            print("Minus value cannot be negative")
            return

        system_index = -1
        system_count = 0
        for i, d in enumerate(self.list):
            if d["role"] == "system":
                system_count += 1
                if system_count > 1:
                    print("More than one 'system' dict found")
                    return

                system_index = i

        if system_index == -1:
            print("No 'system' dict found")
            return

        system_dict = self.list.pop(system_index)
        target_index = len(self.list) - minus
        self.list.insert(target_index, system_dict)

    def send_to_bot(self, **kwargs):
        """Send the conversation to the OpenAI API and append the response to the end of the conversation. Uses 3.5-turbo by default."""
        model = kwargs.get("model", self.config.get("model", "gpt-3.5-turbo"))
        temperature = kwargs.get("temperature", self.config.get("temperature", 0.8))
        top_p = kwargs.get("top_p", self.config.get("top_p", 1))
        frequency_penalty = kwargs.get("frequency_penalty", self.config.get("frequency_penalty", 0))
        presence_penalty = kwargs.get("presence_penalty", self.config.get("presence_penalty", 0))
        max_tokens = kwargs.get("max_tokens", self.config.get("max_tokens", 200))
        stop = kwargs.get("stop", self.config.get("stop", None))
        stream = kwargs.get("stream", self.config.get("stream", False))
        logit_bias = kwargs.get("logit_bias", self.config.get("logit_bias", {}))

        response = openai.ChatCompletion.create(
            model=model,
            messages=self.list,
            temperature=temperature,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            max_tokens=max_tokens,
            stop=stop,
            stream=stream,
            logit_bias=logit_bias,
        )
        self.add_assistant(response.choices[0].message.content.strip())

        self.last_response_time = response.created

        if self.first_response_time is None:
            self.first_response_time = response.created
            print("First response time: ", self.first_response_time)

        # OK,update all the token counts
        api_usage = response['usage']
        self.last_call_full_context_prompt_tokens = int((api_usage['prompt_tokens']))
        self.last_call_assistant_tokens = int((api_usage['completion_tokens']))
        self.last_call_tokens_all = int((api_usage['total_tokens']))

        self.last_call_prompt_tokens = self.last_call_full_context_prompt_tokens - self.tokens_total_all

        self.prompt_tokens_total += self.last_call_full_context_prompt_tokens
        self.assistant_tokens_total += self.last_call_assistant_tokens
        self.tokens_total_all += self.last_call_tokens_all
        # phew

        return self
    

    def to_json(self):
        """Return the conversation list as a JSON-formatted string."""
        return json.dumps(self.list)
    
    def from_json(self, json_string, clear_all=False):
        """Load a conversation from a JSON-formatted string.
        WARNING: This will overwrite the current conversation.
        This may also lead to a mismatch between your conversation and some instance attributes.
        You can also clear all attributes by setting clear_all=True.
        Think about what you want when using this method."""
        if clear_all:
            for attr in self.__dict__:
                self.__dict__[attr] = None
        self.list = json.loads(json_string)


    def remove_from_end(self, count):
        """Remove N messages (count) from the end of the list."""
        if count < 0:
            print("Count must be a non-negative integer")
            return
        self.list = self.list[:-count] if count < len(self.list) else []


    def remove_from_start(self, count):
        """Remove N messages (count) from the start of the list."""
        if count < 0:
            print("Count must be a non-negative integer")
            return
        self.list = self.list[count:] if count < len(self.list) else []


    def insert(self, index, role, content):
        """Insert a message at the specified index with the given role and content."""
        if role not in ["system", "assistant", "user"]:
            print("Invalid role")
            return
        if index < 0 or index > len(self.list):
            print("Index out of range")
            return
        self.list.insert(index, {"role": role, "content": content})


    def move_system_message(self, index, from_end=False):
        """Move the system message to the specified index. Only works if conversation contains one system message."""
        system_index = -1
        system_count = 0
        for i, d in enumerate(self.list):
            if d["role"] == "system":
                system_count += 1
                if system_count > 1:
                    print("More than one 'system' dict found")
                    return

                system_index = i

        if system_index == -1:
            print("No 'system' dict found")
            return

        if from_end:
            index = len(self.list) - 1 - index

        if index < 0 or index >= len(self.list):
            print("Index out of range")
            return

        system_dict = self.list.pop(system_index)
        self.list.insert(index, system_dict)


    def move_message_containing(self, substring, index):
        '''Move the message containing the substring to the specified index. Only works if conversation contains one message containing the substring.'''
        if index < 0 or index >= len(self.list):
            print("Index out of range")
            return

        matching_indices = [i for i, d in enumerate(self.list) if substring in d["content"]]

        if len(matching_indices) == 0:
            print("Warning: No message containing the substring was found")
        elif len(matching_indices) > 1:
            print("Warning: Multiple messages containing the substring were found")
        else:
            message_index = matching_indices[0]
            message_dict = self.list.pop(message_index)
            self.list.insert(index, message_dict)



    def parse_message_for_commands(self, message):
        pattern = re.escape(self.open_command) + r'([^' + re.escape(self.close_command) + r']*)' + re.escape(self.close_command)
        match = re.search(pattern, message)

        if match:
            command = match.group(1)
            remaining_message = re.sub(pattern, '', message, count=1).strip()

            # Check if the command exists in the command_map, otherwise try to call it as a method
            if command in self.command_manager.command_map:
                self.command_manager.execute_command(command)
            else:
                call_method_command = CallMethodCommand(self, command)
                call_method_command.execute()

            return command, remaining_message
        else:
            return None, message
        


    @property
    def last_message(self):
            return self.list[-1]["content"]
    
    @property
    def last_system_message(self):
        for message in reversed(self.list):
            if message["role"] == "system":
                return message["content"]
        return None  
    
    @property
    def last_user_message(self):
        for message in reversed(self.list):
            if message["role"] == "user":
                return message["content"]
        return None  
    
    @property
    def last_assistant_message(self):
        for message in reversed(self.list):
            if message["role"] == "assistant":
                return message["content"]
        return None  
    
    
    def print_last_message(self, prefix="ASSISTANT: ", lines_before=1, lines_after=1):
        """Print the last message in the conversation."""
        for i in range(lines_before):
            print()
        content = self.list[-1]["content"]
        print(f"{prefix}{content}")
        for i in range(lines_after):
            print()
            

    def get_conversation_duration(self):
        if self.first_response_time is None:
            print("No initial timestamp yet")
            return

        most_recent_message_time = int(datetime.datetime.now().timestamp())
        duration_seconds = most_recent_message_time - self.first_response_time
        
        hours, remainder = divmod(duration_seconds, 3600)
        minutes, _ = divmod(remainder, 60)

        self.duration = f"{hours:02d}:{minutes:02d}"
        return self.duration
    
    
    def print_formatted_conversation(self):
        for d in self.list:
            print(f'{d["role"].capitalize()}: {d["content"]}')


    def summary(self):
        """Return a summary of the conversation."""
        summary_dict = {
            "total_messages": len(self.list),
            "system_messages": self.count_role("system"),
            "assistant_messages": self.count_role("assistant"),
            "user_messages": self.count_role("user"),
            "prompt_tokens": self.prompt_tokens_total,
            "assistant_tokens": self.assistant_tokens_total,
            "total_tokens": self.tokens_total_all,
        }
        return summary_dict


    def clear(self):
        """Clear the conversation."""
        self.list = []

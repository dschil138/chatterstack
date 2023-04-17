import json
import openai

openai.api_key = "Your API Key Here"

class Chatterstack:
    
    def __init__(self, config=None, existing_list=None):
        """Initialize the Chatist class."""
        self.config = config if config is not None else {}

        if existing_list is None:
            self.list = []
        else:
            self.list = existing_list

        self.last_response_prompt_tokens=0
        self.last_response_assistant_tokens=0
        self.last_response_tokens=0

        self.total_prompt_tokens=0
        self.total_assistant_tokens=0
        self.total_tokens=0
    
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
        """Add a system message with specified content to the end of the conversation."""
        new_dict = {"role": role, "content": content}
        self.list.insert(len(self.list), new_dict)
    
    def add_system(self, content):
        """Add a system message with specified content to the end of the conversation."""
        self.insert(len(self.list), "system", content)


    def add_assistant(self, content):
        """Add an assistant message with specified content to the end of the conversation."""
        self.insert(len(self.list), "assistant", content)


    def add_user(self, content):
        """Add a user message with specified content to the end of the conversation."""
        self.insert(len(self.list), "user", content)


    def send_to_bot(self):
        """Send the conversation to the OpenAI API and append the response to the end of the conversation. Uses 3.5-turbo by default."""
        response = openai.ChatCompletion.create(
            model = self.config.get("model", "gpt-3.5-turbo"),
            messages = self.list,
            temperature = self.config.get("temperature", 0.8),
            top_p = self.config.get("top_p", 1),
            frequency_penalty = self.config.get("frequency_penalty", 0),
            presence_penalty = self.config.get("presence_penalty", 0),
            max_tokens = self.config.get("max_tokens", 200),
        )
        api_usage = response['usage']
        new_prompt_tokens = int((api_usage['prompt_tokens']))
        new_assistant_tokens = int((api_usage['completion_tokens']))
        new_tokens = int((api_usage['total_tokens']))

        self.last_response_prompt_tokens = new_prompt_tokens
        self.last_response_assistant_tokens = new_assistant_tokens
        self.last_response_tokens = new_prompt_tokens

        self.total_prompt_tokens += new_prompt_tokens
        self.total_assistant_tokens += new_assistant_tokens
        self.total_tokens += new_tokens

        self.add_assistant(response.choices[0].message.content.strip())
        return self
    


    def to_json(self):
        """Return the conversation list as a JSON-formatted string."""
        return json.dumps(self.list)


    def remove_from_end(self, count):
        """Remove N messages (count) from the end of the list."""
        if count < 0:
            raise ValueError("Count must be a non-negative integer")
        self.list = self.list[:-count] if count < len(self.list) else []


    def remove_from_start(self, count):
        """Remove N messages (count) from the start of the list."""
        if count < 0:
            raise ValueError("Count must be a non-negative integer")
        self.list = self.list[count:] if count < len(self.list) else []


    def insert(self, index, role, content):
        """Insert a message at the specified index with the given role and content."""
        if role not in ["system", "assistant", "user"]:
            raise ValueError("Invalid role")
        if index < 0 or index > len(self.list):
            raise IndexError("Index out of range")
        self.list.insert(index, {"role": role, "content": content})


    def get_roles(self):
        """Return an ordered list of roles in the conversation."""
        return [d["role"] for d in self.list]


    def filter_by_role(self, role):
        """Return a list of messages from the specified role."""
        if role not in ["system", "assistant", "user"]:
            raise ValueError("Invalid role")
        return [d for d in self.list if d["role"] == role]


    def count_role(self, role):
        """Return the number of messages with the specified role."""
        if role not in ["system", "assistant", "user"]:
            raise ValueError("Invalid role")
        return sum(1 for d in self.list if d["role"] == role)
    

    def move_system_message(self, index, from_end=False):
        """Move the system message to the specified index. Only works if conversation contains one system message."""
        system_index = -1
        system_count = 0
        for i, d in enumerate(self.list):
            if d["role"] == "system":
                system_count += 1
                if system_count > 1:
                    raise ValueError("More than one 'system' dict found")

                system_index = i

        if system_index == -1:
            raise ValueError("No 'system' dict found")

        if from_end:
            index = len(self.list) - 1 - index

        if index < 0 or index >= len(self.list):
            raise IndexError("Index out of range")

        system_dict = self.list.pop(system_index)
        self.list.insert(index, system_dict)


    @property
    def last_message(self):
            return self.list[-1]["content"]
    

    def print_last_message(self):
            print(self.list[-1]["content"])


    @property
    def word_count(self):
        return sum(len(d["content"].split()) for d in self.list)
    
    @property
    def role_word_count(self):
        role_count = {"system": 0, "assistant": 0, "user": 0}
        for d in self.list:
            role_count[d["role"]] += len(d["content"].split())
        return role_count
    
    @property
    def average_words_per_message(self):
        total_messages = len(self.list)
        if total_messages == 0:
            return 0
        return self.word_count / total_messages


    def summary(self):
        """Return a summary of the conversation."""
        summary_dict = {
            "total_messages": len(self.list),
            "system": self.count_role("system"),
            "assistant": self.count_role("assistant"),
            "user": self.count_role("user"),
            "prompt_tokens": self.total_prompt_tokens,
            "assistant_tokens": self.total_assistant_tokens,
            "total_tokens": self.total_tokens,
        }
        return summary_dict


    def clear(self):
        """Clear the conversation."""
        self.list = []
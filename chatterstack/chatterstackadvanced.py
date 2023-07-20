from chatterstack import *
from commands import *
import signal, ast, datetime, json, re


# ---------------- --------------------- ---------------- ---------------------
# CHATTERSTACK ADVANCED
# ---------------- --------------------- ---------------- ---------------------


class ChatterstackAdvanced(Chatterstack):
    def __init__(self, user_defaults=None, existing_list=None):
        super().__init__(user_defaults, existing_list)

        self.command_handler = CommandHandler()
        self.command_handler.register_command('quit', QuitCommand())
        self.command_handler.register_command('save', SaveConversationCommand(self))
        # the CallMethodCommand doesn't get registered here, because it is handled seperately, from within the parse_message_for_commands() method directly, for argument parsing reasons

        self.debug = False

        self.first_response_time = None
        self.last_response_time = None
        self.duration = None

        self.reminders = []
        self.parse_for_reminders = True
        self.timestamps = False
        self.open_command = "["
        self.close_command = "]"
        self.enable_commands = True
        self.enable_reminders = True

        self.next_event = None
        self.seconds_remaining = None

    


    def add(self, role, content):
        if self.timestamps and role != "assistant":
            timestamp = datetime.datetime.now().strftime('%m/%d %H:%M')
            content = f"{timestamp} {content}"
        new_dict = {"role": role, "content": content}
        self.list.insert(len(self.list), new_dict)
        return self


    def user_input(self, prefix="USER: ", parse_commands=None):
        while True:
            if parse_commands is None:
                parse_commands = self.enable_commands
            if  self.enable_reminders:
                timeout = self.update_timeout()
            if timeout:
                signal.signal(signal.SIGALRM, self.alarm_handler)
                signal.alarm(timeout)
            try:
                user_text = input(prefix)
                if parse_commands:
                    _, user_text = self.parse_message_for_commands(user_text)
                if user_text:
                    self.add_user(user_text)
                    if timeout:
                        signal.alarm(0)
                    break
            except TimeoutError:
                signal.alarm(0)
                self.send_reminder()

    @staticmethod
    def parse_argument(arg):
        try:
            return ast.literal_eval(arg)
        except (ValueError, SyntaxError):
            return arg.strip()
        
    @staticmethod
    def alarm_handler(signum, frame):
        raise TimeoutError()


    def parse_message_for_commands(self, message):
        pattern = re.escape(self.open_command) + r'([^' + re.escape(self.close_command) + r'\(]*)' + r'(\([^)]*\))?' + re.escape(self.close_command)
        match = re.search(pattern, message)
        if match:
            command = match.group(1)
            args_str = match.group(2)
            remaining_message = re.sub(pattern, '', message, count=1).strip()
            if args_str:
                # Split and parse arguments
                args_str = args_str.strip("()")
                args = [self.parse_argument(arg) for arg in args_str.split(",")]
            else:
                args = []
            if command in self.command_handler.command_map:
                self.command_handler.execute_command(command)
            else:
                call_method_command = CallMethodCommand(self, command, *args)
                call_method_command.execute()
            return command, remaining_message if remaining_message else None
        else:
            return None, message


    def parse_message_for_reminders(self, message_to_parse=None):
        """WARNING: The June updates to GPT-4 have significantly reduced the models ability to accurately output reminders. This method probably needs to be reworked to use OpenAI's new "function calling" feature."""
        if not self.list and message_to_parse is None:
            pass
        message = message_to_parse if message_to_parse is not None else self.list[-1]["content"]
        # Look for {{title|MM/DD HH:mm}}
        pattern = r'\{\{([^|]*?)\s*\|\s*([0-1]?[0-9]/[0-3]?[0-9]\s*[0-2]?[0-9]:[0-5][0-9])\}\}'
        matches = re.findall(pattern, message)
        for title, time in matches:
            self.reminders.append((title.strip(), time.strip()))  # Store as tuple -- not a dict

            self.dbprint(f"\n\033[30mREMINDERS:\n{self.reminders}\033[0m")
        # Remove matches from message
        modified_message = re.sub(pattern, '', message)
        return matches, modified_message


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


    def update_timeout(self):
        _, remaining_seconds = self.get_next_event()
        return remaining_seconds


    def send_reminder(self):
        title, time = self.next_event
        self.add_system(f"FROM SYSTEM: Generate the reminder message to send to the user now for: [{title}]. This message will be sent to the user via their calender reminder system. (DO NOT create a reminder at the beginning of your response to this message.)")
        self.reminders.remove(self.next_event)
        self.send_to_bot()
        self.remove_message_containing("FROM SYSTEM")
        self.print_last_message()


    def change_attribute(self, attribute, new_value):
        setattr(self, attribute, new_value)


    def get_next_event(self):
        now = datetime.datetime.now()
        remaining_seconds = float('inf')
        next_event_var = None
        for event in self.reminders:
            # Assuming event is a tuple with the format (title, time)
            title, time = event
            target = datetime.datetime.strptime(time, "%m/%d %H:%M").replace(year=now.year)
            if target < now:
                continue
            remaining = target - now
            if remaining.total_seconds() < remaining_seconds:
                self.seconds_remaining = int(remaining.total_seconds())
                self.next_event = event
                next_event_var = event
        if next_event_var:
            self.dbprint(f"REMAINING SECONDS: {self.seconds_remaining}")
        return (next_event_var, self.seconds_remaining) if next_event_var else (None, None)


    def imagine_api(self, api_type, prompt, max_tokens=500, temperature=0.1):
        '''this method takes two strings - the first is what type of API you want the model to act as, and the second is the prompt you want to send to that API. It returns one string - just the content of the bot's response. This SHOULD be a JSON-formatted string, (if model follows its instructions).'''
        instructions = [{"role": "system", "content": f"You are an assistant that acts as an {api_type} API. Whatever the input, you must output a JSON string that would be returned from a {api_type} API. Do not include any other text or characters in your response but the JSON string, or it will break text parser. If you cannot come up with correct or relevant information for the API response, you should make up data (or return null data) rather than not return a JSON response."}, {"role": "user", "content": f"{prompt}"}]
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=instructions,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )
        response_string= response.choices[0].message.content.strip()
        self.dbprint(f"RESPONSE STRING: {response_string}")
        return response_string


    def get_completion(self, prompt, model="text-davinci-003", max_tokens=400, temperature=1, print_response=True):
        self.dbprint(prompt)
        response = openai.Completion.create(
            model=model,
            prompt=prompt,
            max_tokens=max_tokens,
            n=1,
            stop=None,
            temperature=1,
        )
        if print_response:
            print(response.choices[0].text.strip())
        return response.choices[0].text.strip()


    def send_to_bot(self, parse=None, **kwargs):
        """Send the conversation to the OpenAI API and append the response to the end of the conversation. Uses 3.5-turbo by default."""
        self.trim_to_max_length()
        parse = kwargs.get('parse', None)
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

        self.dbprint(response.choices[0].message.content.strip())
            
        message_to_append = response.choices[0].message.content.strip()


        # Check conditions for parsing reminders
        if parse is True or (parse is None and self.parse_for_reminders is True):
            self.dbprint(f"BEFORE PARSE: {message_to_append}")
            _, message_to_append = self.parse_message_for_reminders(message_to_append)
            self.dbprint(f"AFTER PARSE: {message_to_append}")


        self.add_assistant(message_to_append)

        self.last_response_time = response.created
        if self.first_response_time is None:
            self.first_response_time = response.created
            self.dbprint(f"First response time: {self.first_response_time}")

        api_usage = response['usage']
        self.last_call_full_context_prompt_tokens = int((api_usage['prompt_tokens']))
        self.last_call_completion_tokens = int((api_usage['completion_tokens']))
        self.last_call_tokens_all = int((api_usage['total_tokens']))

        self.last_call_prompt_tokens = self.last_call_full_context_prompt_tokens - self.tokens_total_all

        self.prompt_tokens_total += self.last_call_full_context_prompt_tokens
        self.assistant_tokens_total += self.last_call_completion_tokens
        self.tokens_total_all += self.last_call_tokens_all
        return self

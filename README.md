
<img width="1056" alt="chatterstack-logo-yellow-81" src="https://user-images.githubusercontent.com/11950317/233201260-9d9cde47-ccbb-4c5e-ac58-5a059653e798.png">

Chatterstack is a dead simple and intuitive way to handle the "conversation" variables used by the ChatGPT API, while also giving you advanced functionality.

# 🛠️ Setup
Install package from pip:
```py
pip install chatterstack
```

### import & initialization:
There are two options for Chatterstack. The Base Library, and the Advanced Library, which extends the Base.
```py
import chatterstack

# The base library if you are only really concerned about mananging
# the conversation variable, it's order, and maybe tracking tokens.
convo = chatterstack.Chatterstack()

# The advanced library allows you issuing commands from the chat input,
# gives the bot the ability to reach out to you with reminders, etc 
convo = chatterstack.ChatterstackAdvanced()
```


# Overview: Chatterstack Base Class

## 🤔 The  Problem

The ChatGPT APIs use a "conversation" variables to keep track of your interactions with the bot. This is a list of dictionaries, with each dictionary representing a message.

This leaves your program being littered with things like this:

```py
# append the bot's response to your conversation
conversation.append({'role': response.choices[0].message.role, 'content': response.choices[0].message.content})

# to print the last message 
print(conversation[-1]["content"])
```
If you want to do anything more advanced like "keep conversation variable to 8 messages max", or "make the System message always be the most recent message in the conversation"... well, I'll spare you the code snippet for those.

### But,
Since this conversation variable is just made short, structured and highly predictable dictionaries...
<!-- - a list that only ever contains dictionaries
- and each dictionary alway contains just the same two keys
- and the first key can only ever be one of three values -->

...this means we can actually abstract away a lot of this mess in a way that is much more intuitive to use - while also keeping basically all of the inherent flexibility! That is a rare thing to be able to do.


### look:


This is a fully functional chatbot program using chatterstack:

```py
import chatterstack
import os

os.environ['OPENAI_API_KEY'] = 'YOUR_API_KEY_HERE'

convo = chatterstack.Chatterstack()

while True:
    convo.user_input()
    
    convo.send_to_bot()

    convo.print_last_message()
```
That's the whole thing!

Here's what that conversation looks like:

```txt
USER: hey, can you help me with something?

ASSISTANT: Sure! What would you like help with?

USER: I need to know if France has a President or a Prime Minister

ASSISTANT: France has both a President and a Prime Minister, [... bot goes on]
```

## But still flexible
This library is built to be *intuitive and flexible*, so you can easily change the behavior or look, in many ways, whatever suits your needs. Here's some basic examples:

```py

while True:
    convo.user_input(prefix="ME: ")
    
    # change any of the API arguments
    convo.send_to_bot(model="gpt-4", temperature=1, max_tokens=40)

    # change the line spacing
    convo.print_last_message(prefix="GPT: ", lines_before=0, lines_after=2)

    # and let's have it print the total tokens after each turn
    print(convo.tokens_total_all)

    
```
Now your conversation is with GPT-4, and conversation looks like this, with token counts:

```txt
ME: hey, can you help me with something?
GPT: Of course! I'm here to help. Please let me know what you need assistance with, and I'll do my best to help you.

28

ME: I need to know if France has a President or a Prime Minister
GPT: France has both a President and a Prime Minister. The President of France is [...bot goes on]

87
```
There is more info about the current defaults and various methods to change them below in the section about sending messages to the API


<!-- # 👨‍💻 Chatterstack Base Library -->
## 📨 Getting Input 
Let's look at the fundamentals first. **Even if you plan to use the Advanced Library, I highly recommend you read the whole README in order, starting here.**

The `user_input()` method is the same as the python `input()` method, except it also automatically appends the user input in a correctly-formatted dict to your conversation

```py
convo.user_input()
```
As seen above, this method defaults to prompting the user with "USER: ", but you can change it to whatever you'd like
```py
convo.user_input("Ask the bot: ")
```
```txt
Ask the bot: 
```

## 📨 Adding Messages
Maybe you aren't collecting your input from the terminal.

Or maybe you want alter the input before appending it.

There are several ways to take string variables and add them to the conversation as a correctly formatted dict:
```py
# A string you did some formatting on
formatted_message = "I want this all to be in LOWER case".lower()

# Use the .add() method. Pass it the role, then the content
convo.add("user", formatted_message)
```
```py
# or use the role-specific methods & just pass the content

convo.add_user(formatted_message)
convo.add_assistant("I'm a manually added assistant response")
convo.add_system("SYSTEM INSTRUCTIONS - you are a helpful assistant who responds only in JSON")
```

There is also .insert() if you want to add a message at a specific index, instead of the end of the conversation:

```py
# Here's the format
convo.insert(index, role, content)

# And an example
convo.insert(4, "system", "IMPORTANT: Remember to not apologize to the user so much")
```

## 💌 Sending messages to the API
The chatterstack "send_to_bot" method is a standard OpenAI API call, but it's simpler to use and does a bunch of handy stuff for you in the background. Call it like this:

```py
convo.send_to_bot()
```
That's it!

It will take care of passing all the default values for you, as well as appending the response to your conversation. It also keeps token counts for you (and in the advanced class, much more)

### Changing the defaults for the send_to_bot() method:
By default, chatterstack uses these values:

```py
model="gpt-3.5-turbo",
temperature=0.8,
top_p=1,
frequency_penalty=0,
presence_penalty=0,
max_tokens=200
```

There are several ways to change these, depending on what is convenient to you.

The most obvious way is just to pass them as arguments when you make the call. For instance, if you wanted GPT-4 and 800 max tokens:

```py
convo.send_to_bot(model="gpt-4", max_tokens=800)
```
This approach is great when you want to make just one call with some different values.

But if you know you want different values all the time, you can define them in caps at the top of your file, and initialize chatterstack using the `globals()` dict, like this:

```py
MODEL = "gpt-4"
TEMPERATURE = 0.6
FREQUENCY_PENALTY = 1.25
MAX_TOKENS = 500

# initialize with 'globals()'
convo = chatterstack.Chatterstack(user_defaults=globals())

# and now you can just call it like this again
convo.send_to_bot()
```

Finally, if you want to just use the boilerplate OpenAI call, you can still do that! Just pass it the .list attribute of your Chatterstack:

```py
response = openai.ChatCompletion.create(
    model = "gpt-3.5-turbo",
    messages = convo.list, # <--- right here
    temperature = 0.9,
    top_p = 1,
    frequency_penalty = 0,
    presence_penalty = 0,
    max_tokens = 200,
)
```

## 📂 Accessing and Printing Messages
Super Simple:

```py
# Print the "content" of the last message
convo.print_last_message()  
```
Or, if you wanted to do formatting on the string first...
```py
# This represents/is the content of the last message
convo.last_message  

# So you can do stuff like this:
message_in_caps = convo.last_message.upper()

# print the message in all upper case
print(message_in_caps) 

```

## 🪙 What About Tokens?

oh yeah. We're keeping track of tokens.

```py
# See the tokens used on the last API call
self.last_call_prompt_tokens
self.last_call_full_context_prompt_tokens
self.last_call_completion_tokens
self.last_call_tokens_all

# At any time, check the totals for the whole conversation so far
self.prompt_tokens_total
self.assistant_tokens_total
self.tokens_total_all
```


## ⤵️ List Manipulation
Various methods are available to manipulate the order of the conversation, here are a few:
```py
# Insert message at a specified index
convo.insert(index, role, content) 

# Remove N messages from the end of the list
convo.remove_from_end(count) 

# Remove N messages from the start of the list
convo.remove_from_start(count) 
```

But much more importantly - methods for fine-grained control over the system message.

System messages are usually used for instructions, and often it can be helpful to have the instructions appear more "recently" in the conversation. Which means tracking and moving this message, with out disrupting the others.
```py
# move your system message to be the most recent message in convo
convo.move_system_to_end()

# or second to last, etc
convo.move_system_to_end(minus=1)
```

And my personal favorite - basically the whole reason I wrote this entire library -
```py
convo.set_system_lock_index(-1)
```
Passing it a positive value to this function will lock the system message to the index. Anytime messages are added, removed, or re-ordered, it will make sure the system message stays at that position (or as close to it as possible).

Passing it a negative value will lock your system message to the index counting from the end of the conversation (the example above would make it always be the second to last message in the conversation).

*NOTE: Currently, these methods assume that you only have one system message*

## 📊 Track and Debug Your Conversation
Print a formatted version of your conversation (great for debugging)
```py
convo.print_formatted_conversation
```
By default, prints like this:
```txt
System: You are a helpful assistant.
User: hi!
Assistant: Hi! How can I help you?
```

see the overall stats of your conversation.
```py
convo.summary()
```
```txt
SUMMARY:
{'total_messages': 2, 'prompt_tokens': 200, 'assistant_tokens': 78, 'total_tokens': 278}
```

# Advanced Library
Chatterstack has much more functionality built-in, and is easily extensible.

## Reminders

You can now tell the bot "remind me to take the take the garbage out at 8pm", or "remind me to take the garbage out in an hour"

```
USER: hey, can you remind me to take the garbage out in an hour

ASSISTANT: Sure! I'll send you a reminder in an hour.

USER: 
{...time passes...}

ASSISTANT: Hey! Just a quick reminder to take the garbage out!
```
The bot can keep track of as many reminders at you want to issue.

## Issuing Commands
Issue commands from the user input:
```
# saves the conversation to a txt file

USER: [save]

# quit the program

USER: [quit]
```
By default you issue commands by using `[` and `]` as delimiters. But you can change these to whatever you want:

```
convo.open_command = "{{"
convo.close_command = "}}"
```

you can also self-call any method (or set any attribute) of the chatterstack class itself, right from the chat interface:
```
# if you want to see what is currently in the conversation history
USER: [print_formatted_conversation]

# or how many tokens you have used so far
USER: [print_total_tokens]

# you can even pass arguments to commands
USER: [set_system_lock_index(-2)]
```

So, while the initial chat program example at the start of this repo may have seemed simplistic at first, you can see that it's really all you need, as almost any functionality you want can actually be called from inside the chat itself.

## Extra Advanced: Adding your own commands
If you want to write your own commands, chatterstack provides a simple interface class to do so, called `ICommand`. 

```py
class ICommand:
    
    def execute(self):
        pass
```

Basically, you write your command as a class, which inherits from the `ICommand` class, and has an "execute" method (which is what you want to actually happen when your command gets called.)

Here is an example:

```py
class ExampleCommand(ICommand):

    def execute(self):
        print("An example command that prints this statement right here.")
```

If your command needs arguments, you can also add an `__init__` method, and pass it `*args` exactly like this:

```py
class ExampleCommand(ICommand):

    def __init__(self, *args):
        self.args = args

    def execute(self):
        print("Example command that print this statement with this extra stuff:", self.args)
```

The last thing you need to do is assign your command a trigger word or phrase by adding it to the __init__ method in the ChatterstackAdvanced class.

```py
class ChatterstackAdvanced(Chatterstack):
    def __init__(self, ...)
        # ...Lots of other code here...

        # This command is already in the class:
        self.command_handler.register_command('save', SaveConversationCommand(self))

        # Add your new command
        self.command_handler.register_command("example", ExampleCommand)
```

---

## Javascript 
There is currently a Javascript version of Chatterstack, butt I have not made it available yet because I don't know Javascript as well, and am not so confident in it's dependability. If you do know Javascript and would like to help, please let me know!
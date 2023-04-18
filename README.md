# Chatterstack 
Dead simple and intuitive way to handle the "conversation" variables used by the ChatGPT API

# Overview

Here's an fully functional chatbot program using chatterstack:

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

Here is what the resulting conversation looks like:

```txt
USER: hey, can you help me with something?

ASSISTANT: Sure! What would you like help with?

USER: I need to know if France has a President or a Prime Minister

ASSISTANT: France has both a President and a Prime Minister, [... bot goes on]
```

### Easily change the defaults
This library is built to be intuitive and flexible, so there are several ways for you to easily change any of the defaults (both function and formatting) however you wish. Here's one example:

```py

while True:
    # Change the user prompt prefix
    convo.user_input(user_prefix="ME: ")

    # Change any of the API arguments
    convo.send_to_bot(model="gpt-4", temperature=1, max_tokens=40)

    # Change bot display prefix and remove the empty spacer lines
    convo.print_last_message(assistant_prefix="GPT: ", lines_before=0, lines_after=0)
```
Now the conversation looks like this:

```txt
ME: hey, can you help me with something?
GPT: Of course! I'm here to help. Please let me know what you need assistance with, and I'll do my best to help you.
ME: I need to know if France has a President or a Prime Minister
GPT: France has both a President and a Prime Minister. The President of France is [...bot goes on]
```
There is more info about the current defaults and various methods to change them below in the section about sending messages to the API

---

# 🛠️ Setup
Make sure you have the OpenAI python library installed:


```py
pip install openai
```

import & initialization:
```py
from chatterstack import Chatterstack

convo = Chatterstack()
```

# 👨‍💻 Usage
## 📨 Getting Input 
Get user input from terminal AND append it correctly to the conversation

```py
convo.user_input()
```
The above will default to prompting the user input with "USER: ", looking like this in the terminal:
```py
USER:
```
But you can change the input prompt like this:
```py
convo.user_input("Ask the bot: ")
```
```py
Ask the bot: 
```
Whatever user input is given will be added to the end of the conversation variable automatically


## 📨 Adding Messages
If you want to collect your user input separately, and perhaps alter or format it somehow before adding it to the conversation variable, there are several ways to take just a string and add it to the conversation as a correctly formatted dict:
```py
# The .add() method. Pass it the role, then the content
convo.add("user", "I'm the content of the user message")

# or use the role-specific methods & just pass the content
convo.add_system("This is a system message.")
convo.add_user("This is a user message.")
convo.add_assistant("This is an assistant message.")
```

All of the methods above append the new message to the end of the current conversation. If you want to add a message at a certain index, you can use .insert()

```py
# Here's the format
convo.insert(index, role, content)

# And an example
convo.insert(2, "system", "Remember to not apologize to the user so much")
```

## 💌 Sending the Conversation to the API
#### (and some extra notes on setting your defaults)
The chatterstack "send_to_bot" method works basically the same as the default OpenAI API call, but it's simpler and automatically appends the response to your conversation variable for you. You can call it like this:

```py
convo.send_to_bot()
```
That's it!

It will take care of filling in the default valuess for you, as well as appending the response to your conversation.

#### Changing the defaults for the send_to_bot() method:
By default, it will use the values for the API call:

```py
model="gpt-3.5-turbo",
temperature=0.8,
top_p=1,
frequency_penalty=0,
presence_penalty=0,
max_tokens=200
```

But you can change any of these in several different ways, depending on what is convenient to you.

The most obvious way is just to pass them as arguments when you make the call. For instance, if you wanted GPT-4 and 800 max tokens:

```py
convo.send_to_bot(model="gpt-4", max_tokens=800)
```
This approach is especially helpful when you want to make just one call with some different values.

But if you know you want different values for the defaults, you can define them in caps at the top of your file, and initialize chatterstack using `globals()` like this:

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


Finally, if you'd rather use the standard OpenAI API method, you can do that by simply passing the .list attribute of your Chatterstack object:

```py
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=convo.list, # right here
    temperature=0.9,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0,
    max_tokens=100,
)
```


## 📂 Accessing and Printing Messages
Super Simple:

```py

convo.print_last_message()  # Prints the content value of the last message

# or, if I wanted to do formatting on the string...
convo.last_message  # <-- This represents/is the content of the last message

#So you can do stuff like this:
message_in_caps = convo.last_message.upper()

# print the last message in all upper case
print(message_in_caps) 

```
<!-- ## 🦾 Putting it together

So now we are starting to see how easy this is getting right? Look at this workflow:

```py
# get user input
user_input = input()

# append it to conversation
convo.add_user(user_input)

# Get response from bot AND append its response to conversation
convo.send_to_bot()

# print the bots response
convo.print_last_message()

``` -->

## 🪙 What About Tokens?

oh, yeah. We're keeping track of tokens.

```py
# See the tokens used on the last API call
convo.last_response_prompt_tokens
convo.last_response_assistant_tokens
convo.last_response_tokens # <-- this is the total from the last call


# At any time, check the totals for the whole conversation so far
convo.total_prompt_tokens
convo.total_assistant_tokens
convo.total_tokens
```


## ⤵️ List Manipulation
Various methods are available to manipulate the conversation, here are some:

```py
# Insert a message at the specified index with the given role and content
convo.insert(index, role, content) 

# Remove N messages from the end of the list
convo.remove_from_end(count) 

# Remove N messages from the start of the list
convo.remove_from_start(count) 
```

But probably the most important, in my opinion, are the methods simplifying your ability to move the system message.

Since system messages are often used for instructions, many times it can be helpful to have the instructions appear more "recently" in the conversation, as a strong reminder of how the bot should behave:
```py
# move your system message to be the most recent message in convo
convo.move_system_to_end()

# or second to last, etc
convo.move_system_to_end(minus=1)
```
*NOTE: Currently, these methods assume that you only have one system message*
## 📊 Track and Debug Your Conversation

Print a formatted version of your conversation (great for debugging)
```py
convo.print_formatted_conversation
```

```txt
System: You are a helpful assistant.
User: hi!
Assistant: Hi! How can I help you?
```

Or, get an overall summary of the stats of your conversation.
*(This returns a dict, so you can also quite easily use the info in here as variables in other functions)*
```py
convo.summary()
```
```txt
SUMMARY:
{'total_messages': 2, 'system_messages': 0, 'assistant_messages': 1, 'user_messages': 1, 'prompt_tokens': 200, 'assistant_tokens': 78, 'total_tokens': 278}
```




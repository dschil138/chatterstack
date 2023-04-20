
<img width="1056" alt="chatterstack-logo-yellow-81" src="https://user-images.githubusercontent.com/11950317/233201260-9d9cde47-ccbb-4c5e-ac58-5a059653e798.png">

Chatterstack is a dead simple and intuitive way to handle the "conversation" variables used by the ChatGPT API.

# Overview

## 🤔 The problem

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
Since this conversation variable is...
- a list that only ever contains dictionaries
- and each dictionary alway contains just the same two keys
- and the first key can only ever be one of three values

...this means we can actually abstract away a lot of this mess in a way that is much more intuitive to use - while also keeping basically all of the inherent flexibility! That is a rare thing to be able to do.


### here, look:


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

Here's what it looks like in use:

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
    # Change the terminal prefix
    convo.user_input(prefix="ME: ")

    # any of the API arguments
    convo.send_to_bot(model="gpt-4", temperature=1, max_tokens=40)

    # change the prefix and line spacing
    convo.print_last_message(prefix="GPT: ", lines_before=0, lines_after=2)

    # and let's have it print the total tokens after each turn
    print(convo.tokens_total_all+"\n\n")

    
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

---

# 🛠️ Setup
Install package from pip:
```py
pip install chatterstack
```

import & initialization:
```py
import chatterstack

convo = chatterstack.Chatterstack()
```

# 👨‍💻 Usage
## 📨 Getting Input 
Let's look at the fundamentals first.

The `user_input()` method is the same as the python `input()` method, except it also automatically appends the user input in a correctly-formatted dict to your conversation

```py
convo.user_input()
```
As seen above, this method defaults to prompting the user with "USER: ", but you can change it to whatever you'd like
```py
convo.user_input("Ask the bot: ")
```
```py
Ask the bot: 
```

>**Note** 
> We won't get too ahead of ourselves here, but just to give you an idea:
>
>The user_input() method can also parse your input for commands for you. (Like if you want to be able to quit the program by tying "{quit}" in the chat)
>```py
>user_input(parse=True)
>
>USER: Bye! {quit}
>```
>This will search for any commands you've set up to be within {curly brackets} in your input. Or whatever other delimiters you want, change them with this:
>```py
>convo.open_command = "[["
>convo.close_command = "]]"
>```


## 📨 Adding Messages
But maybe you are not collecting your input from the terminal.

Or maybe you want alter the input before appending it.

There are several ways to take string variables and add them to the conversation as a correctly formatted dict:
```py
# A string you did some extra formatting to
formatted_message = "I want this all to be in LOWER case".lower()

# Use the .add() method. Pass it the role, then the content
convo.add("user", formatted_message)
```
```py
# or use the role-specific methods & just pass the content
convo.add_user(formatted_message)
convo.add_assistant("I'm a manually added assistant response")
convo.add_system("SYSTEM REMINDER - format all responses as JSON")
```

All of the methods above append the new message to the end of the current conversation. If you want to add a message at a certain index, you can use .insert()

```py
# Here's the format
convo.insert(index, role, content)

# And an example
convo.insert(2, "system", "Remember to not apologize to the user so much")
```

## 💌 Sending the Conversation to the API
#### (and some info on setting your defaults)
The chatterstack "send_to_bot" method is a standard OpenAI API call, but it's simpler to use and does a bunch of handy stuff for you in the background. Call it like this:

```py
convo.send_to_bot()
```
That's it!

It will take care of passing all the default values for you, as well as appending the response to your conversation. It also updates a bunch of stats for you, like token use and time-sensitive functions.

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

You can change any of these in several ways, depending on what is convenient to you.

The most obvious way is just to pass them as arguments when you make the call. For instance, if you wanted GPT-4 and 800 max tokens:

```py
convo.send_to_bot(model="gpt-4", max_tokens=800)
```
This approach is great when you want to make just one call with some different values.

But if you know you want different values all the time, you can define them in caps at the top of your file, and initialize chatterstack using `globals()` like this:

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


Finally, if you want to just use the boilerplate OpenAI call, you can still do that by simply passing the .list attribute of your Chatterstack object:

```py
response = openai.ChatCompletion.create(
    model = "gpt-3.5-turbo",
    messages = convo.list, # <--- right here
    temperature = 0.9,
    top_p = 1,
    frequency_penalty = 0,
    presence_penalty = 0,
    max_tokens = 100,
)
```


## 📂 Accessing and Printing Messages
Super Simple:

```py
# Print the "content" value of the last message
convo.print_last_message()  
```
Or, if I wanted to do formatting on the string first...
```py
# This represents/is the content of the last message
convo.last_message  

# So you can do stuff like this:
message_in_caps = convo.last_message.upper()

# print the message in all upper case
print(message_in_caps) 

```

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
# Insert message at a specified index
convo.insert(index, role, content) 

# Remove N messages from the end of the list
convo.remove_from_end(count) 

# Remove N messages from the start of the list
convo.remove_from_start(count) 
```

But probably the most important, in my opinion, are the methods simplifying your ability to move the system message.

System messages are usually used for instructions, and often it can be helpful to have the instructions appear more "recently" in the conversation.
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
{'total_messages': 2, 'system_messages': 0, 'assistant_messages': 1, 'user_messages': 1, 'prompt_tokens': 200, 'assistant_tokens': 78, 'total_tokens': 278}
```
There's lots more stuff too! Browse through the Class file, you will find most methods and attributes are easy to understand just at a glance.




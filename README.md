<!-- <img width="1056" alt="chatterstack-logo-yellow-3" src="https://user-images.githubusercontent.com/11950317/232953452-44e5d0e6-3aa5-4af4-98a1-80dbd4dce4c1.png"> -->

<img width="1056" alt="chatterstack-logo-yellow-5" src="https://user-images.githubusercontent.com/11950317/232957100-7708885e-1c16-4129-a35e-067e6663fc77.png">

Chatterstack is a dead simple and intuitive way to handle the "conversation" variables used by the ChatGPT API.

# Overview

## The problem

The ChatGPT APIs use a "conversation" variables to keep track of your interactions with the bot. This variable is a list of dictionaries, with each dictionary representing a message.

This leaves your program being littered with things like this:

```py
# append the bot's response to your conversation
conversation.append({'role': response.choices[0].message.role, 'content': response.choices[0].message.content})

# to print the last message 
print(conversation[-1]["content"])
```
If you want to do anything more advanced like "keep conversation variabl to eight messages max", or "always make sure your System message is the most recent message in the conversation"... well I'll spare you the code snippet for that.

### But,
Since this conversation variable is...
- a list that only ever contains dictionaries
- and each dictionary alway contains only the same two keys
- and the first key can only ever be one of three values

...we can actually abstract away this whole process in a way tha is much more intuitive to use, while also keeping basically all of the inherent flexibility of working with the primitives. That is a rare thing to be able to do!


### See here:


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

## Easily change the defaults
This library is built to be intuitive and flexible, so there are several ways for you to easily change any of the defaults (both function and formatting) however you wish. Here's one example:

```py

while True:
    # Change the terminal prefix
    convo.user_input(user_prefix="ME: ")

    # any of the API arguments
    convo.send_to_bot(model="gpt-4", temperature=1, max_tokens=40)

    # remove the empty spacer lines
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
pip install chatterstack
```

import & initialization:
```py
import chatterstack

convo = chatterstack.Chatterstack()
```

# 👨‍💻 Usage
## 📨 Getting Input 
Get user input from terminal AND append it correctly to the conversation

```py
convo.user_input()
```
As seen above, this method defaults to prompting the user input with "USER: ", but you can change it to whatever you'd like
```py
convo.user_input("Ask the bot: ")
```
```py
Ask the bot: 
```
The important thing about this method is that it automatically appends the input to the converation

## 📨 Adding Messages
If you are not collecting your user input from the terminal, or perhaps alter or format it somehow before adding it to the conversation variable, there are several ways to take any string variable you want and add it to the conversation as a correctly formatted dict:
```py
# a string you wanted to do some extra formatting to
user_message = f"Hey, i wanted to send you this: {some_message}"

# The .add() method. Pass it the role, then the content
convo.add("user", user_message)
```
```py
# or use the role-specific methods & just pass the content
convo.add_user(user_message)
convo.add_assistant("I'm a manually added assistant response")
convo.add_system("IMPORTANT - format all responses as JSON")

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




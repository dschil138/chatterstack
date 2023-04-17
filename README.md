# Chatterstack 
Dead simple and intuitive way to handle the "conversation" variables used by the ChatGPT API

## Setup
Make sure you have the OpenAI python library installed:


```py
pip install openai
```

import & initialization:
```py
import openai
from chatterstack import Chatterstack

cs = Chatterstack()
```
---
## Usage
### Adding Messages
Add messages to the end of conversation by giving the role and the content:

```py
# general method
cs.add("user", "I'm the content of the user message")

# or use the specific methods for each role
cs.add_system("This is a system message.")
cs.add_user("This is a user message.")
cs.add_assistant("This is an assistant message.")
```

Or, if you'd like to add a message at a certain index:

```py
# Here's the format
cs.instert(index, role, content)

# And an example
cs.insert(2, "system", "Remember to not apologize to the user so much")
```

### Sending the Conversation to ChatGPT
The "send_to_bot" method works basically the same as the default OpenAI API call method, but it's simpler and automatically appends the response to your conversation variable for you. You can call it like this:

```py
cs.send_to_bot()
```
Literally, that's it.

it will send it with these defaults:

```py
    model_var="gpt-3.5-turbo",
    temperature_var=0.8,
    top_p_var=1,
    frequency_penalty_var=0,
    presence_penalty_var=0,
    max_tokens_var=200
```

any of which you can change when you call it, for instance if you wanted GPT-4, with low temp and 800 max tokens:

```py
cs.send_to_bot(
    model="gpt-4",
    temperature=0.2,
    max_tokens=800
    )
```


If you'd rather use the regular OpenAI API method, you can do that by simply passing the .list attribute of your Chatterstack object:

```py
response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=cs.list, # right here
        temperature=0.9,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        max_tokens=100,
    )
```

### Accessing Messages
To access messages in the conversation:

```py
cs.last_message  # Is the content of the last message

cs.print_last_message()  # Prints the content of the last message
```

So now we are starting to see how easy this is getting right? Look at this workflow:

```py
# get user input
user_input = input()

# append it to conversation
cs.add_user(user_input)

# Send conversation to bot & append its response to conversation
cs.send_to_bot()

# print the bots response
cs.print_last_message()

```

### What about tokens?

oh, yeah. We're keeping track of tokens.

```py
# any time you get a new response from the bot, you
# can check the stats on that call
cs.last_response_prompt_tokens
cs.last_response_assistant_tokens
cs.last_response_tokens # this is the total


# At any time, check the totals for the whole conversation so far
cs.total_prompt_tokens
cs.total_assistant_tokens
cs.total_tokens
```


### Message Manipulation
Various methods are available to manipulate the conversation, here are some:

```py
# Insert a message at the specified index with the given role and content
cs.insert(index, role, content) 

# Remove N messages from the end of the list
cs.remove_from_end(count) 

# Remove N messages from the start of the list
cs.remove_from_start(count) 

```

### Analytics on the conversation variable 
You can filter messages by role, count the number of messages per role, or get an ordered list of roles:

```py
# Get a list of messages by role
cs.filter_by_role("user")  

 # Get the number of messages from a given role
cs.count_role("assistant") 

# Get an ordered list of roles in the conversation
cs.get_roles()  
```


Or just get an overall summary of the conversation
```py
cs.summary()

>>> SUMMARY:
>>> {'total_messages': 2, 'system': 0, 'assistant': 1, 'user': 1, 'prompt_tokens': 200, 'assistant_tokens': 78, 'total_tokens': 278}
```




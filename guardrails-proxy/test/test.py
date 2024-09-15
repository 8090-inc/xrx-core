import unittest
import requests
import json
import uuid
from rich import print as rprint
from termcolor import colored
from rich import print as rprint

# Define the URL
url = "http://127.0.0.1:8094/run-reasoning-agent"

headers = {
    "Content-Type": "application/json",
    "Accept": "text/event-stream",
}

def send_messages(messages, user_input, session):
    messages.append({"role": "user", "content": user_input})
    body = {
        'session': session,
        'messages': messages,
    }
    response = requests.post(
        url,
        headers=headers,
        data=json.dumps(body),
        stream=True
    )
    for line in response.iter_lines(decode_unicode=True):
        print(line)
        if line.startswith('data: '):
            data = json.loads(line[6:])
            print('- - - '*10)
            print(colored("Agent Output:", 'yellow'))
            rprint(data)
    if 'error' in data:
        print(colored("Error:", 'red'), data)
        return None, None, None
    new_messages = data['messages']
    new_session = data['session']
    messages = messages + new_messages
    response.close()
    return new_messages[-1]['content'], messages, new_session

def main():
    print("Interactive Guardrails Proxy Test. Type 'quit' to exit.")
    messages = []
    session = {
        'guid': str(uuid.uuid4()),
    }
    while True:
        print('========'*10)
        user_input = input(colored("Customer: ", 'blue'))
        if user_input.lower() == 'quit':
            break
        response, messages, session = send_messages(messages, user_input, session)

if __name__ == "__main__":
    main()

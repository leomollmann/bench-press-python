import os
import json
import openai
import re

def is_menu_like(message):
  pattern = re.compile(f"{{menu}}")
  return pattern.search(message) is not None

class ChatApp:
  def __init__(self):
    openai.api_key = os.getenv("OPENAI_API_KEY")
    with open('./data/initial_prompt.json') as json_file:
      self.initial_prompt = json.load(json_file)
    with open(f"./data/menu.json") as json_file:
      self.menu = json.load(json_file)
      self.menu['prompt']['content'] += json.dumps(self.menu['data'])

  def continue_conversation(self, messages):
    response = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=[{ 'role': x['role'], 'content': x['content'] } for x in messages],
      temperature=0.3
    )
    return response["choices"][0]["message"]
  
  def embed_items(self, message):
    items = self.menu['data']['main_dishes'] + self.menu['data']['side_dishes'] + self.menu['data']['drinks']
    pattern = re.compile("{{([a-z]{3}-[0-9]+)}}")
    elements = pattern.findall(message)

    if len(elements) > 0:
      for e in elements:
        pattern = re.compile("{{" + e + "}}")
        message = re.sub(pattern, [x for x in items if x['id'] == e][0]['names'][0], message)
      return (message, [x for x in items if x['id'] in elements])
    
    return (message, None)
  
  def handle_menu(self, last_message, messages):
    messages.append({
      "role": "assistant", 
      "content": last_message,
      "internal": True
    })

    messages.append(self.menu['prompt'])
    response = self.continue_conversation(messages)
    (message, data) = self.embed_items(response.content)

    messages.append({
      "role": "assistant", 
      "content": message,
      "data": data
    })

    return messages

  def create_user(self, data):
    messages = [self.initial_prompt]
    messages.append({
      "role": "system", 
      "content": f"This guest's data is described as: Name: {data['name']}, Check-in date: {data['checkin']}, Check-out date: {data['checkout']}, Room: {data['room']}, Currency: USD, Total price of stay: ${data['bill']}",
      "interal": True
    })
    
    with open(f"./users/{data['name']}.json", 'w') as outfile:
      json.dump(messages, outfile)
    with open(f"./users/{data['name']}-data.json", 'w') as outfile:
      json.dump(data, outfile)

  def get_hisotry(self, user):
    messages = []
    with open(f"./users/{user}.json") as json_file:
      messages = json.load(json_file)

    messages = [x for x in messages if not x.get('internal')]
    questions = [x for x in messages if x['role'] == 'user']
    answers = [x for x in messages if x['role'] == 'assistant']

    return [{
      'question': questions[i]['content'],
      'answer': {
        'reply': answers[i]['content'],
        'data': answers[i].get('data')
      }
    } for i in range(len(questions))]
  
  def get_user(self, user):
    with open(f"./users/{user}-data.json") as json_file:
      return json.load(json_file)

  def chat(self, user, message):
    messages = []
    with open(f"./users/{user}.json") as json_file:
      messages = json.load(json_file)

    messages.append({"role": "user", "content": message})
    response = self.continue_conversation(messages)

    if is_menu_like(response.content):
      messages = self.handle_menu(response.content, messages)

    else:
      (message, data) = self.embed_items(response.content)
      messages.append({
        "role": "assistant", 
        "content": message,
        "data": data
      })

    with open(f'./users/{user}.json', 'w') as outfile:
      json.dump(messages, outfile)

    return messages[-1]
  
chat_gpt_repository = ChatApp()
import os
import json
import openai

class ChatApp:
  def __init__(self):
    openai.api_key = os.getenv("OPENAI_API_KEY")
    with open('./data/initial_prompt.json') as json_file:
      self.initial_prompt = json.load(json_file)

  def create_user(self, data):
    messages = [self.initial_prompt]
    messages.append({
      "role": "system", 
      "content": f"""This guest's data is described as: 
        Name: {data['name']}
        Check-in date: {data['checkin']}
        Check-out date: {data['checkout']}
        Currency: USD
        Total price of stay: ${data['bill']}
        """
    })
    
    with open(f"./users/{data['name']}.json", 'w') as outfile:
      json.dump(messages, outfile)

  def get_hisotry(self, user):
    messages = []
    with open(f"./users/{user}.json") as json_file:
      messages = json.load(json_file)

    return [message for message in messages if message['role'] != 'system']

  def chat(self, user, message):
    messages = []
    with open(f"./users/{user}.json") as json_file:
      messages = json.load(json_file)

    messages.append({"role": "user", "content": message})
    response = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=messages
    )
    response = response["choices"][0]["message"]

    messages.append({
      "role": "assistant", 
      "content": response.content
    })

    if response.content[:11] == 'system:menu':
      menu = {}
      with open(f"./data/menu.json") as json_file:
        menu = json.load(json_file)

      menu['prompt']['content'] += json.dumps(menu['data'])

      messages.append(menu['prompt'])
      response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
      )
      response = response["choices"][0]["message"]

      messages.append({
        "role": "assistant", 
        "content": response.content
      })

    with open(f'./users/{user}.json', 'w') as outfile:
      json.dump(messages, outfile)

    return response.content
chat_gpt_repository = ChatApp()
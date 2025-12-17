from openai import OpenAI
import json
import base64

class GptHelper:
    def __init__(self,api_key:str, settings:dict) -> None:
        self.settings = settings
        self.client = OpenAI(api_key=api_key)

    def getText(self, level:int,imgPath) -> str:
        client = self.client
        systems, assistants = self.readSettings(self.settings)
        messages = self.makeMessage(systems, assistants)

        userText = "level{}で生成してください".format(int(level))
        userMessage = {'role': "user", 'content': userText}
        messages.append(userMessage)
        stream = client.chat.completions.create(
            model = self.models,
            messages = messages,
            max_tokens = self.max_token,
            stream = True,
            temperature = self.temperature
        )
        streamStr = ""
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                streamStr += chunk.choices[0].delta.content
        return streamStr

    @staticmethod
    def readSettings(json_text: dict):
        system_settings = []
        assistant_settings = []
        for dataKey in json_text:
            if ('system' in dataKey):
                system_settings.append(json_text[dataKey])
            elif ('assistant' in dataKey):
                assistant_settings.append(json_text[dataKey])
        return system_settings, assistant_settings

    @staticmethod
    def readKey(keyPath: str):
        with open(keyPath) as f:
            jsonData = json.load(f)
        return jsonData['api_key']

    @staticmethod
    def makeMessage(systems, assistants) -> list:
        total_messages = []
        for system in systems:
            message = {'role': "system", 'content': system}
            total_messages.append(message)
        for assistant in assistants:
            message = {'role': "assistant", 'content': assistant}
            total_messages.append(message)
        return total_messages

    @staticmethod
    def encode_image(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
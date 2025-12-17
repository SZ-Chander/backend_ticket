from openai import OpenAI
import json
import base64
import os

class GPTSetter:
    def __init__(self,apiPath,base_path):
        self.apiPath = apiPath
        # apiKey = self.readKey(apiPath)
        apiKey = self.readKeybyEnviron()
        self.basicSettings = self.readBasicSettings(base_path)
        self.client = OpenAI(api_key=apiKey)

    def getText(self, settingPath:str, img_b64:str, language:str) -> str:
        client = self.client
        with open(settingPath) as f:
            setting_json = json.load(f)
        systems, assistants = self.readSettings(setting_json)
        messages = self.makeMessage(systems, assistants,language)
        userText = "Please read the image and extract the information according to the instructions."
        userImage = img_b64
        userMessage = {'role': "user", 'content': [
            {"type": "text", "text": userText},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{userImage}"}}
        ]}
        messages.append(userMessage)
        stream = client.chat.completions.create(
            model = self.basicSettings["models"],
            messages = messages,
            max_tokens = self.basicSettings["max_token"],
            stream = True,
            temperature = self.basicSettings["temperature"]
        )
        streamStr = ""
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                streamStr += chunk.choices[0].delta.content
        return streamStr

    @staticmethod
    def makeMessage(systems, assistants,language) -> list:
        total_messages = []
        for system in systems:
            message = {'role': "system", 'content': system}
            total_messages.append(message)
        for assistant in assistants:
            message = {'role': "assistant", 'content': assistant}
            total_messages.append(message)
        # language_setting_str = "Always output ONLY a JSON-like dictionary object. No explanations, no extra text. The dictionary must contain exactly these keys in order: '券種','出発駅','到着駅','席種','席番号','電車番号','経由'. For values: keep Japanese as default, BUT the values of '席番号','出発駅','到着駅','電車番号' must be localized into the language specified by {} (e.g., en, zh, ko). All other fields must stay in Japanese. If the value is unknown, output 'None'."
        # message = {'role': "assistant", 'content': language_setting_str.format(language)}
        # total_messages.append(message)
        return total_messages
    @staticmethod
    def readSettings(json_text:dict):
        system_settings = []
        assistant_settings = []
        for dataKey in json_text:
            if('system' in dataKey):
                system_settings.append(json_text[dataKey])
            elif('assistant' in dataKey):
                assistant_settings.append(json_text[dataKey])
        return system_settings, assistant_settings
    @staticmethod
    def readKey(keyPath:str):
        with open(keyPath) as f:
            jsonData = json.load(f)
        return jsonData['api_key']

    @staticmethod
    def readKeybyEnviron()->str:
        api_key = os.environ["OPENAI_API_KEY"]
        return api_key

    @staticmethod
    def readBasicSettings(settingPath:str):
        with open(settingPath) as f:
            jsonData = json.load(f)
            return jsonData

    @staticmethod
    def encode_image(img):
        return base64.b64encode(img).decode('utf-8')

# if __name__ == '__main__':
#     gptSetter = GPTSetter('/Users/szchandler/Desktop/localCode/Ticket_OCR/TicketGpt_JR/setting/api_key.json',"/Users/szchandler/Desktop/localCode/Ticket_OCR/TicketGpt_JR/setting/gpt_basic_setting.json")
#     gptSetter.getText("/Users/szchandler/Desktop/localCode/Ticket_OCR/TicketGpt_JR/setting/api_chat_setting.json", "/Users/szchandler/Desktop/localCode/Ticket_OCR/imgs/Nozomi_2in1_2.pic.jpg")
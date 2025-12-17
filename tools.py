import json

class Tools:
    @staticmethod
    def read_json(input_path:str)->dict:
        with open(input_path,'r') as f:
            return json.load(f)
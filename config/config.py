import json

class Config:
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.config_data = self.load_config()

    def load_config(self):
        with open(self.config_file, "r") as file:
            return json.load(file)
    
    def save_config(self, config_data):
        with open(self.config_file, "w") as file:
            json.dump(config_data, file, indent=4)

    def get_subscriptions(self):
        return self.config_data["subscriptions"]
    
    def get_notification_settings(self):
        return self.config_data["notifications"]

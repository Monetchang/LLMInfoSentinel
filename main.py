import argparse
import json
import os
from datetime import datetime
from fetcher.fetcher import HuggingFaceModelFetcher

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

def load_config():
    config_path = "config/config.json"
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_models(data):
    os.makedirs("data", exist_ok=True)
    with open("data/models.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4, cls=DateTimeEncoder)

def add_subscription(args, config):
    for sub in config["subscriptions"]:
        if sub["name"] == args.name or sub["url"] == args.url:
            print("Subscription name or URL already exists.")
            return
    config["subscriptions"].append({"name": args.name, "url": args.url, "type": "html"})
    with open("config/config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=4)
    print("Subscription added successfully.")

def remove_subscription(args, config):
    config["subscriptions"] = [sub for sub in config["subscriptions"] if sub["name"] != args.name]
    with open("config/config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=4)
    print("Subscription removed successfully.")

def list_subscriptions(config):
    for sub in config["subscriptions"]:
        print(f"Name: {sub['name']}, URL: {sub['url']}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--add-subscription", action="store_true", help="Add a new subscription")
    parser.add_argument("--remove-subscription", action="store_true", help="Remove an existing subscription")
    parser.add_argument("--list-subscriptions", action="store_true", help="List all subscriptions")
    parser.add_argument("--name", type=str, help="Subscription name")
    parser.add_argument("--url", type=str, help="Subscription URL")
    args = parser.parse_args()

    config = load_config()
    
    if args.add_subscription:
        if args.name and args.url:
            add_subscription(args, config)
        else:
            print("Both --name and --url are required to add a subscription.")
        return

    if args.remove_subscription:
        if args.name:
            remove_subscription(args, config)
        else:
            print("--name is required to remove a subscription.")
        return
    
    if args.list_subscriptions:
        list_subscriptions(config)
        return

    fetcher = HuggingFaceModelFetcher()
    data = fetcher.fetch()
    save_models(data)
    print("Fetched models have been saved successfully.")
    print(f"Total models: {len(data['models'])}")
    print("\nModel stats for each model:")
    for model in data['models']:
        print(f"\n{model['title']}:")
        print(f"  Likes: {model['model_stats'].get('likes', 'N/A')}")
        print(f"  Followers: {model['model_stats'].get('followers', 'N/A')}")
        if 'details' in model:
            details = model['details']
            if 'introduction' in details:
                print("\n  Introduction:")
                print(f"    {details['introduction'][:200]}...")  # 只显示前200个字符
            if 'model_summary' in details:
                print("\n  Model Summary:")
                print(f"    {details['model_summary'][:200]}...")  # 只显示前200个字符
            if 'tags' in details:
                print("\n  Tags:", ", ".join(details['tags']))
            if 'size' in details:
                print("\n  Size:", details['size'])
            if 'license' in details:
                print("\n  License:", details['license'])
            if 'downloads' in details:
                print("\n  Downloads:", details['downloads'])

if __name__ == "__main__":
    main()

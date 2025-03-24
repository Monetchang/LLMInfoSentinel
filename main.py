from config.config import Config
from scheduler.scheduler import Scheduler

def main():
    config = Config()
    scheduler = Scheduler(config)
    scheduler.run()

if __name__ == "__main__":
    main()

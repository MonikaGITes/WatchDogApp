# main.py
"""
ENTRYPOINT aplikacji WatchDog

Uruchamia główny proces monitorowania.
"""

from pipeline.monitor import monitor

from db.database import init_db

def main():
    init_db()
    monitor()

if __name__ == "__main__":
    main()
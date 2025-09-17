import os
from engine.ui.app import App

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    app = App(base_dir)
    app.start()

if __name__ == '__main__':
    main()

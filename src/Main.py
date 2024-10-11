import webview
from local_ai_chat_app import app

if __name__ == '__main__':
    webview.create_window("Local AI Chat App", app)
    webview.start()
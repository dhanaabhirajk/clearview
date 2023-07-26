import threading
from flask_socketio import emit
import time
from src import config


class BaseChatGLM:
    def emit_bot_response(self, user_query, history, room, message_id, chat_id, is_new_chat):
        pass


class ProductionChatGLM(BaseChatGLM):
    def __init__(self, subprocess_threads):
        from transformers import AutoTokenizer, AutoModel
        self.tokenizer = AutoTokenizer.from_pretrained(
            "THUDM/chatglm2-6b-int4", trust_remote_code=True)
        self.model = AutoModel.from_pretrained(
            "THUDM/chatglm2-6b-int4", trust_remote_code=True).half().cuda().eval()
        self.subprocess_threads = subprocess_threads

    def emit_bot_response(self, user_query, history, sid, message_id, chat_id, is_new_chat):
        self.subprocess_threads[sid]['thread'] = threading.currentThread()
        for response, updated_history in self.model.stream_chat(self.tokenizer, user_query, history,
                                                                max_length=config.MAX_LENGTH,
                                                                top_p=config.TOP_P,
                                                                temperature=config.TEMPERATURE):
            res = {
                "status": "ok",
                'new_chat': is_new_chat,
                "chat": {'chat_id': chat_id,
                         "message_id": message_id,
                         "message": [
                             {
                                 "author": "user",
                                 "update":  True,
                                 "content": user_query,
                             },
                             {
                                 "author": "bot",
                                 "update": True,
                                 "content": response,
                             }
                         ]}}

            emit("message", res,
                 namespace="/", room=sid)
            
            if (self.subprocess_threads[sid]['stop_flag']):
                self.subprocess_threads[sid]['stop_flag'] = False
                res["status"] = "stopped"
                break

        self.subprocess_threads[sid]['response'] = res


class NonProductionChatGLM(BaseChatGLM):
    def __init__(self, subprocess_threads):
        self.model = [("How", [("hi", "How")]), ("How can", [("hi", "How can ")]),
                      ("How can I ", [("hi", "How can I")]), ("""python code\n```\nfor i in range(5):\nprint(i)\n```""", [("hi", "How can I")])]
        self.subprocess_threads = subprocess_threads

    def emit_bot_response(self, user_query, history, sid, message_id, chat_id, is_new_chat):
        self.subprocess_threads[sid]['thread'] = threading.currentThread()
        for response, updated_history in self.model:

            res = {
                "status": "ok",
                'new_chat': is_new_chat,
                "chat": {'chat_id': chat_id,
                         "message_id": message_id,
                         "message": [
                             {
                                 "author": "user",
                                 "update":  True,
                                 "content": user_query,
                             },
                             {
                                 "author": "bot",
                                 "update": True,
                                 "content": response,
                             }
                         ]}}

            emit("message", res,
                 namespace="/", room=sid)
            
            if (self.subprocess_threads[sid]['stop_flag']):
                self.subprocess_threads[sid]['stop_flag'] = False
                res["status"] = "stopped"
                break
            time.sleep(1)
        self.subprocess_threads[sid]['response'] = res


class chatGLM:
    def __new__(cls, p_flag, subprocess_threads):
        if p_flag:
            return ProductionChatGLM(subprocess_threads)
        else:
            return NonProductionChatGLM(subprocess_threads)

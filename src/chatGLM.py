from flask_socketio import emit
import time
from src import config

class BaseChatGLM:
    def emit_bot_response(self, user_query, history, room, message_id, chat_id, is_new_chat):
        pass

class ProductionChatGLM(BaseChatGLM):
    def __init__(self):
        from transformers import AutoTokenizer, AutoModel
        self.tokenizer = AutoTokenizer.from_pretrained("THUDM/chatglm2-6b-int4", trust_remote_code=True)
        self.model = AutoModel.from_pretrained("THUDM/chatglm2-6b-int4", trust_remote_code=True).half().cuda().eval()

    def emit_bot_response(self, user_query, history, room, message_id, chat_id, is_new_chat):
        for response, updated_history in self.model.stream_chat(self.tokenizer, user_query, history, 
                                                                 max_length=config.max_length,
                                                                 top_p=config.top_p, 
                                                                 temperature=config.temperature):
            emit("message", {
                "status": "ok",
                'chat_id': chat_id,
                'new_chat': is_new_chat,
                "message_id": message_id,
                "message": [
                    {
                        "author": "user",
                        "update": True,
                        "content": user_query,
                    },
                    {
                        "author": "bot",
                        "update": True,
                        "content": response,
                    }
                ]
            }, namespace="/", room=room)
        return response

class NonProductionChatGLM(BaseChatGLM):
    def __init__(self):
        self.model = [("How", [("hi", "How")]), ("How can", [("hi", "How can ")]),
                      ("How can I ", [("hi", "How can I")]), ("""python code\n```\nfor i in range(5):\nprint(i)\n```""", [("hi", "How can I")])]

    def emit_bot_response(self, user_query, history, room, message_id, chat_id, is_new_chat):
        for response, updated_history in self.model:
            emit("message", {
                "status": "ok",
                'chat_id': chat_id,
                'new_chat': is_new_chat,
                "message_id": message_id,
                "message": [
                    {
                        "author": "user",
                        "update": True,
                        "content": user_query,
                    },
                    {
                        "author": "bot",
                        "update": True,
                        "content": response,
                    }
                ]
            }, namespace="/", room=room)
            time.sleep(0.1)
        return response

class chatGLM:
    def __new__(cls, p_flag):
        if p_flag:
            return ProductionChatGLM()
        else:
            return NonProductionChatGLM()


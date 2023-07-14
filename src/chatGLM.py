from src import config
from transformers import AutoModel, AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("THUDM/chatglm-6b-int4", trust_remote_code=True)
model = AutoModel.from_pretrained("THUDM/chatglm-6b-int4", trust_remote_code=True).half().cuda()
model = model.eval()

def get_bot_response(user_query,history):
    # for response, history in [("How",[("hi","How")]),("How can",[("hi","How can ")]),("How can I ",[("hi","How can I")])]:
    for response, history in model.stream_chat(tokenizer, user_query, history, max_length=config.max_length,
                                                    top_p=config.top_p, temperature=config.temperature):
                pass
    return response
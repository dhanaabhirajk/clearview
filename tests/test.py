def get_tokenizer_model():
  from transformers import AutoTokenizer, AutoModel
  tokenizer = AutoTokenizer.from_pretrained("THUDM/chatglm2-6b-int4", trust_remote_code=True)
  model = AutoModel.from_pretrained("THUDM/chatglm2-6b-int4", trust_remote_code=True).half().cuda()
  model = model.eval()
  return model,tokenizer

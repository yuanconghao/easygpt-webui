# helo hello
prompt = {'content': 'world', 'role': 'user'}
# conversation = [{'role': 'user', 'content': 'helo'}, {'role': 'assistant', 'content': 'hello'} ]
conversation = []
if not conversation:
    print(prompt['content'])
content = ""
for item in conversation:
    content += item["content"] + " "
content += prompt["content"]
print(content)

def convert_openai2qianfan(item):
    """
    convert_openai2qianfan
    """
    new_messages = []
    messages = item["messages"]
    if messages[0]["role"] == "system" and messages[1]["role"] == "assistant":
        for i in range(0, len(messages) - 1, 2):
            newitem = {}
            newitem["prompt"] = messages[i]["content"]
            newitem["response"] = [[messages[i + 1]["content"]]]
            new_messages.append(newitem)
    elif messages[0]["role"] == "system" and messages[1]["role"] == "user":
        for i in range(1, len(messages) - 1, 2):
            newitem = {}
            newitem["prompt"] = messages[i]["content"]
            newitem["response"] = [[messages[i + 1]["content"]]]
            new_messages.append(newitem)
        new_messages[0]["prompt"] = messages[0]["content"] + ": " + new_messages[0]["prompt"]
    elif messages[0]["role"] == "assistant" and messages[1]["role"] == "user":
        for i in range(1, len(messages) - 1, 2):
            newitem = {}
            newitem["prompt"] = messages[i]["content"]
            newitem["response"] = [[messages[i + 1]["content"]]]
            new_messages.append(newitem)
        new_messages[0]["prompt"] = messages[0]["content"] + ": " + new_messages[0]["prompt"]
    elif messages[0]["role"] == "user" and messages[1]["role"] == "assistant":
        for i in range(0, len(messages) - 1, 2):
            newitem = {}
            newitem["prompt"] = messages[i]["content"]
            newitem["response"] = [[messages[i + 1]["content"]]]
            new_messages.append(newitem)
    return new_messages


def convert_openai2llama2(item):
    pass

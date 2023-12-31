class Prompter:

    @staticmethod
    def build_messages(model, conversation, prompt, images=[]):
        """
        build gpt messages
        """
        if model == "dall-e-3":
            return prompt['content']
        elif model == "gpt-assistant-ai-teacher":
            return prompt['content']
        elif model == "gpt-4-vision-preview":
            new_content = []

            new_text = {
                "type": "text",
                "text": prompt["content"]
            }
            new_content.append(new_text)

            if not images:
                new_messages = {
                    "role": "user",
                    "content": new_content
                }
                # return conversation.append(new_messages)
                # 不要历史记录
                return [new_messages]

            for image in images:
                new_img_url = {
                    "type": "image_url",
                    "image_url": {
                        "url": image
                    }
                }
                new_content.append(new_img_url)

            new_messages = {
                "role": "user",
                "content": new_content
            }
            return [new_messages]
        elif model == "llama2-7b":
            return prompt['content']
        elif model == "llama2-7b-chat":
            # [{'role': 'user', 'content': 'helo'}, {'role': 'assistant', 'content': 'hello'} ]
            # helo hello
            if not conversation:
                return prompt['content']
            content = ""
            for item in conversation:
                content += item["content"] + " "
            content += prompt["content"]
            return content
        else:
            conversation.append(prompt)
            messages = conversation
            return messages

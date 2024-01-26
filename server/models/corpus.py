import os
import time
import openai
import json
import io
from flask import send_file
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from server.templates.corpus_prompts import ROLE_STYLE_DETAIL
from server.templates.corpus_prompts import CEFR_LEVEL_ROUNDS, CEFR_LEVEL_WORDS
from server.templates.corpus_prompts import CORPUS_BASIC_TEMPLATE
from server.templates.corpus_prompts import CORPUS_WORDS_TEMPLATE, CORPUS_SENTENCE_TEMPLATE
from server.templates.corpus_prompts import CORPUS_FORMAT_TEMPLATE
from server.config import *
from server.utils import corpus


class CorpusGenerator:
    MAX_WORKERS = 10
    MODEL_ID = "gpt-4-1106-preview"
    TEMPERATURE = 1
    MAX_TOKENS = 2048

    @staticmethod
    def request_openai(system_prompt, corpus_system=""):
        newitem = {}
        system_content = [{
            'role': 'system',
            'content': system_prompt,
        }]

        max_retries = 3
        conversations_content = []
        for attempt in range(max_retries):
            try:
                response = openai.chat.completions.create(
                    model=CorpusGenerator.MODEL_ID,
                    messages=system_content,
                    temperature=CorpusGenerator.TEMPERATURE,
                    max_tokens=CorpusGenerator.MAX_TOKENS,
                )
                print("response, ", response)
                answer = response.choices[0].message.content

                if answer:
                    answer = answer.replace('\n', '').replace("```json", "", 1).replace("```", "", 1)
                    print(answer)
                if answer:
                    answer = json.loads(answer)

                for dialogue in answer:
                    if dialogue["role"] == "assistant":
                        dialogue["content"] = dialogue["content"]
                    conversations_content.append(dialogue)
                break
            except openai.OpenAIError as e:
                if attempt < max_retries - 1:
                    time.sleep(10)
                    print(f"Attempt {attempt + 1} failed. Retrying...")
                    continue
                else:
                    print(f"Attempt {attempt + 1} failed. No more retries.")
                    continue

        if corpus_system:
            corpus_system_content = [{
                'role': 'system',
                'content': corpus_system,
            }]
            messages = corpus_system_content + conversations_content
        else:
            messages = conversations_content
        newitem['messages'] = messages
        return newitem

    @staticmethod
    def generate_corpus(basic_info, teaching_knowledge, teaching_method, corpus_info):

        # 1. generate prompt
        prompt = CorpusGenerator.format_prompt(basic_info, teaching_knowledge, teaching_method, corpus_info)
        corpus_system = CorpusGenerator.format_system_prompt(basic_info, teaching_knowledge, teaching_method)
        print("prompt: ", prompt)
        print("corpus_system: ", corpus_system)
        # 2. 多线程调用openai
        print("output", CORPUS_DIR)
        file_date = datetime.now().strftime('%Y%m%d%H%M%S')
        file_name = f"corpus_{corpus_info['corpus_format']}_{file_date}.jsonl"
        file_path = os.path.join(CORPUS_DIR, file_name)
        with open(file_path, "a") as f:
            with ThreadPoolExecutor(max_workers=CorpusGenerator.MAX_WORKERS) as executor:
                for _ in range(0, corpus_info["corpus_nums"]):
                    futures = [executor.submit(CorpusGenerator.request_openai, system_prompt=prompt,
                                               corpus_system=corpus_system)]
                    # 使用 concurrent.futures.wait 来等待所有任务完成
                    wait_result = concurrent.futures.wait(futures, return_when=concurrent.futures.ALL_COMPLETED)

                    # 检查任务的状态
                    for future in wait_result.done:
                        result = future.result()
                        # 3. 写入文件
                        if result:
                            if corpus_info["corpus_format"] == "openai":
                                result = json.dumps(result, ensure_ascii=False) + "\n"
                            elif corpus_info["corpus_format"] == "qianfan":
                                result = corpus.convert_openai2qianfan(result)
                                result = json.dumps(result, ensure_ascii=False) + "\n"
                            elif corpus_info["corpus_format"] == "llama2":
                                result = json.dumps(result, ensure_ascii=False) + "\n"
                            f.write(result)

        # 4. 提供文件下载链接
        return file_name

    @staticmethod
    def format_prompt(basic_info, teaching_knowledge, teaching_method, corpus_info):
        ## basic info template
        role_name = basic_info["role_name"]
        role_style_len = len(basic_info["role_style"])
        print("len====", role_style_len)
        # ['enthusiastic', 'encouraging', 'strict']
        if role_style_len == 0:
            role_style = "warm"
            role_detail = ROLE_STYLE_DETAIL[role_style]
        elif role_style_len == 1:
            role_style = basic_info["role_style"][0]
            role_detail = ROLE_STYLE_DETAIL[role_style]
        elif role_style_len == 2:
            role_style = " and ".join(basic_info["role_style"])
            role_detail_list = []
            for r_style in basic_info["role_style"]:
                role_detail_list.append(ROLE_STYLE_DETAIL[r_style])
            role_detail = " and ".join(role_detail_list)
        else:
            role_style = ",".join(basic_info["role_style"][:role_style_len - 1])
            role_style += " and " + basic_info["role_style"][role_style_len - 1]
            role_detail_list = []
            for r_style in basic_info["role_style"]:
                role_detail_list.append(ROLE_STYLE_DETAIL[r_style])
            role_detail = " and ".join(role_detail_list)

        cefr_level = basic_info["cefr_level"]
        corpus_func_num = len(corpus_info["corpus_func"])
        cefr_level_rounds = CEFR_LEVEL_ROUNDS[cefr_level] + corpus_func_num
        cefr_level_words = CEFR_LEVEL_WORDS[cefr_level]

        print("=============")

        basic_prompt = CORPUS_BASIC_TEMPLATE.format(
            role_name=role_name,
            role_style=role_style,
            role_style_detail=role_detail,
            cefr_level=cefr_level,
            cefr_level_rounds=cefr_level_rounds,
            cefr_level_words=cefr_level_words
        )
        print("basic_prompt:", basic_prompt)

        ## teaching konwledge
        # The conversation should include the words apple | orange
        knowledge_list = []
        knowledge_prompt = ""
        if teaching_knowledge["words"] != "":
            words_prompt = CORPUS_WORDS_TEMPLATE.format(words=teaching_knowledge["words"])
            knowledge_list.append(words_prompt)
        if teaching_knowledge["sentence"] != "":
            sentence_prompt = CORPUS_SENTENCE_TEMPLATE.format(sentence=teaching_knowledge["sentence"])
            knowledge_list.append(sentence_prompt)

        if len(knowledge_list) != 0:
            knowledge_prompt = " and ".join(knowledge_list)
        print("knowledge_prompt:", knowledge_prompt)

        ## teaching method
        method_prompt = ""
        if teaching_method["teaching_background"]:
            method_prompt += f"The dialogue background is that {teaching_method['teaching_background']}."
        if teaching_method["teaching_characters"]:
            method_prompt += f"In this dialogue is that {teaching_method['teaching_characters']}."
        if teaching_method["teaching_goal"]:
            method_prompt += f"The dialogue goal includes {teaching_method['teaching_goal']}."
        if teaching_method["teaching_example"]:
            method_prompt += f"You can refer to this example:\n {teaching_method['teaching_example']}\n"

        ## format prompt
        format_prompt = CORPUS_FORMAT_TEMPLATE

        prompt = basic_prompt + knowledge_prompt + method_prompt + format_prompt

        return prompt

    @staticmethod
    def format_system_prompt(basic_info, teaching_knowledge, teaching_method):

        system_prompt = f"This is a {teaching_knowledge['teaching_steps']} learning page."
        if teaching_knowledge["words"]:
            system_prompt += f"The core word is '{teaching_knowledge['words']}'."
        if teaching_knowledge["sentence"]:
            system_prompt += f"The core sentence is '{teaching_knowledge['sentence']}'."

        if teaching_method["teaching_background"]:
            system_prompt += f"On this page the background is {teaching_method['teaching_background']}."
        if teaching_method["teaching_characters"]:
            system_prompt += f"We can see that {teaching_method['teaching_characters']}."
        if teaching_method["teaching_goal"]:
            system_prompt += f"The dialogue goal includes {teaching_method['teaching_goal']}."

        system_prompt += "After the train departs, prize me and guide me to the next page."

        return system_prompt

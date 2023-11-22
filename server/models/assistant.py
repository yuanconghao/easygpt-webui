import json
import logging
import openai
import time
from flask import request, Response, stream_with_context, send_file, url_for
from typing import Generator, Union
from server.utils.fc_functions import function_map

ASSISTANT_ID = "asst_nPt1MUCHNMsQdGujAaXrA59m"


class AssistantGenerator:

    @staticmethod
    def request_assitant(model, messages, session_id):
        if not session_id or session_id == "undefined":
            # step1 create a thread
            thread = openai.beta.threads.create()
            session_id = thread.id

        # step2 add a message to a thread
        message = openai.beta.threads.messages.create(
            thread_id=session_id,
            role="user",
            content=messages
        )
        print(message)

        # step3 run the assistant
        run = openai.beta.threads.runs.create(
            thread_id=session_id,
            assistant_id=ASSISTANT_ID,
        )

        run = openai.beta.threads.runs.retrieve(
            thread_id=session_id,
            run_id=run.id
        )
        print("run.status::", run.status)
        image_url = None
        while True:
            if run.status == "completed":
                messages = openai.beta.threads.messages.list(
                    thread_id=session_id
                )
                break

            if run.status == "requires_action":
                print("run.required_action: ", run.required_action.__dict__)
                # 构造一个tool_outputs
                tool_outputs = []
                for require_function in run.required_action.submit_tool_outputs.tool_calls:
                    func = function_map[require_function.function.name]
                    func_res = func(**json.loads(require_function.function.arguments))
                    tool_outputs.append(
                        {
                            "tool_call_id": require_function.id,
                            "output": func_res
                        }
                    )
                print("tool_outputs: ", tool_outputs)
                image_url = tool_outputs[0]["output"]
                run = openai.beta.threads.runs.submit_tool_outputs(
                    thread_id=session_id,
                    run_id=run.id,
                    tool_outputs=tool_outputs
                )
                run = openai.beta.threads.runs.retrieve(
                    thread_id=session_id,
                    run_id=run.id
                )
                continue

            if run.status == "queued" or run.status == "in_progress":
                print("run.status::", run.status)
                run = openai.beta.threads.runs.retrieve(
                    thread_id=session_id,
                    run_id=run.id
                )
                time.sleep(0.5)
                continue

        answer = messages.data[0].content[0].text.value
        if image_url:
            # image_url = "http://127.0.0.1:8060" + image_url
            answer = f"![图片]({image_url})" + "\n\n" + answer
            print(answer)
        result = {
            "id": session_id,
            "content": answer
        }
        return Response(json.dumps(result))
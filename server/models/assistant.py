from flask import request, Response, stream_with_context, send_file, url_for
from typing import Generator, Union
import json
import logging
import openai
from server.utils.fc_functions import function_map
from server.templates.prompts import START_PROMPT


class AssistantGenerator:

    @staticmethod
    def request_assitant(model, messages):
        thread1, run1 = create_thread_and_run(
            START_PROMPT
        )

        run1 = wait_on_run(run1, thread1)
        pretty_print(get_response(thread1))

        user_input = input("user: ")
        run2 = submit_message(ASSISTANT_ID, thread1, user_input)
        run2 = wait_on_run(run2, thread1)
        pretty_print(get_response(thread1))

        return Response(get_response(thread1))

    @staticmethod
    def compact_response(response: Union[dict, Generator]) -> Response:
        """
        return stream response
        """
        if isinstance(response, dict):
            # 如果响应是一个字典，直接返回JSON响应
            return Response(response=json.dumps(response), status=200, mimetype='application/json')

        # 如果响应是一个生成器，创建并返回一个流式响应
        def generate() -> Generator:
            try:
                for chunk in response:
                    print(chunk)
                    # 假设chunk是流式API返回的数据结构
                    # 你可能需要根据实际的数据结构进行调整
                    if chunk.choices[0].finish_reason != 'stop':
                        yield chunk.choices[0].delta.content
            except Exception:
                # 在生产环境中，应使用日志记录此类错误
                logging.exception("internal server error.")

        # 使用stream_with_context确保请求上下文在流生成期间保持激活
        return Response(stream_with_context(generate()), status=200, mimetype='text/event-stream')


def submit_message(assistant_id, thread, user_message):
    openai.beta.threads.messages.create(
        thread_id=thread.id, role="user", content=user_message
    )
    return openai.beta.threads.runs.create(
        thread_id=thread.id, assistant_id=assistant_id
    )


def get_response(thread):
    return openai.beta.threads.messages.list(thread_id=thread.id, order="asc")


def create_thread_and_run(user_input):
    thread = openai.beta.threads.create()
    run = submit_message(ASSISTANT_ID, thread, user_input)
    return thread, run


def pretty_print(messages):
    print("# messages")
    print(messages)
    # 这里由于beta版本，无法正确解析 图片内容 ，只能暂时打印出整个内容
    for m in messages:
        try:
            print(f"{m.role}: {m.content[0].text.value}")
        except:
            print(f"{m.role}: {m.content}")
    print()


def run_submit_tool_outputs(thread, run, tool_outputs):
    return openai.beta.threads.runs.submit_tool_outputs(
        thread_id=thread.id,
        run_id=run.id,
        tool_outputs=tool_outputs
    )


# waiting a loop
def wait_on_run(run, thread):
    while run.status == "queued" or run.status == "in_progress":
        print("run.status::", run.status)
        run = openai.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
        time.sleep(0.5)
    print("run.status::", run.status)
    if run.status == "requires_action":
        print("run: ", run)
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
        run = run_submit_tool_outputs(thread, run, tool_outputs)
        run = wait_on_run(run, thread)
    return run

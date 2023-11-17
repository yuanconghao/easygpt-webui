import openai

functions = [
    {
        "type": "function",
        "function": {
            "name": "get_teaching_image",
            "description": "当你需要教材的图片时，返回对应的图片",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "the topic of the class"},
                    "type": {"type": "string", "enum": ["正式课", "体验课"]},
                    "level": {"type": "string", "enum": ["S", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]},
                    "stage": {"type": "string", "description": "这节课当前的stage，通常是数字，需要你从目前的对话信息中总结出来"}
                },
                "required": ["topic", "type", "level", "stage"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_teaching_schedule",
            "description": "获取这节课的教学计划",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "the topic of the class"},
                    "type": {"type": "string", "enum": ["正式课", "体验课"]},
                    "level": {"type": "string", "enum": ["S", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]}
                },
                "required": ["topic", "type", "level"]
            }
        }
    }
]


def get_teaching_schedule(topic: str, type: str, level: str):
    """
    获取教学计划fuction

    args:

            topic 课程主题
            type 课程类型
            level 课程等级
    """
    return """\
主题：Colorful toys
核心词汇：a pink doll a brown teddy bear, a blue truck, a green monster
核心句法：Do you like this pink doll. Yes, I do./ No, I don't.
目标：通过学习可以让学生能够在日常生活中运用核心词汇和核心表达。
课程流程：
    本课有三个stage，每个stage需要展示图片，然后根据图片内容与学生进行对话练习，并在对话过程中确定是否已经掌握。
    stage1: 通过展示图片，让学生学习核心词汇，然后进行对话练习。
    stage2: 通过展示图片，让学生学习核心句法，然后进行对话练习。
    stage3: 通过展示图片，让学生学习核心句法，然后进行对话练习。
"""


def get_teaching_image(topic: str, type: str, level: str, stage: int):
    """
    获取教材fuction

    args:

            topic 课程主题
            type 课程类型
            level 课程等级
    """
    print("get_teaching_image")
    print("topic:", topic)
    print("type:", type)
    print("level:", level)
    print("stage:", stage)
    # return "path of image stage{}".format(stage)
    return "https://i.ibb.co/LxqWzT2/stage1.jpg"


# step2 create a thread
thread = openai.beta.threads.create()

print(thread)

content = input("User:")
while True:

    # step3 add a message to a thread
    message = openai.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=content
    )

    print(message)

    # step4 run the assistant
    run = openai.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id="asst_fPLHb5lL8cW9eI7Lk0uy32Db",
    )

    run_status = openai.beta.threads.runs.retrieve(
        thread_id=thread.id,
        run_id=run.id
    )
    while True:
        if run_status.status == "completed":
            messages = openai.beta.threads.messages.list(
                thread_id=thread.id
            )
            break

        if run_status.status == "requires_action":
            tool_call = run_status.required_action.submit_tool_outputs.tool_calls[0]
            tool_outputs = []
            if tool_call.function.name == "get_teaching_image":
                topic = "Colorful toys"
                type = "体验课"
                level = "Level1"
                stage = "stage1"
                image_url = get_teaching_image(topic, type, level, stage)
                tool_outputs.append(
                    {
                        "tool_call_id": tool_call.id,
                        "output": image_url
                    }
                )
            elif tool_call.function.name == "get_teaching_schedule":
                topic = "Colorful toys"
                type = "体验课"
                level = "Level1"
                teaching_schedule = get_teaching_schedule(topic, type, level)
                tool_outputs.append(
                    {
                        "tool_call_id": tool_call.id,
                        "output": teaching_schedule
                    }
                )

            if tool_outputs:
                run = openai.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread.id,
                    run_id=run.id,
                    tool_outputs=tool_outputs
                )

        run_status = openai.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
        print(run_status.status)

    print("Teacher:", messages.data[0].content[0].text.value)

    content = input("User:")

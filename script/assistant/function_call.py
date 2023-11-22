functions = [
    {
        "type": "function",
        "function": {
            "name": "get_teaching_image",
            "description": "当你需要教材的图片时，返回对应的图片",
            "parameters": {
                "type": "object",
                "properties": {
                    "type": {"type": "string", "description": "课程类型", "enum": ["正式课", "体验课"]},
                    "level": {"type": "string", "description": "课程级别",
                              "enum": ["S", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]},
                    "topic": {"type": "string", "description": "课程话题"},
                    "lesson": {"type": "string", "description": "课程题目"},
                    "stage": {"type": "string", "description": "这节课当前的stage，通常是数字，需要你从目前的对话信息中总结出来"}
                },
                "required": ["type", "level", "topic", "lesson", "stage"]
            }
        }
    },
]


def get_teaching_image(type, level, topic, lesson, stage):
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
    return "path of image stage{}".format(stage)

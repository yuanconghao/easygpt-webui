import json

functions = [
    {
        "type": "function",
        "function": {
            "name": "get_teaching_stage_image",
            "description": "获取指定stage的图片时，调用这个function，它会返回图片的路径, 获得路径之后需要利用Code interpreter将图片显示出来",
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
    },
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
体验课Level1 Colorful Toys 

知识点：
核心词汇为：a pink doll a brown teddy bear, a blue truck, a green monster 
核心句法为：Do you like this pink doll. Yes, I do./ No, I don\'t.

本课要求：
本课共有3个stage，根据每个stage的要求，进行相关图片展示、对话练习。
Make sure each stage's goals reached then move to the next stage.

Stage 1
图片内容：Timmy holding a brown teddy bear, saying ”It’s a brown teddy bear”
教学目标：Student can understand the meaning, form and pronunciation of the word.
教学流程：
Present the word: Display the stage1's picture in conversation “It’s a brown teddy bear”.
Practice the word: Have the student repeat check the student’s pronunciation. If there is any mistake , correct it.
Meaning check: Ask the student, What is this in Timmy’s hand? Check the answer, and if there is any mistake, please correct it.


Stage 2
图片内容：Timmy holding a brown teddy bear, asking the girl ”Do you like this brown teddy bear?” the girl answer “No, I don’t.”
教学目标：Student can comprehend the meaning of the dialogue and read the sentences.
教学流程：
Present the dialogue: Display stage2's picture in conversation. Introduce the setting and the characters. Ask the student who they are and what Timmy is holding. Have the student listen to the audio.
Practice the dialogue: Have the student repeat the sentences to understand the pronunciation and meaning. Continue until the student can read them accurately and fluently.
Produce the dialogue: Engage in a role-play with the student.


Stage 3
Action:  
图片介绍：图中有四种玩具”a brown teddy bear”,”a green monster”,”a red doll”,”a blue truck” 下方是需要练习的句型 “Do you like … ?” “Yes, I do. / No, I don’t.”
教学目标：Student can apply prescribed sentence structures to express preferences or dislikes.
教学流程：
Present the Activity: Display stage3's picture in conversation and introduce the associated sentence structures.
Produce the Dialogue: Guide the student in asking questions using the sentence structure "Do you like..." Encourage the student to respond based on his/her own opinion. Facilitate role-switching during the activity, with a focus on the student's pronunciation and the correct usage of the sentence structures.
Give Feedback: Assess the student's performance. Provide constructive feedback and correct any mistakes.
"""


def get_teaching_image(topic: str, type: str, level: str, stage: str):
    """
    获取教材fuction
    args:

            topic 课程主题
            type 课程类型
            level 课程等级
    """
    stage1 = json.dumps({"image_file_id": "file-GvMmx0PV63EkoXVvCoWZHsPt"})
    stage2 = json.dumps({"image_file_id": "file-nRElA8UEfNzscZVUpid2SStY"})
    stage3 = json.dumps({"image_file_id": "file-xRsOdAOrrLZKiXYc04VwJp9Q"})
    image_file_id_map = {
        "1": stage1,
        "2": stage2,
        "3": stage3
    }
    return image_file_id_map[stage]


function_map = {
    "get_teaching_schedule": get_teaching_schedule,
    "get_teaching_stage_image": get_teaching_image
}

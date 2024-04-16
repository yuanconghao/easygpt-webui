import sys

sys.path.append("../../")
from server.models.gpt import GPTGenerator
from server.models.prompter import Prompter
import openai
import time

# 假定json_data是上面提供的JSON格式的大纲
json_data = {
    "第一章": {
        "title": "引言",
        "sections": {
            "第一节": "安全威胁环境的复杂性",
            "第二节": "防御者面临的挑战",
            "第三节": "ATT&CK框架简介"
        }
    },
    "第二章": {
        "title": "ATT&CK框架概述",
        "sections": {
            "第一节": "ATT&CK的起源和发展",
            "第二节": "ATT&CK的核心组成：技术、战术和过程",
            "第三节": "ATT&CK在安全领域的应用"
        }
    },
    "第三章": {
        "title": "技术利用方式的详细介绍",
        "sections": {
            "第一节": "ATT&CK中的技术分类",
            "第二节": "利用方式的具体描述",
            "第三节": "对防御者的指导意义"
        }
    },
    "第四章": {
        "title": "为何了解技术对防御者至关重要",
        "sections": {
            "第一节": "提升防御者的安全意识",
            "第二节": "增强企业的安全防护能力",
            "第三节": "缩短对新威胁的响应时间"
        }
    },
    "第五章": {
        "title": "ATT&CK在企业安全中的作用",
        "sections": {
            "第一节": "重要性的平台和数据源",
            "第二节": "监控系统与数据收集的指南",
            "第三节": "减轻和检测入侵技术滥用的影响"
        }
    },
    "第六章": {
        "title": "ATT&CK场景示例的应用",
        "sections": {
            "第一节": "场景示例的作用",
            "第二节": "具体技术的场景分析",
            "第三节": "通过示例学习攻击者行为"
        }
    },
    "第七章": {
        "title": "ATT&CK示例的信息来源",
        "sections": {
            "第一节": "Wikipedia风格的引用方法",
            "第二节": "利用博客和安全研究文章",
            "第三节": "扩展阅读与深入研究"
        }
    },
    "第八章": {
        "title": "如何有效使用ATT&CK框架",
        "sections": {
            "第一节": "定制化防御策略",
            "第二节": "进行安全演练和培训",
            "第三节": "持续的安全监测与改进"
        }
    },
    "第九章": {
        "title": "结论",
        "sections": {
            "第一节": "ATT&CK的价值重申",
            "第二节": "未来趋势和预期发展",
            "第三节": "防御者行动的呼吁"
        }
    },
    "第十章": {
        "title": "附录",
        "sections": {
            "第一节": "ATT&CK资源链接",
            "第二节": "相关安全工具和平台",
            "第三节": "推荐阅读列表"
        }
    }
}

def generate_content(instruct):
    model = "gpt-4-1106-preview"
    conversation = []
    prompt = {'content': instruct, 'role': 'user'}
    images = []
    messages = Prompter.build_messages(model, conversation, prompt, images)

    response = openai.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.5,
        max_tokens=4096,
        stream=False,
    )
    answer = response.choices[0].message.content
    return answer

# 遍历所有章节和小节
for chapter_key, chapter_value in json_data.items():
    chapter_title = chapter_key
    for section_key, section_title in chapter_value['sections'].items():
        instruct = f"你是我的报告生成助手，帮我生成标题为《ATT&CK框架：为防御者揭示技术利用方式的重要性》的报告章节，" \
                 f"我会提供每个章节的标题: {chapter_title} {section_key} {section_title}，" \
                 f"你要对该章节进行续写，尽量写的细致，详细些。不要续写，只能写提供的章节标题的内容，并且每个子章节内容不能少于2000字数。直接将结果输出，不要多余的废话。"
        print(instruct)
        answer = generate_content(instruct)

        # 打开文件并追加内容
        with open('articles.txt', 'a', encoding='utf-8') as file:
            file.write(answer)
        # 模拟一些延迟
        time.sleep(1)  # 等待1秒





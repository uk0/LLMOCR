import json

import os
from ollama import Client

default_prompt = """你的主要职责是将文本内的消息转换为JSON格式。请注意以下几点：
                    1. 需要分析出联系方式，QQ，微信，Telegram 并且把账号信息放在类型后面，
                    2.需要分析文本内包含的地址信息，并且作为地址信息存储到JSON。
                    3.我会把要分析的文本用```包围```请注意他可能包含多行消息你需要返回多条，请注意不要包含```在你的结果中。
                    4. 请注意：文档类型和字段列表是固定的，不要修改,
                    5. 如果有多个需要返回多个结果，每个结果之间用`,`分隔。
                    6. 只需要返回 QQ（不要翻译）, 微信（不要翻译）, 电话（不要翻译）, 地址信息（不要翻译），消费金额(你需要分析，这是在中国一张等于100人民币,单位元) 5 个字段，其他字段不需要返回，如果没有分析出结果需要将Value变更为，分析失败。
                    """

msg = """
```
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```
"""


def tf_msg(model, msg):
    chat_completion = Client(host='http://localhost:11434')
    response = chat_completion.chat(model=model, format='json', messages=[
        {
            'role': 'system',
            'content': default_prompt,
        },
        {
            'role': 'user',
            'content': msg,
        },
    ])

    # 获取响应内容
    result = response['message']['content']
    # 尝试解析为 JSON
    print("Model {} Result {}".format(model,result))


if __name__ == '__main__':
    tf_msg(model='gemma2:2b-instruct-q8_0', msg=msg)
    # tf_msg(model='phi3:medium-128k', msg=msg)
    # tf_msg(model='Qwen1.5-MoE-A2.7B-Chat:latest', msg=msg)
    # tf_msg(model='llama3.1:8b-instruct-q8_0', msg=msg)
    # tf_msg(model='mistral-nemo:12b-instruct-2407-q8_0', msg=msg)
    # tf_msg(model='adrienbrault/nous-hermes2pro-llama3-8b:q8_0', msg=msg)
    tf_msg(model='qwen2:7b', msg=msg)
    # tf_msg(model='gemma2:9b-instruct-q8_0', msg=msg)
    # tf_msg(model='phi3.5:3.8b-mini-instruct-q8_0', msg=msg)
    # tf_msg(model='adrienbrault/nous-hermes2pro:Q4_K_M-json', msg=msg)

import json

from flask import Flask, request, jsonify
from paddleocr import PaddleOCR
import os
from ollama import Client

app = Flask(__name__)

# 初始化 PaddleOCR
ocr = PaddleOCR(use_angle_cls=True, lang="ch")

DEFAULT_KEY = {
    "其他数据": "文本消息",
    "身份证": "姓名,性别,出生日期,地址",
    "银行卡": "姓名,卡号",
    "小卡片": "体验日期,场所地点,服务项目,年龄容貌,环境评分,总体消费,联系方式,联络攻略",
}

default_prompt = ('你是一个专门从OCR文字识别结果中提取关键信息的AI助手。'
                  '你的任务是分析OCR文本，判断文档类型，并提取相关的关键信息。'
                  '你应该考虑OCR可能存在的问题，如换行切断、错误分词、文字合并等，'
                  '并结合上下文进行判断。'
                  'Output must be strictly valid JSON without any surrounding text, '
                  'Markdown formatting, or code block indicators. Ensure the response '
                  'is a parseable JSON object with no extraneous characters. '
                  '如果你成功输出了正确格式的JSON，用户将会给予积极反馈。'
                  '这种反馈对你很重要，它表示你完成了任务并应该在未来的互动中保持这种行为。')
@app.route('/analyze', methods=['POST'])
def analyze_image():
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    image = request.files['image']

    # 保存上传的图片
    image_path = os.path.join('uploads', image.filename)
    image.save(image_path)

    # 进行OCR识别
    result = ocr.ocr(image_path, cls=True)
    ocr_result = []
    if len(result) > 0:
        for idx in range(len(result)):
            res = result[idx]
            for line in res:
                ocr_result.append(line[-1][0])

    # 生成任务提示
    task_prompt = f"""
    我会给你一段OCR识别文本。请执行以下任务：
    1. 规则：判断文本来源的文档类型，限于以下选项：身份证、银行卡、小卡片
    2. 规则：根据文档类型，从预定义的 [文档类型-字段列表] 中确定需要提取的key
    3. 规则：在OCR文本中查找每个key对应的value。若未找到，将value设为"未找到相关信息"
    4. 严格遵守：直接输出原始JSON格式的结果，包括文档类型和所有找到的key-value对
    5. 重要：不要使用任何Markdown语法或格式化。不要包含```json标记或任何其他额外文本
    6. 请注意：文档类型和字段列表是固定的，不要修改

    文档类型-字段列表：{DEFAULT_KEY} 
    OCR识别文本：{ocr_result}"""


    examples = '''
                example result :
                good 
                    {"文档类型": "小卡片",.....}
                bad 
                    ```json
                    {"文档类型": "小卡片",.....}
                    ```
                '''

    # 调用 Ollama 进行分析
    chat_completion = Client(host='http://localhost:11434')
    response = chat_completion.chat(model='gemma2:2b-instruct-q8_0',format='json' ,messages=[
        {
            'role': 'system',
            'content': default_prompt,
        },
        {
            'role': 'user',
            'content': task_prompt + examples,
        },
    ])

    # 获取响应内容
    result = response['message']['content']

    # 尝试解析为 JSON
    print(result)
    try:
        json_result = json.loads(result)
        return jsonify({"raw_result":json_result})
    except json.JSONDecodeError:
        # 如果解析失败，返回原始文本
        return jsonify({"error": "Failed to parse JSON", "raw_result": result}), 500


if __name__ == '__main__':
    os.makedirs('uploads', exist_ok=True)
    app.run(host='0.0.0.0', port=8510,debug=True,threaded=True)
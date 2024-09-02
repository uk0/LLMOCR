import json

from flask import Flask, request, jsonify
from paddleocr import PaddleOCR
import os
from ollama import Client

app = Flask(__name__)

# 初始化 PaddleOCR
ocr = PaddleOCR(use_angle_cls=True, lang="ch")

DEFAULT_KEY = {
     # "CT检查报告单": "患者姓名,性别,年龄,检查日期,检查部位,检查编号,临床诊断,检查方法,造影剂使用情况,检查表现,诊断意见,医生签名,报告日期,检查设备型号,特殊说明,随访建议",    "身份证": "姓名,性别,出生日期,地址",
    # "银行卡": "姓名,卡号,日期",
    "小卡片": "体验日期,场所地点,服务项目,年龄容貌,环境评分,总体消费,联系方式,联络攻略",
    # "中华人民共和国机动车驾驶证": "姓名,性别,住址,出生日期,初次领证日期,有效期限,准驾车型,证号,交通管理局",
    "身份证正面": "姓名,性别,住址,出生日期,公民身份证号码,民族",
    "身份证反面": "签发机关,有效期起,有效期止"
}

default_prompt = ('你是一个专门从OCR文字识别结果中提取关键信息的AI助手。'
                  '你的任务是分析OCR文本，判断文档类型，并提取相关的关键信息。'
                  '你应该考虑OCR可能存在的问题，如换行切断、错误分词、文字合并等，'
                  '并尝试从中提取出文档类型和关键信息。')
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
    print("----------------------------------------------------------------------------------")
    print(ocr_result)
    # 生成任务提示
    task_prompt = f"""
    OCR识别文本，请按照以下规则执行任务：
    0. 规则：你需要在```包围的内容严格的按照{DEFAULT_KEY}的 JSON Key Value 进行筛选关键信息
    1. 规则：判断文本来源的文档类型，限于以下选项：```身份证反面 || 身份证正面 || 小卡片```，并提取关键信息
    2. 规则：根据文档类型，从预定义的 `文档类型-字段列表` 中确定需要提取的key
    3. 规则：在OCR文本中查找每个key对应的value。若未找到，你需要尝试分析，如果分析结果较差则将value设为"未找到相关信息"
    4. 规则：直接输出原始JSON格式的结果，包括文档类型和所有找到的key-value对
    现在开始：请根据以下内容提取关键信息
    ```{ocr_result}```"""


    examples = '''
                Example Result :
                
                Good:
                    {"文档类型": "身份证反面或身份证正面或小卡片",.....}
                    
                Bad:
                    ```json
                    {"文档类型": "身份证反面或身份证正面或小卡片",.....}
                    ```
                '''

    # 调用 Ollama 进行分析
    chat_completion = Client(host='http://localhost:11434')
    response = chat_completion.chat(model='gemma2:9b-instruct-q8_0',format='json' ,options={
        'temperature': 0.1
    },messages=[
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
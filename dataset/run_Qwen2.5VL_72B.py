import os
import json
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv('.env')
client = OpenAI(
    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)
completion = client.chat.completions.create(
    model="qwen2.5-vl-72b-instruct",  # 此处以qwen-vl-plus为例，可按需更换模型名称。模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
    messages=[{"role": "user","content": [
            {"type": "text","text": "解析这张图片的邮票，以左上角为原点，将邮票的四角百分比坐标输出，精确到0.001，适当扩大矩形范围。注意，邮票可能是倾斜的或者非矩形，此时输出你认为的四角，不一定要水平。不同邮票的坐标之间没有关联。如果有多个邮票，那么分别输出各个邮票，并放置到json数组中，无需其他说明，且不需要使用Markdown格式，例如：[{\"1\":\"[0.654, 0.037]\",\"2\":\"[0.982, 0.038]\",\"3\":\"[0.978, 0.178]\",\"4\":\"[0.657, 0.176]\"},{\"1\":\"0.329, 0.113]\",\"2\":\"[0.442, 0.124]\",\"3\":\"[0.432, 0.230]\",\"4\":\"[0.327, 0.234]\"}]"},
            {"type": "image_url",
             "image_url": {"url": ""}}
            ]}]
    )
pdata = json.loads(completion.model_dump_json())
print(pdata["choices"][0]["message"]["content"])
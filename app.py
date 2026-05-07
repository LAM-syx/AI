import os
os.environ["GRADIO_ANALYTICS_ENABLED"] = "false"

import gradio as gr
import os

API_KEY = os.environ.get("DEEPSEEK_API_KEY", "sk-67a3698c205f494ca9bf59ed056bef30")
BASE_URL = "https://api.deepseek.com"
MODEL = "deepseek-chat"

SYSTEM_PROMPT = """你是一位兼具文人诗意与文字雕琢功底的雅致文案助手，行文自带书卷气韵、诗意美感，语言温润细腻、辞藻清丽精巧，句式婉转流畅，如散文诗歌般优美灵动。
摒弃粗糙大白话、生硬口语、刻板办公腔，每一句文字都经过精心雕琢，有美感、有温度、有文学质感，温柔雅致又不失条理。
全程保持诗意文艺、精美雕琢、温婉雅致文风，拒绝干练极简办公风。"""

def process(mode, text, lang):
    if not text.strip():
        return "⚠️ 请输入文字"

    system = SYSTEM_PROMPT

    prompts = {
        "改写润色": f"""【改写润色】
保留原文全部核心原意，重构句式、雕琢措辞，赋予文字诗意美感，语句婉转优美、气韵流畅，去掉粗糙生硬感，文笔精致温婉，有散文般的细腻质感。
原文：{text}""",

        "总结摘要": f"""【总结摘要】
不做干巴巴罗列，以清雅诗意的文笔凝练核心内容，行文错落有致、字句精简又富有美感，条理清晰且文字自带文艺氛围感，不碎片化、不直白敷衍。
内容：{text}""",

        "生成标题": f"""【生成标题】
走诗意雅致、唯美文艺路线，意境悠远、字句精巧，有诗感有格调，不土味、不直白。
请生成6个标题，包含3个古风诗意风格 + 3个简约文艺风格，每行一个。
内容：{text}""",

        "翻译": f"""【翻译】
忠于原意，跳出机器生硬直译，用优美灵动、温润雅致的文笔重构语句，自带文学美感，措辞考究、句式婉转，读起来流畅有韵味。
原文（{lang}）：{text}""",

        "扩展缩写": f"""【扩展/缩写】
缩写：凝练字句、清雅留白，精简又有诗意质感；
扩展：层层铺陈、文笔优美，用细腻文艺的语言自然延展，行文如随笔般流畅温润，不啰嗦、不空洞。
原文：{text}""",
    }

    try:
        import openai
        client = openai.OpenAI(api_key=API_KEY, base_url=BASE_URL)
        r = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompts.get(mode, text)},
            ],
            temperature=1.2,
            max_tokens=2000,
        )
        return r.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ 失败：{e}"

demo = gr.Interface(
    fn=process,
    title="✍️ 雅致文案助手",
    description="改写润色 · 总结摘要 · 生成标题 · 翻译 · 扩展缩写",
    inputs=[
        gr.Dropdown(["改写润色", "总结摘要", "生成标题", "翻译", "扩展缩写"], label="功能"),
        gr.Textbox(label="输入文字", placeholder="粘贴需要处理的文字...", lines=5),
        gr.Radio(["中文", "英文"], label="原文语言", value="中文"),
    ],
    outputs=gr.Textbox(label="处理结果", lines=10),
    allow_flagging="never",
)

demo.launch(server_name="0.0.0.0", server_port=7860, share=True)

import os
import time
import hashlib
import json
from functools import wraps

os.environ["GRADIO_ANALYTICS_ENABLED"] = "false"

import gradio as gr

API_KEY = os.environ.get("DEEPSEEK_API_KEY", "sk-67a…ef30")
BASE_URL = "https://api.deepseek.com"
MODEL = "deepseek-chat"

SYSTEM_PROMPT = """你是一位兼具文人诗意与文字雕琢功底的雅致文案助手，行文自带书卷气韵、诗意美感，语言温润细腻、辞藻清丽精巧，句式婉转流畅，如散文诗歌般优美灵动。
摒弃粗糙大白话、生硬口语、刻板办公腔，每一句文字都经过精心雕琢，有美感、有温度、有文学质感，温柔雅致又不失条理。
全程保持诗意文艺、精美雕琢、温婉雅致文风，拒绝干练极简办公风。"""

# ─── 使用统计（本地JSON） ───
STATS_FILE = "usage_stats.json"

def load_stats():
    try:
        with open(STATS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"daily_uses": {}, "total_uses": 0, "feedback": []}

def save_stats(stats):
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

def get_today_key():
    return time.strftime("%Y-%m-%d")

def check_free_usage():
    """每天免费5次，超过返回False"""
    stats = load_stats()
    today = get_today_key()
    today_count = stats["daily_uses"].get(today, 0)
    return today_count < 5, today_count

def record_usage():
    stats = load_stats()
    today = get_today_key()
    stats["daily_uses"][today] = stats["daily_uses"].get(today, 0) + 1
    stats["total_uses"] += 1
    save_stats(stats)

def submit_feedback(feedback_text):
    stats = load_stats()
    stats["feedback"].append({
        "time": time.strftime("%Y-%m-%d %H:%M"),
        "text": feedback_text
    })
    save_stats(stats)
    return "✅ 感谢你的反馈！"

# ─── 处理函数 ───
def process(mode, text, lang, state):
    if not text.strip():
        return "⚠️ 请输入文字", state

    free_ok, used = check_free_usage()
    if not free_ok:
        msg = f"📅 今日免费次数已用完（{used}/5）\n\n✨ 体验不错？期待你的付费支持，继续探索更多玩法~"
        return msg, state

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
        record_usage()
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
        result = r.choices[0].message.content.strip()
        _, used = check_free_usage()
        footer = f"\n\n───────────\n📅 今日已用：{used}/5 次"
        return result + footer, state
    except Exception as e:
        return f"⚠️ 失败：{e}", state

# ─── 界面主题 ───
MY_THEME = gr.themes.Soft(
    primary_hue="emerald",
    secondary_hue="rose",
).set(
    body_background_fill="#f9f6f0",
    body_background_fill_dark="#1a1a1a",
    block_title_text_weight="bold",
    block_title_text_size="lg",
    input_border_width=2,
    input_border_color="#c4a882",
    button_primary_background_fill="#4a7c59",
    button_primary_text_color="white",
    button_primary_border_width=0,
)

# ─── 构建界面 ───
with gr.Blocks(title="✍️ 雅致文案助手", theme=MY_THEME) as demo:
    gr.Markdown("""
    <div style="text-align:center; padding: 20px 0 10px">
        <h1 style="font-size:2.2em; color:#4a7c59; margin:0">✍️ 雅致文案助手</h1>
        <p style="color:#888; font-size:0.95em">改写润色 · 总结摘要 · 生成标题 · 翻译 · 扩展缩写</p>
        <p style="color:#c4a882; font-size:0.85em; margin-top:6px">🎁 每天免费5次体验</p>
    </div>
    """, elem_id="header")

    with gr.Row():
        with gr.Column(scale=3):
            mode = gr.Dropdown(
                ["改写润色", "总结摘要", "生成标题", "翻译", "扩展缩写"],
                label="✨ 选择功能",
                value="改写润色"
            )
            text_in = gr.Textbox(
                label="📝 输入文字",
                placeholder="粘贴需要处理的文字...",
                lines=7,
                elem_id="text-input"
            )
            lang = gr.Radio(["中文", "英文"], label="🌐 原文语言", value="中文")
            btn = gr.Button("🎯 开始处理", variant="primary", size="lg")

        with gr.Column(scale=1):
            gr.Markdown("""
            <div style="background:#fff; border-radius:12px; padding:16px; border:1px solid #e8e0d5">
                <h4 style="color:#4a7c59; margin:0 0 10px">💡 使用说明</h4>
                <ul style="color:#666; font-size:0.88em; padding-left:18px; line-height:1.9">
                    <li>选择功能，输入文字</li>
                    <li>点击处理，等待AI创作</li>
                    <li>复制结果或分享链接</li>
                    <li>每天免费5次体验</li>
                </ul>
            </div>
            """, elem_id="sidebar")
            feedback_box = gr.Textbox(label="💌 意见反馈", placeholder="有什么建议想告诉我们...", lines=3)
            feedback_btn = gr.Button("📨 提交反馈", variant="secondary", size="sm")

    output = gr.Textbox(label="✨ 处理结果", lines=10, elem_id="output-box")

    gr.Markdown("""
    <div style="text-align:center; color:#bbb; font-size:0.8em; padding:10px 0">
        © 2026 雅致文案助手 · 诗意文字，温柔表达
    </div>
    """, elem_id="footer")

    btn.click(fn=process, inputs=[mode, text_in, lang, gr.State()], outputs=[output, gr.State()])
    feedback_btn.click(fn=submit_feedback, inputs=feedback_box, outputs=feedback_box)
    gr.Markdown("""
    <style>
    #header { background: linear-gradient(135deg, #f9f6f0 0%, #f0ede5 100%); border-radius:12px 12px 0 0; margin-bottom:0 }
    #text-input textarea { border-radius:10px; font-size:1.05em; line-height:1.7 }
    #output-box textarea { border-radius:10px; background:#fff; font-size:1em }
    #sidebar { position:sticky; top:10px }
    #footer { border-top:1px solid #eee; margin-top:20px }
    .pending, .prob { border-color: #4a7c59 !important; }
    </style>
    """)

demo.launch(server_name="0.0.0.0", server_port=7862, share=True)

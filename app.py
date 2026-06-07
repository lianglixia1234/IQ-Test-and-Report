import streamlit as st
import pandas as pd
import time
from pathlib import Path
from PIL import Image
from datetime import datetime
from github import Github
from io import StringIO
from streamlit_autorefresh import st_autorefresh

# 🌟 从你自己写的 report.py 文件中，导入这两个核心函数
from report import calculate_report_data, generate_report_html
# 加载你的资产文件
@st.cache_data
def load_report_assets():
    norm_df = pd.read_csv("Norm.xlsx - Sheet1.csv", encoding="utf-8")
    text_df = pd.read_csv("text.xls - Sheet1.csv", encoding="utf-8")
    return norm_df, text_df

norm_df, text_df = load_report_assets()


# ==============================================================================
# 🌟 极致空间优化：消除顶部留白 + 选项按钮样式
# ==============================================================================
st.markdown("""
<style>
/* 消除 Streamlit 默认的顶部大留白 */
.block-container {
    padding-top: 1rem !important;
    padding-bottom: 0rem !important;
}
/* 紧凑化标题和组件之间的间距 */
div[data-testid="stVerticalBlock"] > div {
    padding-bottom: 0.5rem !important;
}
/* 单选框样式 */
div[role="radiogroup"] > label {
    background-color:#f5f5f5;
    border:2px solid #cccccc;
    border-radius:8px;
    padding:6px 15px;
    margin-right:8px;
    font-size:20px !important;
    font-weight:bold;
}
div[role="radiogroup"] {
    flex-direction:row;
}
</style>
""", unsafe_allow_html=True)

# ==========================
# 读取题库
# ==========================
@st.cache_data
def load_questions():
    df = pd.read_csv("questions.csv", encoding="gb18030")
    return df.sort_values("Question_ID").reset_index(drop=True)

questions = load_questions()

# 预加载图片
@st.cache_resource
def preload_images():
    images = {}
    for _, row in questions.iterrows():
        p = Path("IQ_Test_Picture") / str(row["Image"])
        images[str(row["Image"])] = Image.open(p)
    return images

images = preload_images() # 放到全局或按需调用

# ==========================
# Session State 初始化
# ==========================
defaults = {
    "page": "info",
    "start_time": None,
    "current_question": 0,
    "answers": {},
    "submitted": False
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# 保存到 GitHub 函数
def save_to_github(output):
    g = Github(st.secrets["GITHUB_TOKEN"])
    repo = g.get_repo(f"{st.secrets['GITHUB_OWNER']}/{st.secrets['GITHUB_REPO']}")
    try:
        file = repo.get_contents("record.csv")
        old_csv = file.decoded_content.decode("utf-8-sig")
        old_df = pd.read_csv(StringIO(old_csv))
        merged_df = pd.concat([old_df, output], ignore_index=True)
        new_csv = merged_df.to_csv(index=False, encoding="utf-8-sig")
        repo.update_file(path="record.csv", message="Add IQ result", content=new_csv, sha=file.sha)
    except Exception:
        new_csv = output.to_csv(index=False, encoding="utf-8-sig")
        repo.create_file(path="record.csv", message="Create record.csv", content=new_csv)

# ==========================
# 提交测试
# ==========================
def submit_test():
    if st.session_state.get("submitted", False):
        return

    st.session_state.submitted = True
    result = {
        "Name": st.session_state["name"],
        "Sex": st.session_state["gender"],
        "Age": st.session_state["age"],
        "Date": st.session_state["test_date"]
    }

    duration_seconds = int(time.time() - st.session_state.start_time)
    result["Duration_Seconds"] = duration_seconds

    total_score = 0
    factor_scores = {}

    for _, row in questions.iterrows():
        item = str(row["Item"])
        user_answer = st.session_state.answers.get(item, "未作答")
        result[f"{item}_raw_response"] = user_answer

    for _, row in questions.iterrows():
        item = str(row["Item"])
        factor = str(row["Factor"])
        correct_answer = str(row["Answer"])
        user_answer = str(st.session_state.answers.get(item, "未作答"))

        is_correct = 1 if user_answer == correct_answer else 0
        result[f"{item}_response"] = is_correct
        total_score += is_correct

        if factor not in factor_scores:
            factor_scores[factor] = 0
        factor_scores[factor] += is_correct

    for factor, score in factor_scores.items():
        result[f"{factor}_Score"] = score

    result["Total_Score"] = total_score
    output = pd.DataFrame([result])
    st.session_state.result_df = output
    
    try:
        save_to_github(output)
    except Exception as e:
        st.error(f"GitHub同步失败: {e}")

    record_path = Path("record.csv")
    if record_path.exists():
        output.to_csv(record_path, mode="a", header=False, index=False, encoding="utf-8-sig")
    else:
        output.to_csv(record_path, index=False, encoding="utf-8-sig")

# ==========================
# 页面1：登记
# ==========================
if st.session_state.page == "info":
    st.title("📝 信息登记")

    name = st.text_input("姓名")
    gender = st.selectbox("性别", ["男", "女"])
    ages = [x / 2 for x in range(11, 141)]
    age = st.selectbox("年龄（下拉选择整岁或者半岁）", ages)
    test_date = st.date_input("测试日期")

    if st.button("进入测试"):
        if not name:
            st.error("请输入姓名")
        else:
            st.session_state["name"] = name
            st.session_state["gender"] = gender
            st.session_state["age"] = age
            st.session_state["test_date"] = test_date.strftime("%Y-%m-%d")
            st.session_state.page = "intro"
            st.rerun()

# ==========================
# 页面2：说明页
# ==========================
elif st.session_state.page == "intro":
    st.header("测试说明")
    st.image("IQ_Test_Picture/introduction.png", width=1400)
    st.info("请认真阅读说明。准备好后点击开始测试。")

    if st.button("开始测试"):
        st.session_state.start_time = time.time()
        st.session_state.page = "test"
        st.rerun()


# ==========================
# 页面3：测试页（全新左右非对称布局）
# ==========================
elif st.session_state.page == "test":
    # 每 2 秒刷新一次，兼顾流畅度与性能
    st_autorefresh(interval=2000, key="timer_refresh")
    
    TOTAL_TIME = 40 * 60
    remaining = max(0, TOTAL_TIME - (time.time() - st.session_state.start_time))
    
    if remaining <= 0:
        if not st.session_state.submitted:
            submit_test()
        st.session_state.page = "finish"
        st.rerun()
    
    idx = st.session_state.current_question
    q = questions.iloc[idx]
    item = str(q["Item"])
    
    # --------------------------------------------------------------------------
    # 🌟 整体分为左右两列：左边 8.5成宽度放题目核心，右边 1.5成宽度放翻页按钮
    # --------------------------------------------------------------------------
    main_col, side_col = st.columns([8.5, 1.5])
    
    # ==========================
    # 【左侧大区域】：信息 + 图片 + 选项
    # ==========================
    with main_col:
        # 1. 上方：题目数 + 时间并排
        top_col1, top_col2 = st.columns([2, 1])
        with top_col1:
            st.markdown(f"### 📝 第 {idx+1} / {len(questions)} 题")
        with top_col2:
            st.markdown(
                f"<div style='text-align:right; font-size:24px; color:red; font-weight:bold; margin-top:-2px;'> "
                f"⏳ {int(remaining//60):02d}:{int(remaining%60):02d}"
                f"</div>",
                unsafe_allow_html=True
            )
        
        # 2. 中间：题目图片
        img_key = str(q["Image"])
        if img_key in images:
            st.image(images[img_key], use_container_width=True)
        else:
            st.error(f"❌ 未找到图片: {img_key}")
            
        # 3. 底部：选项（紧跟在图片下方）
        option_num = int(q["Options"])
        choices = ["未作答"] + [str(i) for i in range(1, option_num + 1)]
        
        widget_key = f"question_{idx}"
        if widget_key not in st.session_state:
            st.session_state[widget_key] = st.session_state.answers.get(item, "未作答")
        
        def on_answer_change():
            st.session_state.answers[item] = st.session_state[widget_key]

        answer = st.radio(
            "请选择答案：",
            choices,
            key=widget_key,
            horizontal=True,
            on_change=on_answer_change
        )
        st.session_state.answers[item] = answer

    # ==========================
    # 【右侧小区域】：两行垂直对齐的按钮
    # ==========================
    with side_col:
        # 为了让右侧按钮在视觉上有一些向下的偏移，对齐左侧的图片，可以加一点虚空留白
        st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
        
        def move_page(delta):
            st.session_state.current_question += delta

        # 第一行：上一题按钮
        if idx > 0:
            if st.button("\n◀️ 上一题", width=100, key=f"prev_{idx}"):
                move_page(-1)
                st.rerun()
        else:
            st.button("\n◀️ 上一题", width=100, disabled=True, key="prev_disabled")
        
        # 增加两个按钮之间的垂直间距
        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
        
        # 第二行：下一题/确认完成按钮
        if idx < len(questions) - 1:
            if st.button("\n▶️ 下一题", width=100, key=f"next_{idx}"):
                move_page(1)
                st.rerun()
        else:
            if st.button("✅ 确认完成作答", type="primary", use_container_width=True, key="submit_btn"):
                submit_test()
                st.session_state.page = "finish"
                st.rerun()
# ==========================
# ==========================
# main.py 的页面4 部分

elif st.session_state.page == "finish":
    st.success("🎉 测试已完成！个性化报告已实时生成。")
    
    if "balloon_shown" not in st.session_state:
        st.balloons()
        st.session_state.balloon_shown = True

    # 1. 动态统计出五大因子的得分情况
    factor_scores = {}
    for _, row in questions.iterrows():
        factor = str(row["Factor"])
        item = str(row["Item"])
        correct_answer = str(row["Answer"])
        user_answer = str(st.session_state.answers.get(item, ""))
        is_correct = 1 if user_answer == correct_answer else 0
        factor_scores[factor] = factor_scores.get(factor, 0) + is_correct

    total_score = sum(factor_scores.values())

    # 2. 核心调用：使用跨文件导入的计算函数清洗数据
    user_name = st.session_state.get("name", "测试者")
    report_data = calculate_report_data(
        name=user_name,
        gender=st.session_state.get("gender", "男"),
        age=st.session_state.get("age", 10.0),
        test_date=st.session_state.get("test_date", datetime.now().strftime("%Y-%m-%d")),
        total_score=total_score,
        factor_scores=factor_scores,
        norm_df=norm_df,
        text_df=text_df
    )

    # 3. 核心调用：使用跨文件导入的 HTML 函数生成漂亮的前端排版
    report_html = generate_report_html(report_data)
    
    # 渲染到主界面供用户查看
    st.markdown(report_html, unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # 🌟 核心新增：自动将报告上传到 GitHub 的 report/ 文件夹下
    # --------------------------------------------------------------------------
    # 引入我们刚才写在 report.py 里的上传函数
    from report import upload_report_to_github
    
    # 避免页面因 st_autorefresh 刷新导致重复提交，用 session_state 加锁锁住
    github_lock_key = f"uploaded_{st.session_state.start_time}"
    if github_lock_key not in st.session_state:
        # 为当前用户生成一个规范的文件名
        custom_file_name = f"{user_name}_瑞文测验报告_{datetime.now():%Y%m%d_%H%M%S}.html"
        
        # 唤醒上传
        with st.spinner("正在将测试报告安全同步至云端凭证库..."):
            success, msg = upload_report_to_github(custom_file_name, report_html)
            
        if success:
            st.toast(f"✅ 报告已成功加密同步至 GitHub (report/{custom_file_name})")
            st.session_state[github_lock_key] = True  # 激活锁，防止重复上传
        else:
            st.error(f"❌ 报告云端同步失败，原因: {msg}")

    # 4. 原有的用户手动下载按钮保持不变
    st.write(" ")
    st.download_button(
        label="📥 导出并下载独立网页版 HTML 测试报告",
        data=report_html,
        file_name=f"{user_name}_瑞文测验分析报告_{datetime.now():%Y%m%d}.html",
        mime="text/html",
        type="primary"
    )
# 页面4：完成与报告生成页
# ==========================

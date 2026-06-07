import streamlit as st
import pandas as pd
import time
from pathlib import Path
from PIL import Image
from datetime import datetime
from github import Github
from io import StringIO
from streamlit_autorefresh import st_autorefresh

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
    st.title("📝 瑞文智力测验")
    st.subheader("💡 适用于5.5岁及以上")
    st.header("测试登记")

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
    st.image("IQ_Test_Picture/introduction.png", width=1200)
    st.info("请认真阅读说明。准备好后点击开始测试。")

    if st.button("开始测试"):
        st.session_state.start_time = time.time()
        st.session_state.page = "test"
        st.rerun()


# ==========================
# 页面3：测试页
# ==========================
elif st.session_state.page == "test":
    # 每 1 秒刷新一次，兼顾流畅度与性能
    st_autorefresh(interval=1000, key="timer_refresh")
    
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
    # 🌟 核心布局：左边放图片(col_left)，右边放控制台(col_right)
    # --------------------------------------------------------------------------
    col_left, col_right = st.columns([7, 3])
    
    # --- 左侧：题目图片 ---
    with col_left:
        img_key = str(q["Image"])
        if img_key in images:
            # use_container_width=True 让图片自适应左侧容器宽度，防止撑大页面
            st.image(images[img_key], use_container_width=True)
        else:
            st.error(f"❌ 未找到图片: {img_key}")
            
    # --- 右侧：所有操作组件（题号、倒计时、选项、按钮） ---
    with col_right:
        # 1. 题号与倒计时（并排紧凑显示）
        meta_col1, meta_col2 = st.columns([1, 1])
        with meta_col1:
            st.markdown(f"##### 📝 {idx+1} / {len(questions)}")
        with meta_col2:
            st.markdown(
                f"<div style='text-align:right; font-size:22px; color:red; font-weight:bold; margin-top:-2px;'>"
                f"⏳ {int(remaining//60):02d}:{int(remaining%60):02d}"
                f"</div>",
                unsafe_allow_html=True
            )
            
        st.write("---")
        
        # 2. 选择答案区域
        option_num = int(q["Options"])
        choices = ["未作答"] + [str(i) for i in range(1, option_num + 1)]
        
        widget_key = f"question_{idx}"
        if widget_key not in st.session_state:
            st.session_state[widget_key] = st.session_state.answers.get(item, "未作答")
        
        def on_answer_change():
            st.session_state.answers[item] = st.session_state[widget_key]

        # 减小了一点字体和间距，确保右侧不拥挤
        answer = st.radio(
            "请选择答案：",
            choices,
            key=widget_key,
            horizontal=True,
            on_change=on_answer_change
        )
        st.session_state.answers[item] = answer
        
        st.write("---")
        
        # 3. 导航按钮（严格并在同一行，紧跟在单选框下方）
        btn_col1, btn_col2 = st.columns(2)
        
        def move_page(delta):
            st.session_state.current_question += delta

        with btn_col1:
            if idx > 0:
                if st.button("◀️上一题", use_container_width=True, key=f"prev_{idx}"):
                    move_page(-1)
                    st.rerun()
            else:
                st.button("◀️上一题", use_container_width=True, disabled=True, key="prev_disabled")
                
        with btn_col2:
            if idx < len(questions) - 1:
                if st.button("▶️下一题", use_container_width=True, key=f"next_{idx}"):
                    move_page(1)
                    st.rerun()
            else:
                if st.button("✅ 确认完成作答", type="primary", use_container_width=True, key="submit_btn"):
                    submit_test()
                    st.session_state.page = "finish"
                    st.rerun()

# ==========================
# 页面4：完成
# ==========================
elif st.session_state.page == "finish":
    st.success("🎉 测试已完成！")
    
    if "balloon_shown" not in st.session_state:
        st.balloons()
        st.session_state.balloon_shown = True

    duration = int(time.time() - st.session_state.start_time)
    st.write(f"⏱️ 总共完成时间：{duration // 60} 分 {duration % 60} 秒")

    if "result_df" in st.session_state:
        csv_data = st.session_state.result_df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
        st.download_button(
            label="📥 下载测试结果 (CSV)",
            data=csv_data,
            file_name=f"{st.session_state['name']}_{datetime.now():%Y%m%d_%H%M%S}.csv",
            mime="text/csv",
            type="primary"
        )

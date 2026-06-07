import streamlit as st
import pandas as pd
import time
from pathlib import Path
from PIL import Image


# 预加载图片
@st.cache_resource
def load_image(path):
    return Image.open(path)





st.markdown("""
<style>

div[role="radiogroup"] > label {
    background-color:#f5f5f5;
    border:2px solid #cccccc;
    border-radius:8px;
    padding:10px 20px;
    margin-right:10px;
    font-size:24px !important;
    font-weight:bold;
}

div[role="radiogroup"] {
    flex-direction:row;
}

</style>
""",
unsafe_allow_html=True)




# ==========================
# 读取题库
# ==========================

@st.cache_data
def load_questions():

    df = pd.read_csv(
        "questions.csv",
        encoding="gb18030"
    )

    return (
        df.sort_values("Question_ID")
          .reset_index(drop=True)
    )

questions = load_questions()

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



# ==========================
# 提交测试
# ==========================

def submit_test():

    if st.session_state.submitted:
        return

    result = {
        "Name": st.session_state["name"],
        "Sex": st.session_state["gender"],
        "Age": st.session_state["age"],
        "Date": st.session_state["test_date"]
    }

    # 完成时间（秒）
    duration_seconds = int(
        time.time() - st.session_state.start_time
    )

    result["Duration_Seconds"] = duration_seconds

    total_score = 0

    factor_scores = {}

    # ------------------
    # 保存原始作答
    # ------------------

    for _, row in questions.iterrows():

        item = str(row["Item"])

        user_answer = st.session_state.answers.get(
            item,
            ""
        )

        result[
            f"{item}_raw_response"
        ] = user_answer

    # ------------------
    # 计算正确率
    # ------------------

    for _, row in questions.iterrows():

        item = str(row["Item"])

        factor = str(row["Factor"])

        correct_answer = str(row["Answer"])

        user_answer = str(
            st.session_state.answers.get(item, "")
        )

        is_correct = (
            1 if user_answer == correct_answer else 0
        )

        result[
            f"{item}_response"
        ] = is_correct

        total_score += is_correct

        if factor not in factor_scores:
            factor_scores[factor] = 0

        factor_scores[factor] += is_correct

    # ------------------
    # 因素得分
    # ------------------

    for factor, score in factor_scores.items():

        result[f"{factor}_Score"] = score

    # ------------------
    # 总分
    # ------------------

    result["Total_Score"] = total_score

    output = pd.DataFrame([result])


    st.session_state.result_df = output

    record_path = Path("record.csv")

    if record_path.exists():

        output.to_csv(
            record_path,
            mode="a",
            header=False,
            index=False,
            encoding="utf-8-sig"
        )

    else:

        output.to_csv(
            record_path,
            index=False,
            encoding="utf-8-sig"
        )

    st.session_state.submitted = True

# ==========================
# 页面1：登记
# ==========================

if st.session_state.page == "info":

    st.title("📝 瑞文标准智力测验")
    st.subheader("💡 适用于5.5岁及以上")

    
    st.header("测试登记")

    name = st.text_input("姓名")

    gender = st.selectbox(
        "性别",
        ["男", "女"]
    )

    ages = [x / 2 for x in range(11, 141)]

    age = st.selectbox(
        "年龄（下拉选择整岁或者半岁）",
        ages
    )

    test_date = st.date_input(
        "测试日期"
    )

    if st.button("进入测试"):

        if not name:

            st.error("请输入姓名")

        else:

            st.session_state["name"] = name
            st.session_state["gender"] = gender
            st.session_state["age"] = age
            st.session_state["test_date"] = (
                test_date.strftime("%Y-%m-%d")
            )

            st.session_state.page = "intro"

            st.rerun()

# ==========================
# 页面2：说明页
# ==========================

elif st.session_state.page == "intro":

    st.header("测试说明")

    st.image(
        "IQ_Test_Picture/introduction.png",
        width=1000
    )

    st.info(
        "请认真阅读说明。准备好后点击开始测试。"
    )

    if st.button("开始测试"):

        st.session_state.start_time = time.time()

        st.session_state.page = "test"

        st.rerun()

# ==========================
# 页面3：测试页
# ==========================

elif st.session_state.page == "test":
   
    
    TOTAL_TIME = 40 * 60

    elapsed = int(
        time.time()
        - st.session_state.start_time
    )

    remaining = TOTAL_TIME - elapsed

    # ------------------
    # 超时自动提交
    # ------------------

    if remaining <= 0:

        submit_test()

        st.session_state.page = "finish"

        st.rerun()

    minutes = remaining // 60
    seconds = remaining % 60

    idx = st.session_state.current_question
    
    q = questions.iloc[idx]
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
    
        st.markdown(
            f"### 第 {idx+1} 题 / {len(questions)} 题"
        )
    
    with col2:
    
        @st.fragment(run_every="1s")
        def timer():
        
            remaining = (
                TOTAL_TIME
                - (
                    time.time()
                    - st.session_state.start_time
                )
            )
        
            if remaining <= 0:

        
                submit_test()
        
                st.session_state.page = "finish"
        
                st.rerun()
        
            st.markdown(
                f"""
                <div style='text-align:right;
                            font-size:28px;
                            color:red;'>
                ⏳ {int(remaining//60):02d}:{int(remaining%60):02d}
                </div>
                """,
                unsafe_allow_html=True
            )
    
        timer()

    # 图片
    image_path = (
        Path("IQ_Test_Picture")
        / str(q["Image"])
    )

    st.image(
        load_image(image_path),
        width=800
    )

    # 选项
    option_num = int(q["Options"])
    
    choices = ["未作答"] + [
        str(i)
        for i in range(1, option_num + 1)
    ]
    
    item = str(q["Item"])
    
    widget_key = f"question_{idx}"
    
    # 第一次进入该题时恢复历史答案
    if widget_key not in st.session_state:
    
        st.session_state[widget_key] = (
            st.session_state.answers.get(
                item,
                "未作答"
            )
        )
    
    answer = st.radio(
        "请选择答案",
        choices,
        key=widget_key,
        horizontal=True
    )
    
    # 保存当前答案
    st.session_state.answers[item] = answer





    
    # ------------------
    # 导航按钮
    # ------------------

    if idx == 0:

        if st.button("下一题"):

            st.session_state.current_question += 1

            st.rerun()

    elif idx < len(questions) - 1:

        col1, col2 = st.columns(2)

        with col1:

            if st.button("上一题"):

                st.session_state.current_question -= 1

                st.rerun()

        with col2:

            if st.button("下一题"):

                st.session_state.current_question += 1

                st.rerun()

    else:

        col1, col2 = st.columns(2)

        with col1:

            if st.button("上一题"):


                st.session_state.current_question -= 1

                st.rerun()

        with col2:

            if st.button("确认完成作答"):


                submit_test()

                st.session_state.page = "finish"

                st.rerun()

# ==========================
# 页面4：完成
# ==========================

elif st.session_state.page == "finish":

    st.success("测试已完成")

    st.balloons()

    duration = int(
        time.time()
        - st.session_state.start_time
    )

    st.write(
        f"完成时间：{duration // 60}分{duration % 60}秒"
    )

    if "result_df" in st.session_state:

        csv_data = (
            st.session_state.result_df
            .to_csv(
                index=False,
                encoding="utf-8-sig"
            )
            .encode("utf-8-sig")
        )
    
        st.download_button(
            label="📥 下载测试结果",
            data=csv_data,
            file_name=f"{st.session_state['name']}_IQ_Result.csv",
            mime="text/csv"
        )


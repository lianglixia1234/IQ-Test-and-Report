import streamlit as st
import pandas as pd

st.title("🏆瑞文标准智力测验🏆")
st.subtitle("适用于5.5岁及以上")

name = st.text_input(
    "姓名"
)

gender = st.radio(
    "性别",
    ["男", "女"],
    horizontal=True
)

ages = [x / 2 for x in range(5.5, 70)]
# 4.0 ~ 20.0

age = st.selectbox(
    "年龄",
    ages
)

if st.button("开始测试"):

    if not name:
        st.error("请输入姓名")

    else:
        # 保存到 session_state
        st.session_state["name"] = name
        st.session_state["gender"] = gender
        st.session_state["age"] = age

        # 追加到 CSV
        new_record = pd.DataFrame([{
            "Name": name,
            "Sex": gender,
            "Age": age
        }])

        new_record.to_csv(
            "child_answer_record.csv",
            mode="a",
            header=False,   # 文件已有标题列
            index=False,
            encoding="utf-8-sig"
        )

        st.success("信息已保存")

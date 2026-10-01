import streamlit as st

st.set_page_config(
    page_title="signal-lab · 信号与系统交互式实验室",
    page_icon="📡",
    layout="wide",
)

NAV = [
    st.Page("views/home.py", title="首页", icon="🏠", url_path="home", default=True),
    st.Page("views/0_基础信号.py", title="基础信号", icon="📈", url_path="basics"),
    st.Page("views/4_模拟滤波器.py", title="模拟滤波器", icon="🔧", url_path="analog-filters"),
    st.Page("views/5_卷积.py", title="卷积", icon="🌀", url_path="convolution"),
    st.Page("views/6_零极点.py", title="零极点", icon="📍", url_path="pole-zero"),
    st.Page("views/7_三大逼近.py", title="三大逼近", icon="📊", url_path="approximations"),
    st.Page("views/8_数字滤波器.py", title="数字滤波器", icon="🔢", url_path="digital-filters"),
]

st.navigation(NAV).run()

import streamlit as st

st.title("📡 signal-lab")
st.markdown("#### 信号与系统 · 交互式实验室")

st.markdown("""
把《信号与系统》里最抽象的概念，做成**能拖滑块、能看曲线**的交互页面。

每个模块都对着 **浙江大学 085400 电子信息 · 842「信号系统与数字电路」** 的考点来设计 ——
不抄公式，而是让你把参数拖到极端值，**亲眼看着曲线怎么变**。
""")

st.markdown("")

c1, c2, c3, c4 = st.columns(4)
c1.metric("交互模块", "7")
c2.metric("覆盖主线", "变换 · 卷积 · 滤波器")
c3.metric("核心技术", "Streamlit + SciPy")
c4.metric("状态", "已上线")

st.divider()
st.markdown("### 🧭 模块导航")

MODULES = [
    ("views/0_基础信号.py", "📈 基础信号",
     "阶跃、冲激、指数、正弦；时移、反褶、尺度变换"),
    ("views/4_模拟滤波器.py", "🔧 模拟滤波器",
     "幅度平方函数、阻带斜率 −20N dB/十倍频、巴特沃斯低通"),
    ("views/5_卷积.py", "🌀 卷积",
     "图解法的翻转–平移–相乘–积分，LTI 系统的全部内容"),
    ("views/6_零极点.py", "📍 零极点",
     "s 平面极零点如何决定频率响应：距离比公式"),
    ("views/7_三大逼近.py", "📊 三大逼近",
     "巴特沃斯 / 切比雪夫 / 椭圆：同阶数下谁的过渡带最陡"),
    ("views/8_数字滤波器.py", "🔢 数字滤波器",
     "冲激响应不变法 vs 双线性变换，以及频率预畸变"),
]

cols = st.columns(2)
for i, (path, title, desc) in enumerate(MODULES):
    with cols[i % 2]:
        with st.container(border=True):
            st.page_link(path, label=title)
            st.caption(desc)

st.divider()

left, right = st.columns(2)
with left:
    st.markdown("**🔗 相关链接**")
    st.markdown("- GitHub：`github.com/Palpitate-kkkk/signal-lab`")
    st.markdown("- 在线演示：`zju-signal-lab.streamlit.app`")
with right:
    st.markdown("**☕ 使用提示**")
    st.markdown("- 免费版闲置会休眠，首次打开约需唤醒 30 秒")
    st.markdown("- 所有图表可交互：拖拽缩放、悬停查看数值")

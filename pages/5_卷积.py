import numpy as np
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

FONT = "PingFang SC, Hiragino Sans GB, Microsoft YaHei, sans-serif"

TAU = np.linspace(-0.5, 8.0, 901)
DT = TAU[1] - TAU[0]
T_GRID = np.linspace(-0.5, 8.0, 401)


def make_signal(kind, w):
    if kind == "矩形脉冲":
        return np.where((TAU >= 0) & (TAU < w), 1.0, 0.0)
    if kind == "三角脉冲":
        tri = np.clip(1.0 - np.abs(TAU - w / 2) / (w / 2), 0.0, None)
        return np.where((TAU >= 0) & (TAU <= w), tri, 0.0)
    return np.where(TAU >= 0, np.exp(-TAU / w), 0.0)


def style(fig, height=720):
    fig.update_layout(
        height=height,
        font=dict(family=FONT, size=12),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#F8FAFC",
        margin=dict(l=10, r=10, t=50, b=70),
        legend=dict(orientation="h", yanchor="top", y=-0.07, xanchor="center", x=0.5),
    )
    fig.update_xaxes(gridcolor="#E2E8F0", zerolinecolor="#CBD5E1")
    fig.update_yaxes(gridcolor="#E2E8F0", zerolinecolor="#CBD5E1")
    return fig


st.title("⑤ 卷积：把一个信号拆成无数个冲激")
st.caption(
    "卷积不是一个公式，是一个动作：翻转 → 平移 → 相乘 → 求面积。"
    "拖动下面的 t 滑块，看红色的 h 从左往右滑过蓝色的 x。"
)

c1, c2 = st.columns(2)
with c1:
    x_kind = st.selectbox("输入信号 x(τ) 的形状", ["矩形脉冲", "三角脉冲", "指数衰减"])
    x_w = st.slider("x 的宽度 / 时间常数", 0.2, 4.0, 1.0, 0.1)
with c2:
    h_kind = st.selectbox("系统冲激响应 h(τ) 的形状", ["矩形脉冲", "三角脉冲", "指数衰减"])
    h_w = st.slider("h 的宽度 / 时间常数", 0.2, 4.0, 1.0, 0.1)

t = st.slider("当前时刻 t", -0.5, 8.0, 0.5, 0.05)

x = make_signal(x_kind, x_w)
h = make_signal(h_kind, h_w)

H = np.interp((T_GRID[:, None] - TAU[None, :]).ravel(), TAU, h, left=0.0, right=0.0)
H = H.reshape(T_GRID.size, TAU.size)
y = (H * x[None, :]).sum(axis=1) * DT

h_shift = np.interp(t - TAU, TAU, h, left=0.0, right=0.0)
prod = x * h_shift
y_now = float(np.interp(t, T_GRID, y))

fig = make_subplots(
    rows=3,
    cols=1,
    subplot_titles=(
        "① x(τ) 与翻转平移后的 h(t-τ)",
        "② 乘积 x(τ)·h(t-τ)：绿色面积就是这一时刻的卷积值",
        f"③ 卷积结果 y(t)　　当前 t = {t:.2f}，y(t) = {y_now:.3f}",
    ),
    vertical_spacing=0.12,
)

fig.add_trace(
    go.Scatter(x=TAU, y=x, name="x(τ)", line=dict(color="#1E40AF", width=2.5)),
    row=1,
    col=1,
)
fig.add_trace(
    go.Scatter(x=TAU, y=h_shift, name="h(t-τ)", line=dict(color="#DC2626", width=2.5)),
    row=1,
    col=1,
)
fig.add_trace(
    go.Scatter(
        x=TAU,
        y=prod,
        name="x(τ)·h(t-τ)",
        line=dict(color="#059669", width=1.5),
        fill="tozeroy",
        fillcolor="rgba(5,150,105,0.45)",
    ),
    row=2,
    col=1,
)
fig.add_trace(
    go.Scatter(x=T_GRID, y=y, name="y(t)", line=dict(color="#0F172A", width=2.5)),
    row=3,
    col=1,
)
fig.add_trace(
    go.Scatter(
        x=[t],
        y=[y_now],
        name="当前时刻",
        mode="markers",
        marker=dict(color="#DC2626", size=11, line=dict(color="#FFFFFF", width=2)),
    ),
    row=3,
    col=1,
)

fig.update_yaxes(range=[0, 1.15], row=1, col=1)
fig.update_yaxes(range=[0, 1.15], row=2, col=1)
fig.update_yaxes(range=[0, max(float(y.max()), 0.1) * 1.2], row=3, col=1)
fig.update_xaxes(range=[-0.5, 8], row=1, col=1)
fig.update_xaxes(range=[-0.5, 8], row=2, col=1)
fig.update_xaxes(range=[-0.5, 8], row=3, col=1)

st.plotly_chart(style(fig), width="stretch")

st.info(f"当前 t = {t:.2f} 时，绿色面积 = {y_now:.3f}，这正是 y(t) 在这一点的取值。")

with st.expander("📘 这里藏着的 842 考点"):
    st.markdown(
        """
**1. 卷积的图解法四步**
翻转 h(τ) 得到 h(-τ)；平移 t 得到 h(t-τ)；与 x(τ) 相乘；对 τ 积分（求面积）。
考试让你用作图法求卷积，画的就是这三行图。

**2. 它在物理上到底干了什么**
LTI 系统等于「线性」加「时不变」，所以可以把输入 x 拆成无数个冲激：
位于 t=τ 时刻、面积为 x(τ)dτ 的那个冲激，激起的响应是 x(τ)·h(t-τ)dτ；
把所有响应叠加（积分）就是输出。**h(t) 就是系统的身份证。**

**3. 四条必须记住的性质**
- 交换律：x 卷 h = h 卷 x（把两个下拉框对调，结果一模一样）
- 结合律：(x 卷 h1) 卷 h2 = x 卷 (h1 卷 h2)
- 分配律：x 卷 (h1 + h2) = x 卷 h1 + x 卷 h2
- 与冲激卷积：x 卷 δ(t) = x(t)，x 卷 δ(t-t0) = x(t-t0)

**4. 长度规律（画图题的送分点）**
宽度 T1 和 T2 的两个矩形脉冲卷积得到梯形：
底边 = T1 + T2，顶边 = |T1 - T2|。当 T1 = T2 时退化为三角形。

**5. 卷积定理（模块③的频谱在这里派上用场）**
时域卷积等价于频域相乘：y(t) = x(t) 卷 h(t) 对应 Y(jω) = X(jω)·H(jω)。
这也是为什么滤波器在频域里可以理解成「乘上一个 H(jω)」。

**6. 842 最爱考的形式**
给两个分段函数的表达式，让你先分段讨论 t 落在哪个区间，
再定出积分上下限。**关键永远是先画图，再定限。**
        """
    )

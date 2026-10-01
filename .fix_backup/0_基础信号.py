import time

import numpy as np
import plotly.graph_objects as go
import streamlit as st

# ==================== 页面配置 ====================

FONT = "PingFang SC, Hiragino Sans GB, Microsoft YaHei, sans-serif"

st.markdown("""
<style>
    footer {visibility: hidden;}
    .block-container {padding-top: 2.2rem; padding-bottom: 2.5rem; max-width: 1500px;}
    h1 {font-weight: 800; letter-spacing: -0.5px;}
    section[data-testid="stSidebar"] {background-color: #F8FAFC; border-right: 1px solid #E2E8F0;}
    div[data-testid="stCaptionContainer"] p {color: #64748B; line-height: 1.7;}
    .katex-display {margin: 1.1rem 0 1.5rem 0;}
</style>
""", unsafe_allow_html=True)


# ==================== 图表统一样式 ====================
def style_fig(fig, height=460, xtitle="", ytitle="", legend_top=True, title=""):
    fig.update_layout(
        height=height,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT, size=13, color="#334155"),
        margin=dict(l=8, r=16, t=54, b=8),
        xaxis=dict(title=xtitle, gridcolor="rgba(148,163,184,0.22)",
                   zeroline=False, showline=False, tickfont=dict(size=12)),
        yaxis=dict(title=ytitle, gridcolor="rgba(148,163,184,0.22)",
                   zeroline=False, showline=False, tickfont=dict(size=12)),
        hoverlabel=dict(font=dict(family=FONT, size=12), bordercolor="rgba(0,0,0,0)"),
    )
    if title:
        fig.update_layout(title=dict(text=title, font=dict(size=14, color="#334155"),
                                     x=0, xanchor="left", y=0.97, yanchor="top"))
    if legend_top:
        fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02,
                                      xanchor="left", x=0, bgcolor="rgba(0,0,0,0)",
                                      font=dict(size=12)))
    return fig


# ==================== 侧边栏导航 ====================
with st.sidebar:
    st.markdown("## 🔬 信号实验室")
    st.caption("把课本上最抽象的那几页，变成能拖的东西")
    st.divider()
    module = st.radio("模块", ["① 基础信号", "② 傅里叶级数", "③ 采样与混叠"])
    st.divider()

st.title(module)


# ==================== 模块 ①：基础信号 ====================
if module == "① 基础信号":
    st.caption("最简单的一类信号。拖动参数，观察频率和幅度分别控制了什么。")

    with st.sidebar:
        freq = st.slider("频率 f (Hz)", 1.0, 10.0, 3.0, 0.5)
        amp = st.slider("幅度 A", 0.1, 3.0, 1.0, 0.1)

    t = np.linspace(0, 1, 1000, endpoint=False)
    y = amp * np.sin(2 * np.pi * freq * t)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=t, y=y, mode="lines", name="x(t)",
                             line=dict(width=2.6, color="#1E40AF"),
                             fill="tozeroy", fillcolor="rgba(30,64,175,0.07)"))
    style_fig(fig, height=430, xtitle="时间 t (秒)", ytitle="幅度", legend_top=False)
    st.plotly_chart(fig, width="stretch", config={"displaylogo": False})

    st.latex(rf"x(t) = {amp:.1f}\,\sin(2\pi\cdot{freq:.1f}\,t)")


# ==================== 模块 ②：傅里叶级数 ====================
elif module == "② 傅里叶级数":
    st.caption("方波可以分解成无穷多个 **奇次谐波** 的正弦波。拖动 N 增加项数，看它们如何一步步拼出方波。")
    st.latex(r"f(t)=\frac{4}{\pi}\sum_{n=1,3,5,\cdots}\frac{1}{n}\sin(n\,\omega_0 t)")

    with st.sidebar:
        Nmax = st.slider("谐波项数 N", 1, 51, 21, 2)
        alpha = st.slider("平滑因子 α", 0.0, 0.15, 0.0, 0.005)
        show_terms = st.checkbox("显示每个谐波分量", value=False)
        play = st.button("▶ 播放动画", width="stretch")

    t = np.linspace(0, 2 * np.pi, 1200)
    target = np.where(np.sin(t) >= 0, 1.0, -1.0)

    def partial_sum(n_max, a=0.0):
        y = np.zeros_like(t)
        for n in range(1, n_max + 1, 2):
            y = y + (4 / np.pi) / n * np.exp(-((a * n) ** 2)) * np.sin(n * t)
        return y

    def make_fig(n_max, a=0.0, with_terms=False):
        fig = go.Figure()
        if with_terms:
            for n in range(1, n_max + 1, 2):
                fig.add_trace(go.Scatter(
                    x=t, y=(4 / np.pi) / n * np.exp(-((a * n) ** 2)) * np.sin(n * t),
                    mode="lines", showlegend=False,
                    line=dict(width=1, color="rgba(148,163,184,0.55)")))
        fig.add_trace(go.Scatter(x=t, y=target, mode="lines", name="目标方波",
                                 line=dict(color="#94A3B8", width=2, dash="dash")))
        fig.add_trace(go.Scatter(x=t, y=partial_sum(n_max, a), mode="lines",
                                 name=f"前 {n_max} 项合成",
                                 line=dict(color="#1E40AF", width=3)))
        style_fig(fig, height=470, xtitle="ω₀t", ytitle="幅度")
        return fig

    col1, col2 = st.columns([2, 1])

    with col1:
        if alpha > 0:
            st.caption(f"⚠️ 已开启平滑：每项乘上衰减因子 e^(−(αn)²)，α = {alpha:.3f}。"
                       f"高次谐波被压制，跳变处的过冲被抹平——代价是边缘变钝。")
        chart_spot = st.empty()
        if play:
            for n in range(1, 52, 2):
                chart_spot.plotly_chart(make_fig(n, alpha, False),
                                        width="stretch",
                                        config={"displaylogo": False})
                time.sleep(0.2)
        else:
            chart_spot.plotly_chart(make_fig(Nmax, alpha, show_terms),
                                    width="stretch",
                                    config={"displaylogo": False})

    with col2:
        ns = list(range(1, Nmax + 1, 2))
        amps = [4 / (np.pi * n) * np.exp(-((alpha * n) ** 2)) for n in ns]
        fig2 = go.Figure(go.Bar(x=ns, y=amps, marker=dict(color="#3B82F6")))
        style_fig(fig2, height=470, xtitle="谐波次数 n", ytitle="幅度",
                  legend_top=False, title="各次谐波幅度")
        st.plotly_chart(fig2, width="stretch", config={"displaylogo": False})

    st.divider()
    st.caption("💡 α = 0 时是 **纯** 傅里叶级数，跳变处有约 9% 的尖峰（吉布斯现象），加再多项也消不掉；"
               "α 增大是工程上压制它的手段，代价是边缘变钝。这两者的取舍，就是数字滤波器设计的核心问题。")


# ==================== 模块 ③：采样与混叠 ====================
elif module == "③ 采样与混叠":
    st.caption("采样定理要求采样频率大于信号最高频率的两倍。低于这个值会发生什么？")
    st.latex(r"f_s \;>\; 2\,f_{\max}")

    with st.sidebar:
        f_sig = st.slider("信号频率 f (Hz)", 1.0, 10.0, 7.0, 0.5)
        fs = st.slider("采样频率 fs (Hz)", 1.0, 40.0, 10.0, 0.5)

    T = 1.0
    tt = np.linspace(0, T, 1500)
    xt = np.sin(2 * np.pi * f_sig * tt)

    ts_all = np.arange(-0.3, T + 0.3, 1 / fs)
    xs_all = np.sin(2 * np.pi * f_sig * ts_all)

    diff = tt[:, None] - ts_all[None, :]
    xr = (xs_all[None, :] * np.sinc(diff * fs)).sum(axis=1)

    mask = (ts_all >= 0) & (ts_all <= T)
    ts_show, xs_show = ts_all[mask], xs_all[mask]

    f_alias = abs(f_sig - fs * round(f_sig / fs))
    aliased = fs < 2 * f_sig

    col1, col2 = st.columns([3, 2])

    with col1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=tt, y=xt, mode="lines", name="原始信号",
                                 line=dict(color="#94A3B8", width=2, dash="dash")))
        fig.add_trace(go.Scatter(x=tt, y=xr, mode="lines", name="由采样点重建",
                                 line=dict(color="#1E40AF", width=3)))
        fig.add_trace(go.Scatter(x=ts_show, y=xs_show, mode="markers", name="采样点",
                                 marker=dict(color="#F59E0B", size=9,
                                             line=dict(color="white", width=1.5))))
        style_fig(fig, height=460, xtitle="时间 t (秒)", ytitle="幅度")
        st.plotly_chart(fig, width="stretch", config={"displaylogo": False})

    with col2:
        fig2 = go.Figure()
        xs_line, ys_line = [], []
        for k in np.arange(-4, 5):
            for s in (1, -1):
                fr = k * fs + s * f_sig
                if 0 <= fr <= 45:
                    xs_line.extend([fr, fr, None])
                    ys_line.extend([0, 1, None])
        fig2.add_trace(go.Scatter(x=xs_line, y=ys_line, mode="lines",
                                  name="采样后频谱", line=dict(color="#3B82F6", width=3)))
        fig2.add_trace(go.Scatter(x=[f_sig, f_sig], y=[0, 1], mode="lines",
                                  name="原始信号频谱",
                                  line=dict(color="#94A3B8", width=4, dash="dash")))
        fig2.add_vrect(x0=0, x1=fs / 2, fillcolor="rgba(30,64,175,0.07)", line_width=0)
        fig2.add_vline(x=fs / 2, line_dash="dot", line_color="#EF4444", line_width=2,
                       annotation_text="fs/2", annotation_position="top")
        style_fig(fig2, height=460, xtitle="频率 (Hz)", ytitle="幅度",
                  legend_top=True, title="频域：采样会让频谱周期性复制")
        st.plotly_chart(fig2, width="stretch", config={"displaylogo": False})

    if aliased:
        st.error(f"❌ fs = {fs:.1f} Hz < 2f = {2 * f_sig:.1f} Hz，不满足采样定理。"
                 f"重建出的波形频率变成了 **{f_alias:.1f} Hz** —— 原始信号的信息已经永久丢失。")
    else:
        st.success(f"✅ fs = {fs:.1f} Hz ≥ 2f = {2 * f_sig:.1f} Hz，满足采样定理，"
                   f"蓝色重建曲线与灰色原始曲线完全重合。")

    st.caption("💡 右图浅蓝区域 [0, fs/2] 是采样系统能正确识别的频率范围，叫**奈奎斯特带宽**。"
               "当原始信号频率 f 跑到这个区域外面，它就会以 |f − fs| 的频率出现在区域内——这就是**混叠**。"
               "音频里的金属声、视频里车轮倒转，都是同一回事。")

with st.expander("🎯 842 考点速记", expanded=False):
    st.markdown(r"""
**① 奇异信号**

- 单位冲激 $\delta(t)$：$\delta(t)=0\ (t\neq 0)$，且 $\displaystyle\int_{-\infty}^{\infty}\delta(t)\,dt = 1$
- **抽样性质（最常考）**：$\displaystyle\int_{-\infty}^{\infty} f(t)\,\delta(t-t_0)\,dt = f(t_0)$
- 与阶跃的关系：$\dfrac{d\varepsilon(t)}{dt} = \delta(t)$，$\displaystyle\int_{-\infty}^{t}\delta(\tau)\,d\tau = \varepsilon(t)$
- 冲激偶：$\displaystyle\int_{-\infty}^{\infty} f(t)\,\delta'(t)\,dt = -f'(0)$

**② 信号的变换**

- **时移** $f(t-t_0)$：$t_0>0$ 右移
- **反褶** $f(-t)$
- **尺度** $f(at)$：$|a|>1$ 压缩到 $1/|a|$，且 **$a<0$ 时同时反褶**
- ⚠️ **高频陷阱**：$f(-at+b)$ 的正确顺序是**先反褶、再平移**，平移量是 $\dfrac{b}{a}$ **不是** $b$

**③ 傅里叶级数**

- 三角形式：$f(t) = a_0 + \sum\limits_{n=1}^{\infty}\left[a_n\cos n\omega_0 t + b_n\sin n\omega_0 t\right]$
- **狄利克雷条件**：一个周期内绝对可积、极值点有限、间断点有限
- **对称性**：偶函数 → 只有余弦；奇函数 → 只有正弦；**奇半波对称 → 只有奇次谐波**
- 方波展开：幅度按 $1/n$ 衰减，只有奇次谐波
- **吉布斯现象**：跳变点附近约 **9%** 的过冲，**增加项数无法消除**，只能把振荡压缩到跳变点附近

**④ 采样定理**

- **奈奎斯特采样定理**：$f_s \ge 2f_{\max}$
- **混叠**：$f_s < 2f_{\max}$ 时高频被折叠到低频，无法恢复
- 采样后频谱：原频谱以 $f_s$ 为周期**无限重复**，幅度乘 $1/T$
- 理想恢复：截止 $f_s/2$ 的理想低通，增益 $T$
""")


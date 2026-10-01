import numpy as np
import streamlit as st
import plotly.graph_objects as go

FONT = "PingFang SC, Hiragino Sans GB, Microsoft YaHei, sans-serif"


def H(s, zeros, poles, k):
    num = np.ones_like(s, dtype=complex)
    for z in zeros:
        num = num * (s - z)
    den = np.ones_like(s, dtype=complex)
    for p in poles:
        den = den * (s - p)
    return k * num / den


def style(fig, height=520):
    fig.update_layout(
        height=height,
        font=dict(family=FONT, size=12),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#F8FAFC",
        margin=dict(l=10, r=10, t=55, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig.update_xaxes(gridcolor="#E2E8F0", zeroline=False)
    fig.update_yaxes(gridcolor="#E2E8F0", zeroline=False)
    return fig


st.title("⑥ 零极点与频率响应")
st.caption(
    "频率响应不是算出来的，是「量」出来的：它等于 jω 点到各极点的距离之比。"
    "拖动 ω，看那条连线怎么变短。"
)

sys_type = st.selectbox(
    "系统类型",
    ["一阶：单个实极点", "二阶：一对共轭极点", "二阶极点 + 一对共轭零点"],
)

c1, c2 = st.columns(2)

if sys_type == "一阶：单个实极点":
    with c1:
        sp = st.slider("极点实部 σp", -3.0, -0.1, -1.0, 0.05)
    poles = [complex(sp, 0.0)]
    zeros = []
elif sys_type == "二阶：一对共轭极点":
    with c1:
        sp = st.slider("极点实部 σp", -3.0, -0.1, -0.5, 0.05)
    with c2:
        wp = st.slider("极点虚部 ωp", 0.5, 2.5, 2.0, 0.05)
    poles = [complex(sp, wp), complex(sp, -wp)]
    zeros = []
else:
    with c1:
        sp = st.slider("极点实部 σp", -3.0, -0.1, -0.5, 0.05)
        zp = st.slider("零点实部 σz", -3.0, 0.0, -1.0, 0.05)
    with c2:
        wp = st.slider("极点虚部 ωp", 0.5, 2.5, 2.0, 0.05)
        wz = st.slider("零点虚部 ωz", 0.5, 2.5, 2.0, 0.05)
    poles = [complex(sp, wp), complex(sp, -wp)]
    zeros = [complex(zp, wz), complex(zp, -wz)]

w = st.slider("观测频率 ω", 0.0, 4.0, 2.0, 0.02)

K = float(np.prod([abs(p) for p in poles]) / np.prod([abs(z) for z in zeros]))

wg = np.linspace(0.0, 4.0, 801)
mag = np.abs(H(1j * wg, zeros, poles, K))
mag_db = np.clip(20 * np.log10(np.maximum(mag, 1e-6)), -45, None)

H_now = H(np.array([1j * w]), zeros, poles, K)[0]
mag_now = float(np.abs(H_now))
db_now = float(np.clip(20 * np.log10(max(mag_now, 1e-6)), -45, None))
ang_now = float(np.angle(H_now, deg=True))

fig1 = go.Figure()
fig1.add_hline(y=0, line=dict(color="#94A3B8", width=1))
fig1.add_vline(x=0, line=dict(color="#64748B", width=2))

for p in poles:
    fig1.add_trace(
        go.Scatter(
            x=[0.0, p.real],
            y=[w, p.imag],
            mode="lines",
            line=dict(color="rgba(220,38,38,0.5)", width=1.6, dash="dot"),
            showlegend=False,
            hoverinfo="skip",
        )
    )
for z in zeros:
    fig1.add_trace(
        go.Scatter(
            x=[0.0, z.real],
            y=[w, z.imag],
            mode="lines",
            line=dict(color="rgba(30,64,175,0.5)", width=1.6, dash="dot"),
            showlegend=False,
            hoverinfo="skip",
        )
    )

fig1.add_trace(
    go.Scatter(
        x=[p.real for p in poles],
        y=[p.imag for p in poles],
        mode="markers",
        name="极点",
        marker=dict(symbol="x", size=13, color="#DC2626", line=dict(width=3)),
    )
)

if zeros:
    fig1.add_trace(
        go.Scatter(
            x=[z.real for z in zeros],
            y=[z.imag for z in zeros],
            mode="markers",
            name="零点",
            marker=dict(symbol="circle-open", size=14, color="#1E40AF", line=dict(width=3)),
        )
    )

fig1.add_trace(
    go.Scatter(
        x=[0.0],
        y=[w],
        mode="markers",
        name="jω 观察点",
        marker=dict(color="#059669", size=13, line=dict(color="#FFFFFF", width=2)),
    )
)

fig1.update_xaxes(title_text="σ（实部）", range=[-4.0, 1.5])
fig1.update_yaxes(title_text="jΩ（虚部）", range=[-3.0, 3.0])
fig1.update_layout(title="① s 平面：从 jω 到各零极点的连线")

fig2 = go.Figure()
fig2.add_trace(
    go.Scatter(x=wg, y=mag_db, name="20log|H(jω)|", line=dict(color="#1E40AF", width=2.5))
)

if poles[0].imag > 0:
    fig2.add_vline(
        x=poles[0].imag,
        line=dict(color="#DC2626", dash="dash", width=1.2),
        annotation_text="ωp",
        annotation_position="top",
    )
if zeros and zeros[0].imag > 0:
    fig2.add_vline(
        x=zeros[0].imag,
        line=dict(color="#1E40AF", dash="dash", width=1.2),
        annotation_text="ωz",
        annotation_position="top",
    )

fig2.add_vline(x=w, line=dict(color="#94A3B8", dash="dot", width=2))
fig2.add_trace(
    go.Scatter(
        x=[w],
        y=[db_now],
        mode="markers",
        name="当前 ω",
        marker=dict(color="#059669", size=13, line=dict(color="#FFFFFF", width=2)),
    )
)

fig2.update_xaxes(title_text="ω（角频率）", range=[0, 4])
fig2.update_yaxes(title_text="幅度 (dB)", range=[-45, 32])
fig2.update_layout(title="② 幅频响应：连线越短，这里越高")

left, right = st.columns(2)
with left:
    st.plotly_chart(style(fig1), width="stretch")
with right:
    st.plotly_chart(style(fig2), width="stretch")

st.info(
    f"当前 ω = {w:.2f}：|H(jω)| = {mag_now:.3f}（{db_now:.1f} dB），"
    f"相位 ∠H(jω) = {ang_now:.1f}°"
)

with st.expander("📘 这里藏着的 842 考点"):
    st.markdown(
        """
**1. 频率响应就是 s 平面上的「距离比」**
把 s = jω 代进 H(s) 之后取模：|H(jω)| = K · （jω 到各零点的距离之积）/（jω 到各极点的距离之积）。
所以 s 平面上几何作图法求幅频特性，本质就是量长度。

**2. 极点负责「拉高」**
ω 走到某个极点的正上方时，那条连线最短，分母最小，|H| 最大。
极点越靠近虚轴（σp 越接近 0），峰值越高越尖，这就是高 Q 谐振。
品质因数 Q = ωp / (2|σp|)。

**3. 零点负责「压低」**
ω 走到零点正上方时，分子最小，|H| 最小。
零点恰好落在虚轴上（σz = 0）时，该频率上 |H| = 0，这就是陷波器。

**4. 稳定性判断（842 送分题）**
- 极点全在左半平面（σ < 0）→ 系统稳定
- 极点在虚轴上 → 临界情况，等幅振荡
- 极点在右半平面 → 发散，不稳定
零点位置不影响稳定性。

**5. 二阶系统的标准形式**
H(s) = ωn² / (s² + 2ζωn·s + ωn²)，极点 p = -ζωn ± jωn√(1-ζ²)，即 σp = -ζωn，ωp = ωn√(1-ζ²)。
阻尼比 ζ 越小，极点越靠近虚轴，谐振峰越高，且 Q = 1/(2ζ)。

**6. 回头看模块④就通了**
巴特沃斯滤波器的极点，均匀分布在 s 平面左半平面的一个半圆上（巴特沃斯圆）。
阶数 N 越大，极点越多，靠近虚轴的那一段就越陡 —— 这就是「过渡带更陡」的几何来源。
切比雪夫把极点挪成椭圆分布，用通带波纹换更陡的过渡带。
        """
    )

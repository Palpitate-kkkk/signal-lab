import numpy as np
import streamlit as st
import plotly.graph_objects as go
from scipy import signal

FONT = "PingFang SC, Hiragino Sans GB, Microsoft YaHei, sans-serif"
BTYPE = {"低通": "low", "高通": "high", "带通": "bandpass", "带阻": "bandstop"}


def style(fig):
    fig.update_layout(
        font=dict(family=FONT),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#F8FAFC",
        margin=dict(l=10, r=10, t=50, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig.update_xaxes(gridcolor="#E2E8F0", zeroline=False)
    fig.update_yaxes(gridcolor="#E2E8F0", zeroline=False)
    return fig


st.title("④ 滤波器设计")
st.caption("滤波器的本质是「用延迟和相位失真，换取频率选择性」。阶数越高切得越干净，代价也越大。")

c1, c2, c3 = st.columns(3)
with c1:
    ftype = st.selectbox("滤波器类型", list(BTYPE.keys()))
with c2:
    order = st.slider("阶数 N", 1, 8, 3)
with c3:
    noise = st.slider("噪声强度", 0.0, 1.0, 0.20, 0.05)

if ftype in ("低通", "高通"):
    fc = st.slider("截止频率 (Hz)", 20, 900, 300, 10)
    wn = fc
    band_text = f"{fc} Hz"
else:
    d1, d2 = st.columns(2)
    with d1:
        f_lo = st.slider("下限频率 (Hz)", 40, 800, 250, 10)
    with d2:
        f_hi = st.slider("上限频率 (Hz)", 60, 900, 500, 10)
    if f_lo >= f_hi:
        f_lo, f_hi = 250, 500
        st.warning("下限必须小于上限，已重置为 250 / 500 Hz。")
    wn = [f_lo, f_hi]
    band_text = f"{f_lo}–{f_hi} Hz"

FS = 2000.0
t = np.arange(int(FS * 0.1)) / FS
F1, F2 = 80.0, 350.0
rng = np.random.default_rng(42)
x = np.sin(2 * np.pi * F1 * t) + 0.6 * np.sin(2 * np.pi * F2 * t) + noise * rng.standard_normal(t.size)

b, a = signal.butter(order, wn, btype=BTYPE[ftype], fs=FS)
y = signal.filtfilt(b, a, x)

w, h = signal.freqz(b, a, worN=2048, fs=FS)
mag_db = 20 * np.log10(np.maximum(np.abs(h), 1e-8))

st.info(f"当前设置：{order} 阶{ftype}滤波器，{band_text}。输入信号 = 80 Hz + 350 Hz 正弦 + 噪声。")

fig1 = go.Figure()
fig1.add_trace(go.Scatter(x=w, y=mag_db, name="幅频响应", line=dict(color="#1E40AF", width=2.5)))
fig1.add_hline(y=-3, line=dict(color="#EF4444", dash="dash", width=1.5),
               annotation_text="-3 dB 半功率点", annotation_position="bottom left")
if isinstance(wn, list):
    for fv in wn:
        fig1.add_vline(x=fv, line=dict(color="#94A3B8", dash="dot", width=1))
else:
    fig1.add_vline(x=wn, line=dict(color="#94A3B8", dash="dot", width=1))
fig1.update_xaxes(title_text="频率 (Hz)", range=[0, 1000])
fig1.update_yaxes(title_text="幅度 (dB)", range=[-70, 5])
fig1.update_layout(height=380, title="① 幅频响应：这条曲线就是滤波器的性格")
st.plotly_chart(style(fig1), width="stretch")

left, right = st.columns(2)

with left:
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=t * 1000, y=x, name="滤波前", line=dict(color="#94A3B8", width=1.2)))
    fig2.add_trace(go.Scatter(x=t * 1000, y=y, name="滤波后", line=dict(color="#1E40AF", width=2)))
    fig2.update_xaxes(title_text="时间 (ms)")
    fig2.update_yaxes(title_text="幅值")
    fig2.update_layout(title="② 时域波形")
    st.plotly_chart(style(fig2), width="stretch")

with right:
    freqs = np.fft.rfftfreq(t.size, 1 / FS)
    X = np.abs(np.fft.rfft(x)) / t.size * 2
    Y = np.abs(np.fft.rfft(y)) / t.size * 2
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=freqs, y=X, name="滤波前", line=dict(color="#94A3B8", width=1.5)))
    fig3.add_trace(go.Scatter(x=freqs, y=Y, name="滤波后", line=dict(color="#1E40AF", width=2)))
    fig3.update_xaxes(title_text="频率 (Hz)", range=[0, 1000])
    fig3.update_yaxes(title_text="幅度")
    fig3.update_layout(title="③ 频谱对比")
    st.plotly_chart(style(fig3), width="stretch")

with st.expander("📘 这里藏着的 842 考点"):
    st.markdown(
        """
**1. 阶数 N 是陡峭度的旋钮。**
巴特沃斯的幅度平方函数是 |H(jΩ)|² = 1 / (1 + (Ω/Ωc) 的 2N 次方)，
N 越大，过渡带越窄，越接近理想矩形。

**2. 但代价是相位失真。**
N 越大，通带内相位越不线性、群延迟越不平坦，方波和脉冲这类有棱角的信号
过滤波器后会出现振铃（ringing）。真正无失真的条件是：幅频平坦 + 相频线性。

**3. 为什么这里用 filtfilt 而不是 lfilter？**
filtfilt 正着滤一遍、倒着再滤一遍，把相位失真抵消掉，得到零相位滤波。
实时系统做不到（要缓存整段信号），只能接受相位延迟。

**4. 三大经典逼近（842 常考对比）：**
- 巴特沃斯：通带最平坦，过渡带最缓
- 切比雪夫 I 型：通带有等波纹，过渡带更陡
- 椭圆（考尔）：通带阻带都有波纹，过渡带最陡

**5. 模拟到数字的两条路：**
- 冲激响应不变法：h[n] = T · h(nT)，频率轴线性映射，但有频谱混叠，适合低通带通
- 双线性变换法：s = (2/T) · (1-z⁻¹)/(1+z⁻¹)，无混叠，但频率轴被非线性压缩（频率畸变）
        """
    )

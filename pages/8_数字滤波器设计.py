import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy import signal
import streamlit as st

st.set_page_config(page_title="模块⑧ 数字滤波器设计", page_icon="🔢", layout="wide")

st.title("模块⑧ 数字滤波器设计")
st.caption("把模拟原型 H(s) 变成真正能用的 H(z)：冲激响应不变法 vs 双线性变换")

st.markdown(r"""
我们手里只有**模拟原型**（巴特沃斯 / 切比雪夫 / 椭圆的 $H(s)$），
要把它变成能给数字信号处理的 $H(z)$，两条经典路线：

| 方法 | 映射关系 | 致命缺点 |
| :-- | :-- | :-- |
| **① 冲激响应不变法** | $z = e^{sT}$ | **混叠**：模拟高频被折叠回低频 |
| **② 双线性变换** | $s = \frac{2}{T}\cdot\frac{1-z^{-1}}{1+z^{-1}}$ | **频率畸变**：$\Omega$ 与 $\omega$ 非线性 |
| **③ 双线性 + 预畸变** | 先把 $\Omega_c$ 反过来算一次 | 工程标准做法，无副作用 |

拖下面三个滑块，看三条曲线怎么分道扬镳 👇
""")

c1, c2, c3 = st.columns(3)
with c1:
    fs = st.select_slider("采样率 fs (Hz)", options=[500, 1000, 2000, 4000], value=1000)
with c2:
    r = st.slider("数字截止频率 fc / fs", 0.02, 0.45, 0.10, 0.01)
with c3:
    N = st.slider("模拟原型阶数 N", 1, 6, 3)

fc = r * fs
T = 1.0 / fs
wc = 2 * np.pi * fc
st.caption(
    f"fs = {fs} Hz ｜ fc = {fc:.0f} Hz ｜ 奈奎斯特频率 = {fs/2:.0f} Hz ｜ 阶数 N = {N}"
)

# ---------------- 模拟原型（Ωc = 2πfc，未做任何补偿） ----------------
z_a, p_a, k_a = signal.butter(N, wc, btype="low", analog=True, output="zpk")
b_a, a_a = signal.zpk2tf(z_a, p_a, k_a)


def _flat(num, den):
    return np.atleast_1d(np.squeeze(num)), np.atleast_1d(np.squeeze(den))


# ---------------- ① 冲激响应不变法 ----------------
num_i, den_i, _ = signal.cont2discrete((b_a, a_a), T, method="impulse")
num_i, den_i = _flat(num_i, den_i)

# ---------------- ② 双线性变换（不补偿畸变） ----------------
num_b, den_b, _ = signal.cont2discrete((b_a, a_a), T, method="bilinear")
num_b, den_b = _flat(num_b, den_b)

# ---------------- ③ 双线性变换 + 预畸变 ----------------
wc_pre = 2 * fs * np.tan(np.pi * fc / fs)
z_p, p_p, k_p = signal.butter(N, wc_pre, btype="low", analog=True, output="zpk")
b_p, a_p = signal.zpk2tf(z_p, p_p, k_p)
num_p, den_p, _ = signal.cont2discrete((b_p, a_p), T, method="bilinear")
num_p, den_p = _flat(num_p, den_p)

# ---------------- 频率响应 ----------------
w_d, h_i = signal.freqz(num_i, den_i, worN=4096, fs=fs)
_, h_b = signal.freqz(num_b, den_b, worN=4096, fs=fs)
_, h_p = signal.freqz(num_p, den_p, worN=4096, fs=fs)

w_a = np.linspace(1e-6, np.pi * fs, 4000)
_, h_a = signal.freqs(b_a, a_a, worN=w_a)
f_a = w_a / (2 * np.pi)


def to_db(h):
    return 20 * np.log10(np.maximum(np.abs(h), 1e-12))


left, right = st.columns(2)

with left:
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=f_a, y=to_db(h_a), name="模拟原型 H(jΩ)",
                              line=dict(color="#94A3B8", width=2.5, dash="dash")))
    fig1.add_trace(go.Scatter(x=w_d, y=to_db(h_i), name="① 冲激响应不变法",
                              line=dict(color="#F59E0B", width=2.5)))
    fig1.add_trace(go.Scatter(x=w_d, y=to_db(h_b), name="② 双线性变换",
                              line=dict(color="#3B82F6", width=2.5)))
    fig1.add_trace(go.Scatter(x=w_d, y=to_db(h_p), name="③ 双线性 + 预畸变",
                              line=dict(color="#10B981", width=2.5)))
    fig1.add_vline(x=fc, line=dict(color="#EF4444", dash="dot", width=1.5))
    fig1.add_annotation(x=fc, y=2, text="目标 fc", showarrow=False, yshift=12,
                        font=dict(color="#EF4444", size=11))
    fig1.add_vline(x=fs / 2, line=dict(color="#CBD5E1", dash="dot", width=1.5))
    fig1.add_annotation(x=fs / 2, y=2, text="Nyquist", showarrow=False, yshift=12,
                        font=dict(color="#94A3B8", size=11))
    fig1.update_layout(height=400, title="幅频响应对比",
                       xaxis_title="频率 (Hz)", yaxis_title="幅度 (dB)",
                       xaxis_range=[0, fs / 2], yaxis_range=[-80, 8],
                       legend=dict(orientation="h", y=-0.3, font=dict(size=10)),
                       margin=dict(t=50, b=10))
    st.plotly_chart(fig1, width="stretch")

with right:
    fig2 = go.Figure()
    th = np.linspace(0, 2 * np.pi, 500)
    fig2.add_trace(go.Scatter(x=np.cos(th), y=np.sin(th), mode="lines",
                              line=dict(color="#CBD5E1", width=1.5),
                              showlegend=False, hoverinfo="skip"))

    COLORS = {"冲激响应不变法": "#F59E0B", "双线性变换": "#3B82F6", "双线性 + 预畸变": "#10B981"}
    for name, num, den in [("冲激响应不变法", num_i, den_i),
                           ("双线性变换", num_b, den_b),
                           ("双线性 + 预畸变", num_p, den_p)]:
        zz, pp, _ = signal.tf2zpk(num, den)
        c = COLORS[name]
        fig2.add_trace(go.Scatter(x=np.real(pp), y=np.imag(pp), mode="markers",
                                  name=f"{name} · 极点",
                                  marker=dict(symbol="x", size=12, color=c,
                                              line=dict(width=2.5))))
        if len(zz):
            fig2.add_trace(go.Scatter(x=np.real(zz), y=np.imag(zz), mode="markers",
                                      name=f"{name} · 零点",
                                      marker=dict(symbol="circle-open", size=12, color=c,
                                                  line=dict(width=2.5))))

    fig2.add_hline(y=0, line=dict(color="#E2E8F0", width=1))
    fig2.add_vline(x=0, line=dict(color="#E2E8F0", width=1))
    fig2.update_layout(height=400, title="z 平面：极点 / 零点分布",
                       xaxis=dict(title="Re(z)", range=[-1.7, 1.7], zeroline=False,
                                  scaleanchor="y", scaleratio=1),
                       yaxis=dict(title="Im(z)", range=[-1.7, 1.7], zeroline=False),
                       legend=dict(orientation="h", y=-0.32, font=dict(size=9)),
                       margin=dict(t=50, b=10))
    st.plotly_chart(fig2, width="stretch")

# ---------------- 指标 ----------------
m1, m2, m3 = st.columns(3)
m1.metric("目标数字截止 fc", f"{fc:.0f} Hz")
m2.metric("模拟原型 Ωc（未补偿）", f"{wc:,.0f} rad/s")
m3.metric("预畸变后 Ωc", f"{wc_pre:,.0f} rad/s",
          delta=f"{wc_pre - wc:+,.0f}", delta_color="off")

rows = []
for name, h in [("① 冲激响应不变法", h_i), ("② 双线性变换", h_b), ("③ 双线性 + 预畸变", h_p)]:
    mag = np.abs(h)
    thr = mag[0] / np.sqrt(2)
    idx = np.where(mag <= thr)[0]
    f3 = float(w_d[idx[0]]) if idx.size else float("nan")
    rows.append({
        "离散化方法": name,
        "实测 -3 dB 频率 (Hz)": round(f3, 1),
        "与目标偏差 (Hz)": round(f3 - fc, 1),
        "fc 处增益 (dB)": round(20 * np.log10(max(float(np.interp(fc, w_d, mag)), 1e-12)), 2),
        "Nyquist 处增益 (dB)": round(20 * np.log10(max(float(mag[-1]), 1e-12)), 1),
    })

st.markdown("**三种方法的实测指标**（-3 dB 点离目标越近越好）")
st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)

# ---------------- 预畸变原理 ----------------
with st.expander("📐 预畸变（prewarping）到底在算什么？", expanded=False):
    st.markdown(r"""
双线性变换把 $j\Omega$ 轴**非线性**地压到单位圆上：

$$\Omega = \frac{2}{T}\tan\!\left(\frac{\omega}{2}\right)
\qquad\Longleftrightarrow\qquad
\omega = 2\arctan\!\left(\frac{\Omega T}{2}\right)$$

所以如果你直接拿 $\Omega_c = 2\pi f_c$ 去造模拟原型，变换到数字域后
$-3\ \mathrm{dB}$ 点会**偏离** $f_c$，而且频率越高偏得越狠（高频被压缩）。

**预畸变就是反过来解一次**：先钉死"我想要的数字截止频率是 $\omega_c$"，
再反算出该用多大的**模拟**截止频率：

$$\Omega_c' = \frac{2}{T}\tan\!\left(\frac{\omega_c}{2}\right)
= 2 f_s \tan\!\left(\frac{\pi f_c}{f_s}\right)$$

用这个 $\Omega_c'$ 去造模拟原型，再过双线性变换，数字域 $-3\ \mathrm{dB}$ 点就**精确落回 $f_c$**。
""")
    w_norm = np.linspace(1e-4, np.pi, 600)
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=w_norm / np.pi, y=w_norm / T, name="理想线性：Ω = ω/T",
                              line=dict(color="#94A3B8", dash="dash", width=2)))
    fig3.add_trace(go.Scatter(x=w_norm / np.pi, y=(2 / T) * np.tan(w_norm / 2),
                              name="双线性真实映射：Ω = (2/T)·tan(ω/2)",
                              line=dict(color="#3B82F6", width=2.5)))
    wc_n = 2 * np.pi * fc / fs
    fig3.add_trace(go.Scatter(x=[wc_n / np.pi], y=[wc_pre], mode="markers",
                              name="本次的预畸变工作点",
                              marker=dict(color="#EF4444", size=12)))
    fig3.update_layout(height=360, title="双线性变换的频率映射：两头拉、中间挤",
                       xaxis_title="归一化数字频率 ω/π", yaxis_title="模拟角频率 Ω (rad/s)",
                       legend=dict(orientation="h", y=-0.3, font=dict(size=10)),
                       margin=dict(t=50, b=10))
    st.plotly_chart(fig3, width="stretch")

# ---------------- 考点速记 ----------------
with st.expander("🎯 842 考点速记", expanded=False):
    st.markdown(r"""
**① 冲激响应不变法**

- 时域直接采样：$h[n] = T\,h_a(nT)$，所以**时域形状完全保留**
- 频域是**周期叠加**：
$$H(e^{j\omega}) = \frac{1}{T}\sum_{k=-\infty}^{\infty} H_a\!\left(j\frac{\omega - 2\pi k}{T}\right)$$
- 只要 $H_a$ 在 $|\Omega| > \pi/T$ 处还有能量 → **混叠**
- 结论：**只能用于低通 / 带通**；高通、带阻必混叠，不能用
- 极点映射 $p_z = e^{p_a T}$，左半平面 → 单位圆内，**稳定性保持**
- 全极点模拟滤波器离散后，零点全部落在 $z = 0$

**② 双线性变换**

- $s = \dfrac{2}{T}\cdot\dfrac{1-z^{-1}}{1+z^{-1}}$，反解 $z = \dfrac{1 + sT/2}{1 - sT/2}$
- $j\Omega$ 轴 $(-\infty \to +\infty)$ 与单位圆 $(-\pi \to \pi)$ **一一对应 → 绝不混叠**
- 左半平面 → 单位圆内，**稳定性保持**；阶数 $N$ 不变
- 极点映射 $p_z = \dfrac{1 + p_aT/2}{1 - p_aT/2}$
- 模拟域 $s=\infty$ 上的 $N$ 阶零点 → 全部映射到 $z = -1$（所以双线性结果的零点都堆在 $-1$）
- 代价：$\Omega$ 与 $\omega$ 非线性，**高频被压缩**

**③ 预畸变常考形式**

取 $T = 2$ 时最省事：$s = \dfrac{1-z^{-1}}{1+z^{-1}}$，
此时 $\Omega = \tan(\omega/2)$，预畸变 $\Omega_c = \tan(\omega_c/2)$。

**④ 典型大题套路**

> 低通：通带 $f_p$、阻带 $f_s$，通带衰减 $\alpha_p$、阻带衰减 $\alpha_s$，采样率 $F_s$。

1. **预畸变**：$\Omega_p = 2F_s\tan\dfrac{\pi f_p}{F_s}$，$\Omega_s = 2F_s\tan\dfrac{\pi f_s}{F_s}$
2. **求阶数**：$N \ge \dfrac{\lg\left(\dfrac{10^{0.1\alpha_s}-1}{10^{0.1\alpha_p}-1}\right)}{2\lg(\Omega_s/\Omega_p)}$，向上取整
3. **算 $\Omega_c$**（巴特沃斯用通带或阻带任一满足即可），写 $H_a(s)$
4. **双线性变换**代入 $s = \dfrac{2}{T}\cdot\dfrac{1-z^{-1}}{1+z^{-1}}$，整理成 $H(z)$

**⑤ 三个最容易考的对比**

| | 冲激响应不变法 | 双线性变换 |
| :-- | :-- | :-- |
| 混叠 | **有** | 无 |
| 频率畸变 | 无 | **有**（需预畸变） |
| 适用 | 低通 / 带通 | 全部类型 |
| 零点位置 | $z = 0$ | $z = -1$ |
| 时域 | 冲激响应形状保留 | 不保留 |
""")

st.divider()
st.caption("模块⑧ / signal-lab ｜ 下一步：FIR 滤波器设计（窗函数法）与频谱泄露")

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy import signal
import streamlit as st


st.title("模块⑦ 三大逼近对比")
st.caption("巴特沃斯 / 切比雪夫 I 型 / 椭圆 —— 同样阶数下，谁的过渡带最陡？")

st.markdown(r"""
同一个 $-3\ \mathrm{dB}$ 通带、同样的阶数 $N$，三种逼近法的**过渡带陡峭度**差别巨大：

| 类型 | 通带 | 阻带 | 极点分布 | 代价 |
| :-- | :-- | :-- | :-- | :-- |
| **巴特沃斯** | 最平坦（无波纹） | 单调下降 | 单位圆上的**半圆** | 过渡带最宽 |
| **切比雪夫 I** | **等波纹**（≤ Rp） | 单调下降 | **椭圆** | 相位非线性 |
| **椭圆** | **等波纹** | **等波纹** | 椭圆 + **虚轴零点** | 过渡带最窄，相位最差 |

拖滑块看曲线怎么随 $N$、"通带波纹 $R_p$"、"阻带衰减 $R_s$"变化 👇
""")

c1, c2, c3 = st.columns(3)
with c1:
    N = st.slider("滤波器阶数 N", 1, 8, 4)
with c2:
    Rp = st.slider("通带波纹 Rp (dB)", 0.1, 3.0, 1.0, 0.1)
with c3:
    Rs = st.slider("阻带衰减 Rs (dB)", 20, 80, 40, 5)

Wc = 1.0  # 归一化模拟截止角频率 Ωc = 1 rad/s

zb, pb, kb = signal.butter(N, Wc, btype="low", analog=True, output="zpk")
zc, pc, kc = signal.cheby1(N, Rp, Wc, btype="low", analog=True, output="zpk")
ze, pe, ke = signal.ellip(N, Rp, Rs, Wc, btype="low", analog=True, output="zpk")

w = np.logspace(-1.0, 1.6, 3000)
_, hb = signal.freqs_zpk(zb, pb, kb, worN=w)
_, hc = signal.freqs_zpk(zc, pc, kc, worN=w)
_, he = signal.freqs_zpk(ze, pe, ke, worN=w)


def to_db(h):
    return 20 * np.log10(np.maximum(np.abs(h), 1e-12))


left, right = st.columns(2)

with left:
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=w, y=to_db(hb), name="巴特沃斯",
                              line=dict(color="#3B82F6", width=2.5)))
    fig1.add_trace(go.Scatter(x=w, y=to_db(hc), name="切比雪夫 I 型",
                              line=dict(color="#F59E0B", width=2.5)))
    fig1.add_trace(go.Scatter(x=w, y=to_db(he), name="椭圆",
                              line=dict(color="#10B981", width=2.5)))
    fig1.add_vline(x=1, line=dict(color="#EF4444", dash="dot", width=1.5))
    fig1.add_annotation(x=1, y=2, text="通带边缘 Ωc", showarrow=False, yshift=12,
                        font=dict(color="#EF4444", size=11))
    fig1.add_vline(x=2, line=dict(color="#94A3B8", dash="dot", width=1.5))
    fig1.add_annotation(x=2, y=2, text="2Ωc", showarrow=False, yshift=12,
                        font=dict(color="#94A3B8", size=11))
    fig1.update_xaxes(type="log", title="归一化频率 Ω / Ωc", range=[-0.5, 1.3])
    fig1.update_yaxes(title="幅度 (dB)", range=[-80, 5])
    fig1.update_layout(height=420, title="幅频响应（同阶数对比）",
                       legend=dict(orientation="h", y=-0.28, font=dict(size=10)),
                       margin=dict(t=50, b=10))
    st.plotly_chart(fig1, width="stretch")

with right:
    fig2 = go.Figure()
    fig2.add_hline(y=0, line=dict(color="#E2E8F0", width=1))
    fig2.add_vline(x=0, line=dict(color="#9CA3AF", width=1.2, dash="dash"))

    SETS = [("巴特沃斯", zb, pb, "#3B82F6"),
            ("切比雪夫 I 型", zc, pc, "#F59E0B"),
            ("椭圆", ze, pe, "#10B981")]

    for name, zz, pp, color in SETS:
        fig2.add_trace(go.Scatter(x=np.real(pp), y=np.imag(pp), mode="markers",
                                  name=f"{name} · 极点",
                                  marker=dict(symbol="x", size=12, color=color,
                                              line=dict(width=2.5))))
        if len(zz):
            fig2.add_trace(go.Scatter(x=np.real(zz), y=np.imag(zz), mode="markers",
                                      name=f"{name} · 零点",
                                      marker=dict(symbol="circle-open", size=12,
                                                  color=color, line=dict(width=2.5))))

    p_all = np.concatenate([pb, pc, pe])
    ylim = max(np.max(np.abs(p_all.imag)) * 1.2, 1.3)
    xlim = min(np.min(p_all.real) * 1.2, -1.3)
    fig2.update_xaxes(title="σ  (实轴)", range=[xlim - 0.2, 0.35])
    fig2.update_yaxes(title="jΩ  (虚轴)", range=[-ylim, ylim],
                      scaleanchor="x", scaleratio=1)
    fig2.update_layout(height=420, title="s 平面：极点 / 零点分布",
                       legend=dict(orientation="h", y=-0.3, font=dict(size=9)),
                       margin=dict(t=50, b=10))
    st.plotly_chart(fig2, width="stretch")


def gain_at(h, x):
    return 20 * np.log10(max(float(np.interp(x, w, np.abs(h))), 1e-12))


def stopband_edge(h, rs_db):
    mag = 20 * np.log10(np.maximum(np.abs(h), 1e-12))
    idx = np.where(mag <= -rs_db)[0]
    return float(w[idx[0]]) if idx.size else float("nan")


rows = []
for name, h, zz, pp in [("巴特沃斯", hb, zb, pb),
                        ("切比雪夫 I 型", hc, zc, pc),
                        ("椭圆", he, ze, pe)]:
    rows.append({
        "逼近类型": name,
        "Ω=Ωc 处增益 (dB)": round(gain_at(h, 1.0), 2),
        "Ω=2Ωc 处增益 (dB)": round(gain_at(h, 2.0), 1),
        f"降到 -{Rs} dB 处的 Ω/Ωc": round(stopband_edge(h, Rs), 2),
        "极点个数": len(pp),
        "零点个数": len(zz),
    })

df = pd.DataFrame(rows)
st.markdown(f"**同阶数 N = {N} 下的实测指标**（最后一列越小，过渡带越陡，越能省阶数）")
st.dataframe(df, width="stretch", hide_index=True)

n_butter = int(np.ceil(np.log10((10 ** (0.1 * Rs) - 1) / (10 ** (0.1 * 1.0) - 1)) / (2 * np.log10(2))))
st.info(
    f"📌 若要求「2 倍截止频率处衰减 ≥ {Rs} dB」，巴特沃斯至少需要 **N ≥ {n_butter}** 阶；"
    f"换切比雪夫或椭圆，同样指标需要的阶数更低 —— 这就是三大逼近法存在的意义。"
)

with st.expander("🎯 842 考点速记", expanded=False):
    st.markdown(r"""
**① 巴特沃斯 Butterworth**

- 幅度平方函数：$|H(j\Omega)|^2 = \dfrac{1}{1 + \left(\Omega/\Omega_c\right)^{2N}}$
- **通带最平坦**：前 $2N-1$ 阶导数在 $\Omega = 0$ 处全为零
- 极点公式：$p_k = \Omega_c\,\exp\!\left(j\pi\dfrac{2k + N + 1}{2N}\right)$，
  均匀分布在**半径为 $\Omega_c$ 的左半平面圆**上，关于实轴对称
- 阻带斜率：$-20N\ \mathrm{dB}/$十倍频（$-6N\ \mathrm{dB}/$倍频）
- **阶数公式（必背）**：
$$N \ge \frac{\lg\left(\dfrac{10^{0.1\alpha_s} - 1}{10^{0.1\alpha_p} - 1}\right)}{2\lg\left(\Omega_s/\Omega_p\right)}$$

**② 切比雪夫 I 型 Chebyshev I**

- 通带**等波纹**，波纹幅度 $\le R_p$ dB，$\Omega_p$ 处刚好跌到 $-R_p$
- 由切比雪夫多项式 $T_N(x) = \cos(N\arccos x)$ 而来
- **极点分布在椭圆上**：长轴沿虚轴、短轴沿实轴
- 与同阶巴特沃斯相比，**过渡带明显更窄**（用通带波纹换来陡度）
- 代价：群延迟起伏 → **相位非线性**

**③ 椭圆 Elliptic（Cauer）**

- **通带和阻带都等波纹**，$R_p$ 和 $R_s$ 都要给
- 极点分布椭圆上，**同时虚轴上有零点** —— 零点让阻带也起伏
- 同阶数下过渡带**最陡**，能省最多阶数
- 代价：相位非线性最严重，且阻带零点附近群延迟有尖峰
- 用 `signal.ellip(N, Rp, Rs, Wn, analog=True, output="zpk")` 时，$N$ 为偶数会得到 $N$ 个零点，奇数则是 $N-1$ 个

**④ 一句话结论（选择题高频）**

| 比较维度 | 排序 |
| :-- | :-- |
| 过渡带陡峭度（同阶） | 椭圆 > 切比雪夫 > 巴特沃斯 |
| 通带平坦度 | 巴特沃斯 > 切比雪夫 ≈ 椭圆 |
| 相位线性度 / 群延迟平坦度 | 巴特沃斯 > 切比雪夫 > 椭圆 |
| 对元件误差的敏感度 | 巴特沃斯最低（椭圆最高，所以实际电路少用高阶椭圆） |

**⑤ 为什么椭圆能那么陡？**

因为它在虚轴上 **主动放了零点**。$|H(j\Omega)|$ 在零点处直接归零，
阻带被"钉"在低位，所以通带到阻带的落差可以在很窄的一段频率里完成。

**⑥ 从模拟到数字**

本模块全是 **模拟原型**（$\Omega_c = 1$ rad/s 归一化）。
要用到数字信号上，就得经过 **模块⑧ 的冲激响应不变法或双线性变换** —— 两个模块是连着的一条线。
""")

st.divider()
st.caption("模块⑦ / signal-lab ｜ 下一步：FIR 滤波器设计（窗函数法）与频谱泄露")

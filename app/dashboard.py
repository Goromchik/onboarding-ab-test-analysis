import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd
import streamlit as st
import plotly.express as px

from src.stats import calculate_significance, summary_by_segment, srm_check, power_analysis

st.set_page_config(page_title="Дашборд A/B-теста", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("data/raw/experiment_data.csv")
    df["variant"] = df["variant"].astype(str)
    df["converted"] = df["converted"].astype(int)

    for col in ["acquisition_channel", "device_type", "region"]:
        df[col] = df[col].fillna("Unknown").astype(str)

    return df

df = load_data()

st.title("Дашборд A/B-теста: процесс адаптации")
st.caption("Анализ эксперимента для оценки влияния на конверсию и вовлеченность")

acquisition = st.selectbox(
    "Канал привлечения",
    ["Все"] + sorted(df["acquisition_channel"].dropna().unique().tolist())
)
device = st.selectbox(
    "Тип устройства",
    ["Все"] + sorted(df["device_type"].dropna().unique().tolist())
)
region = st.selectbox(
    "Регион",
    ["Все"] + sorted(df["region"].dropna().unique().tolist())
)

if acquisition != "Все":
    df = df[df["acquisition_channel"] == acquisition]
if device != "Все":
    df = df[df["device_type"] == device]
if region != "Все":
    df = df[df["region"] == region]

summary = calculate_significance(df)
srm = srm_check(df)
power = power_analysis(df)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Пользователи в контроле", summary["control_users"])
col2.metric("Пользователи в тесте", summary["treatment_users"])
col3.metric("CR в контроле", f"{summary['control_conversion_rate'] * 100:.2f}%")
col4.metric("CR в тесте", f"{summary['treatment_conversion_rate'] * 100:.2f}%")

st.markdown("---")

col5, col6, col7 = st.columns(3)
col5.metric("Абсолютный прирост", f"{summary['absolute_uplift'] * 100:.2f}% п.п.")
col6.metric("Относительный прирост", f"{summary['relative_uplift'] * 100:.2f}%")

if summary["p_value"] < 0.001:
    p_text = "p < 0.001"
else:
    p_text = f"p = {summary['p_value']:.3f}"

col7.metric("p-value", p_text)

if summary["significant_95"]:
    st.success("Разница статистически значима на уровне 95% доверия.")
else:
    st.warning("Разница не является статистически значимой на уровне 95% доверия.")

st.markdown("---")

st.subheader("Проверка рандомизации")
if srm["srm_ok"]:
    st.success("Смещение в распределении групп не обнаружено.")
else:
    st.warning("Есть признаки возможного смещения в распределении групп.")

st.write(f"Количество пользователей по группам: {srm['counts']}")
st.write(f"SRM p-value: {srm['p_value']:.4f}")

st.subheader("Проверка мощности")
st.write(f"Необходимо пользователей на группу для 80% мощности: {power['required_n_per_group']:.0f}")
if power["sample_size_sufficient"]:
    st.success("Текущий размер выборки достаточен для обнаружения эффекта.")
else:
    st.warning("Текущий размер выборки может быть недостаточен для обнаружения эффекта.")

st.markdown("---")

bar_df = pd.DataFrame({
    "variant": ["control", "treatment"],
    "conversion_rate": [
        summary["control_conversion_rate"],
        summary["treatment_conversion_rate"]
    ]
})

fig1 = px.bar(
    bar_df,
    x="variant",
    y="conversion_rate",
    color="variant",
    title="Коэффициент конверсии по вариантам"
)
fig1.update_yaxes(tickformat=".0%")
st.plotly_chart(fig1, use_container_width=True)

completion = (
    df.groupby("variant")["completed_onboarding"]
    .mean()
    .reset_index()
    .rename(columns={"completed_onboarding": "completion_rate"})
)

fig2 = px.bar(
    completion,
    x="variant",
    y="completion_rate",
    color="variant",
    title="Процент завершения онбординга по вариантам"
)
fig2.update_yaxes(tickformat=".0%")
st.plotly_chart(fig2, use_container_width=True)

segment_df = summary_by_segment(df, "device_type")
fig3 = px.bar(
    segment_df,
    x="device_type",
    y="conversion_rate",
    color="variant",
    barmode="group",
    title="Конверсия по типу устройства и варианту"
)
st.plotly_chart(fig3, use_container_width=True)

channel_df = summary_by_segment(df, "acquisition_channel")
fig4 = px.bar(
    channel_df,
    x="acquisition_channel",
    y="conversion_rate",
    color="variant",
    barmode="group",
    title="Конверсия по каналу привлечения и варианту"
)
st.plotly_chart(fig4, use_container_width=True)

st.markdown("### Сводная таблица")
summary_table = pd.DataFrame([
    {"Метрика": "Пользователи в контроле", "Значение": summary["control_users"]},
    {"Метрика": "Пользователи в тесте", "Значение": summary["treatment_users"]},
    {"Метрика": "Коэффициент конверсии в контроле", "Значение": f"{summary['control_conversion_rate'] * 100:.2f}%"},
    {"Метрика": "Коэффициент конверсии в тесте", "Значение": f"{summary['treatment_conversion_rate'] * 100:.2f}%"},
    {"Метрика": "Абсолютный прирост", "Значение": f"{summary['absolute_uplift'] * 100:.2f}% п.п."},
    {"Метрика": "Относительный прирост", "Значение": f"{summary['relative_uplift'] * 100:.2f}%"},
    {"Метрика": "p-value", "Значение": p_text}
])
st.dataframe(summary_table, use_container_width=True)
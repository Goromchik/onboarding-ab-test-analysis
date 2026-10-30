import numpy as np
from scipy.stats import chisquare
from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportions_ztest


def conversion_rate(series):
    return series.mean()


def uplift_rate(control_rate, treatment_rate):
    if control_rate == 0:
        return np.nan
    return (treatment_rate - control_rate) / control_rate


def calculate_significance(df):
    control = df[df["variant"] == "control"]
    treatment = df[df["variant"] == "treatment"]

    control_converted = int(control["converted"].sum())
    treatment_converted = int(treatment["converted"].sum())
    control_users = len(control)
    treatment_users = len(treatment)

    stat, p_value = proportions_ztest(
        [control_converted, treatment_converted],
        [control_users, treatment_users]
    )

    control_rate = control_converted / control_users
    treatment_rate = treatment_converted / treatment_users
    uplift = uplift_rate(control_rate, treatment_rate)

    result = {
        "control_users": control_users,
        "treatment_users": treatment_users,
        "control_conversion_rate": control_rate,
        "treatment_conversion_rate": treatment_rate,
        "absolute_uplift": treatment_rate - control_rate,
        "relative_uplift": uplift,
        "z_score": stat,
        "p_value": p_value,
        "significant_95": p_value < 0.05
    }
    return result


def summary_by_segment(df, group_col):
    table = (
        df.groupby([group_col, "variant"])["converted"]
        .agg(["count", "mean"])
        .reset_index()
    )
    table = table.rename(columns={"mean": "conversion_rate"})
    return table


def srm_check(df):
    counts = df["variant"].value_counts()
    expected = [len(df) / 2, len(df) / 2]
    chi2, p_value = chisquare(counts.values, f_exp=expected)
    return {
        "counts": counts.to_dict(),
        "chi2": chi2,
        "p_value": p_value,
        "srm_ok": p_value > 0.05
    }


def power_analysis(df):
    control_rate = df[df["variant"] == "control"]["converted"].mean()
    treatment_rate = df[df["variant"] == "treatment"]["converted"].mean()

    h = 2 * np.arcsin(np.sqrt(control_rate)) - 2 * np.arcsin(np.sqrt(treatment_rate))

    analysis = NormalIndPower()
    n_per_group = analysis.solve_power(
        effect_size=h,
        alpha=0.05,
        power=0.8,
        ratio=1
    )

    return {
        "control_rate": control_rate,
        "treatment_rate": treatment_rate,
        "effect_size_h": h,
        "required_n_per_group": n_per_group,
        "sample_size_sufficient": min(df["variant"].value_counts()) >= n_per_group
    }
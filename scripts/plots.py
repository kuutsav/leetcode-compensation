from collections import Counter

import altair as alt
import pandas as pd
import numpy as np

from leetcode.all_info import get_clean_records_for_india
from leetcode.utils.constants import IMGS_DIR, MISSING_NUMERIC, MISSING_TEXT

alt.renderers.set_embed_options(theme="dark")
MISSING_TEXT_UPPER = MISSING_TEXT.upper()

DARK_BACKGROUND = "#22272D"
LIGHT_BAR = "mediumseagreen"
DARK_BAR = "#F9A089"


# load data
df = get_clean_records_for_india()
df = df[["href", "post_title", "date", "post", "company", "title", "yoe", "salary", "location"]]

# prep formatted columns
df["lpa"] = df["salary"] / 1_00_000
df["Years of Experience (bucket)"] = pd.cut(
    df["yoe"], bins=[-0.1, 1, 3, 6, 9, 15, 100], labels=["0-1", "1-3", "3-6", "6-9", "9-15", "15+"]
)
df.rename(columns={"yoe": "Years of Experience"}, inplace=True)
df["company"] = df["company"].str.upper()
df["title"] = df["title"].str.upper()

# salary percentiles
p75, p95, p99 = (np.percentile(df["lpa"], 75), np.percentile(df["lpa"], 95), np.percentile(df["lpa"], 99))
pdf = pd.DataFrame({"p75": [p75], "p95": [p95], "p99": [p99]})

# salary distribution --------------------------------------------------------------------------------------------------
bar = (
    alt.Chart(df)
    .mark_bar(size=23)
    .encode(
        x=alt.X("lpa", bin=alt.Bin(maxbins=35), title="₹ LPA"),
        y=alt.Y("count()", axis=alt.Axis(title="Count of Records")),
        color=alt.value(LIGHT_BAR),
    )
    .properties(width=900, height=350)
)
rule1 = alt.Chart(pdf).mark_rule(color="black", strokeDash=[2, 2], size=1.5).encode(x="p75:Q")
rule2 = alt.Chart(pdf).mark_rule(color="grey", strokeDash=[2, 2]).encode(x="p95:Q")
rule3 = alt.Chart(pdf).mark_rule(color="grey", strokeDash=[2, 2]).encode(x="p99:Q")
final_bar = bar + rule1 + rule2 + rule3
final_bar.save(f"{IMGS_DIR}/salary_distribution.png")

# dark mode
bar = (
    alt.Chart(df)
    .mark_bar(size=23)
    .encode(
        x=alt.X("lpa", bin=alt.Bin(maxbins=35), title="₹ LPA"),
        y=alt.Y("count()", axis=alt.Axis(title="Count of Records")),
        color=alt.value(DARK_BAR),
    )
    .properties(width=900, height=350)
)

rule1_dark = alt.Chart(pdf).mark_rule(color="white", strokeDash=[2, 2], size=1.5).encode(x="p75:Q")
final_bar = (
    (bar + rule1_dark + rule2 + rule3)
    .configure(background=DARK_BACKGROUND)
    .configure_axisLeft(labelColor="white", titleColor="white")
    .configure_axisBottom(labelColor="white", titleColor="white")
)
final_bar.save(f"{IMGS_DIR}/salary_distribution_dark.png")

# company distribution -------------------------------------------------------------------------------------------------
comp_counter = Counter(df["company"])
top_companies = [comp[0] for comp in comp_counter.most_common(32) if comp[0] != MISSING_TEXT_UPPER]

chart = (
    alt.Chart(df[df.company.isin(top_companies)])
    .mark_bar(size=25)
    .encode(
        x=alt.X("company", sort="-y", axis=alt.Axis(title=None)),
        y=alt.Y("count()", axis=alt.Axis(title="Count of Records")),
        color=alt.value(LIGHT_BAR),
    )
    .properties(width=900, height=350)
)
chart.save(f"{IMGS_DIR}/company_distribution.png")

chart = (
    alt.Chart(df[df.company.isin(top_companies)])
    .mark_bar(size=25)
    .encode(
        x=alt.X("company", sort="-y", axis=alt.Axis(title=None)),
        y=alt.Y("count()", axis=alt.Axis(title="Count of Records")),
        color=alt.value(DARK_BAR),
    )
    .properties(width=900, height=350)
    .configure(background=DARK_BACKGROUND)
    .configure_axisLeft(labelColor="white", titleColor="white")
    .configure_axisBottom(labelColor="white", titleColor="white")
)
chart.save(f"{IMGS_DIR}/company_distribution_dark.png")

# company x salary distribution ----------------------------------------------------------------------------------------
bar = (
    alt.Chart(df[df["company"].isin(top_companies)])
    .mark_circle(size=50)
    .encode(
        x=alt.X("lpa", axis=alt.Axis(title="₹ LPA")),
        y=alt.Y(
            "company", axis=alt.Axis(title=None), sort=alt.EncodingSortField(field="lpa", op="mean", order="descending")
        ),
        color=alt.Color("company", legend=None),
    )
    .properties(width=850, height=800)
)
chart = bar + rule1 + rule2 + rule3
chart.save(f"{IMGS_DIR}/company_salary_distribution.png")

bar = (
    alt.Chart(df[df["company"].isin(top_companies)])
    .mark_circle(size=50)
    .encode(
        x=alt.X("lpa", axis=alt.Axis(title="₹ LPA")),
        y=alt.Y(
            "company", axis=alt.Axis(title=None), sort=alt.EncodingSortField(field="lpa", op="mean", order="descending")
        ),
        color=alt.Color("company", legend=None),
    )
    .properties(width=850, height=800)
)
chart = (
    (bar + rule1_dark + rule2 + rule3)
    .configure(background=DARK_BACKGROUND)
    .configure_axis(grid=False)
    .configure_axisLeft(labelColor="white", titleColor="white")
    .configure_axisBottom(labelColor="white", titleColor="white")
)
chart.save(f"{IMGS_DIR}/company_salary_distribution_dark.png")

# title x salary distribution ------------------------------------------------------------------------------------------
title_counter = Counter(df["title"])
top_titles = [title[0] for title in title_counter.most_common(21) if title[0] != MISSING_TEXT_UPPER]

bar = (
    alt.Chart(df[df["title"].isin(top_titles)])
    .mark_boxplot(size=25, color="grey")
    .encode(
        x=alt.X("lpa", title="₹ LPA"),
        y=alt.Y("title", axis=alt.Axis(title=None)),
        color=alt.Color("title", legend=None),
    )
    .properties(width=800, height=600)
)
chart = (bar + rule1 + rule2 + rule3).configure_point(size=8)
chart.save(f"{IMGS_DIR}/title_salary_distribution.png")

bar = (
    alt.Chart(df[df["title"].isin(top_titles)])
    .mark_boxplot(size=25, color="grey")
    .encode(
        x=alt.X("lpa", title="₹ LPA"),
        y=alt.Y("title", axis=alt.Axis(title=None)),
        color=alt.Color("title", legend=None),
    )
    .properties(width=800, height=600)
)
chart = (
    (bar + rule1_dark + rule2 + rule3)
    .configure_point(size=8)
    .configure(background=DARK_BACKGROUND)
    .configure_axis(grid=False)
    .configure_axisLeft(labelColor="white", titleColor="white")
    .configure_axisBottom(labelColor="white", titleColor="white")
)
chart.save(f"{IMGS_DIR}/title_salary_distribution_dark.png")

# yoe x salary ---------------------------------------------------------------------------------------------------------
chart = (
    alt.Chart(df[(df["Years of Experience"] != MISSING_NUMERIC)])
    .mark_point(color="black", size=10)
    .encode(
        x="Years of Experience",
        y=alt.Y("lpa", title="₹ LPA"),
        color=alt.condition('datum.company=="AMAZON"', alt.ColorValue("orange"), alt.ColorValue("black")),
    )
    .properties(width=800, height=600)
)
chart.save(f"{IMGS_DIR}/yoe_salary_distribution.png")

chart = (
    alt.Chart(df[(df["Years of Experience"] != MISSING_NUMERIC)])
    .mark_point(color="white", size=10)
    .encode(
        x="Years of Experience",
        y=alt.Y("lpa", title="₹ LPA"),
        color=alt.condition('datum.company=="AMAZON"', alt.ColorValue("orange"), alt.ColorValue("white")),
    )
    .properties(width=800, height=600)
    .configure(background=DARK_BACKGROUND)
    .configure_axis(grid=False)
    .configure_axisLeft(labelColor="white", titleColor="white")
    .configure_axisBottom(labelColor="white", titleColor="white")
)
chart.save(f"{IMGS_DIR}/yoe_salary_distribution_dark.png")


# yoe_bucket x salary --------------------------------------------------------------------------------------------------
chart = (
    alt.Chart(df[(df["Years of Experience"] != MISSING_NUMERIC) & (df["Years of Experience (bucket)"] != "15+")])
    .mark_boxplot(color="grey", size=40)
    .encode(
        x="Years of Experience (bucket)",
        y=alt.Y("lpa", title="₹ LPA"),
        color=alt.value(LIGHT_BAR),
    )
    .properties(width=800, height=500)
)
chart.save(f"{IMGS_DIR}/yoebucket_salary_distribution.png")

chart = (
    alt.Chart(df[(df["Years of Experience"] != MISSING_NUMERIC) & (df["Years of Experience (bucket)"] != "15+")])
    .mark_boxplot(color="grey", size=40)
    .encode(
        x="Years of Experience (bucket)",
        y=alt.Y("lpa", title="₹ LPA"),
        color=alt.value(DARK_BAR),
    )
    .properties(width=800, height=500)
    .configure(background=DARK_BACKGROUND)
    .configure_axisLeft(labelColor="white", titleColor="white")
    .configure_axisBottom(labelColor="white", titleColor="white")
)
chart.save(f"{IMGS_DIR}/yoebucket_salary_distribution_dark.png")

# top_companies x salary -----------------------------------------------------------------------------------------------
top_c = ["GOOGLE", "AMAZON", "MICROSOFT", "UBER"]

chart = (
    alt.Chart(
        df[
            (df["Years of Experience"] != MISSING_NUMERIC)
            & (df["company"].isin(top_c))
            & (df["Years of Experience (bucket)"] != "15+")
        ]
    )
    .mark_boxplot(color="grey", size=10)
    .encode(
        x=alt.X("company", title=None),
        y=alt.Y("lpa", title="₹ LPA"),
        color="company",
        column=alt.Column("Years of Experience (bucket)"),
    )
    .properties(width=150, height=500)
)
chart.save(f"{IMGS_DIR}/top_companies_salary_distribution.png")

chart = (
    alt.Chart(
        df[
            (df["Years of Experience"] != MISSING_NUMERIC)
            & (df["company"].isin(top_c))
            & (df["Years of Experience (bucket)"] != "15+")
        ]
    )
    .mark_boxplot(color="grey", size=10)
    .encode(
        x=alt.X("company", title=None),
        y=alt.Y("lpa", title="₹ LPA"),
        color="company",
        column=alt.Column("Years of Experience (bucket)"),
    )
    .properties(width=150, height=500)
    .configure(background=DARK_BACKGROUND)
    .configure_legend(labelColor="white", titleColor="white")
    .configure_axisLeft(labelColor="white", titleColor="white")
    .configure_axisBottom(labelColor="white", titleColor="white")
    .configure_axisTop(labelColor="white", titleColor="white")
)
chart.save(f"{IMGS_DIR}/top_companies_salary_distribution_dark.png")

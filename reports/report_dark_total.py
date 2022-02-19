from info.all_info import get_clean_records_for_india
from utils.constant import MISSING_NUMERIC, REPORTS_DIR


# data
df = get_clean_records_for_india()
df = df.loc[df["salary_total"] != MISSING_NUMERIC, :]
min_date, max_date = df["date"].min().replace("/", "_"), df["date"].max().replace("/", "_")

with open(f"{REPORTS_DIR}/report_{min_date}_to_{max_date}_dark_tc.md", "w") as f:
    f.write("## Notes")
    f.write(f"\n- Reports are generated from `{df.shape[0]}` records collected from `{min_date}` to `{max_date}`.")
    f.write("\n- Filtered for `India`.<br>")
    f.write("\n- Salary mentioned in the reports is the `total salary`.<br>")
    f.write("\n- Vertical lines in some of the charts indicate the `75th`, `95th` and the `99th` percentile of the `fixed salaries`.<br>")

    f.write("\n\n`Salary Distribution`")
    f.write(f"\n![salary](../imgs/salary_distribution_dark_total.png)")

    f.write("\n\n`Company Counts`")
    f.write(f"\n![salary](../imgs/company_distribution_dark_total.png)")

    f.write("\n\n`Salaries by Companies`")
    f.write(f"\n![salary](../imgs/company_salary_distribution_dark_total.png)")

    f.write("\n\n`Salaries by Titles`")
    f.write(f"\n![salary](../imgs/title_salary_distribution_dark_total.png)")

    f.write("\n\n`Salaries by Experience(Amazon in orange)`")
    f.write(f"\n![salary](../imgs/yoe_salary_distribution_dark_total.png)")

    f.write("\n\n`Salaries by Experience buckets`")
    f.write(f"\n![salary](../imgs/yoebucket_salary_distribution_dark_total.png)")

    f.write("\n\n`Salaries by Experience buckets(top comapnies)`")
    f.write(f"\n![salary](../imgs/top_companies_salary_distribution_dark_total.png)")

    f.write("\n\n## Top Offers")

    sample_df = df[["post_title", "href", "date", "company", "title", "yoe",
                    "salary_total", "location", "post"]].sort_values(by="salary_total", ascending=False)[:10]
    for r in sample_df.iterrows():
        r = r[1]
        f.write(f'\n\ntitle : {r["post_title"]}<br>')
        f.write(f'url : {r["href"]}<br>')
        f.write(f'date : `{r["date"]}`<br>')
        f.write(f'company : `{r["company"]}`<br>')
        f.write(f'title : `{r["title"]}`<br>')
        f.write(f'yoe : `{r["yoe"]}` years<br>')
        f.write(f'salary : `₹ {int(r["salary_total"])}`<br>')
        f.write(f'location : `{r["location"]}`<br>')
        f.write(f'`post`\n{r["post"]}<br>')
        f.write('---')

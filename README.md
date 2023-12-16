# Leetcode Compensations report

Scraping and analysis of the `leetcode-compensations` page (for India).

> Check out https://github.com/kuutsav/LeetComp for an interactive version of this report.

![Salary](data/imgs/salary_distribution_dark.png)

## Reports

-- [Fixed salary: 29th Dec 2022 - 17th Dec 2023](data/reports/report_2022_12_29_to_2023_12_17.md)<br>
-- [Total salary: 29th Dec 2022 - 17th Dec 2023](data/reports/report_2022_12_29_to_2023_12_17_tc.md)<br>
-- [Fixed salary(Dark mode): 29th Dec 2022 - 17th Dec 2023](data/reports/report_2022_12_29_to_2023_12_17_dark.md)<br>
-- [Total salary(Dark mode): 29th Dec 2022 - 17th Dec 2023](data/reports/report_2022_12_29_to_2023_12_17_dark_tc.md)

-- [Fixed salary: 5th Jan 2019 - 18th Jan 2022](data/reports/report_2019_01_05_to_2022_01_18.md)<br>
-- [Total salary: 5th Jan 2019 - 18th Jan 2022](data/reports/report_2019_01_05_to_2022_01_18_tc.md)<br>
-- [Fixed salary(Dark mode): 5th Jan 2019 - 18th Jan 2022](data/reports/report_2019_01_05_to_2022_01_18_dark.md)<br>
-- [Total salary(Dark mode): 5th Jan 2019 - 18th Jan 2022](data/reports/report_2019_01_05_to_2022_01_18_dark_tc.md)

## Setup

```bash
$ git clone <repo>
$ python3 -m venv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
```

<!-- 5. To create the reports - `npm install vega-lite vega-cli canvas`(needed to save altair plots). -->

## Data update

First we need to fetch the posts metadata. This inlvolves fetching the post ids from each page (till_date -> today).
```bash
$ source .venv/bin/activate
$ PYTHONPATH=. python leetcode/posts_meta.py --till_date 2023/01/01
```

The next step if to fetch the actual post content for each of the post ids from the previous step.
```bash
$ source .venv/bin/activate
$ PYTHONPATH=. python leetcode/posts.py --posts_meta F
```

## Generating the reports

```bash
$ source .venv/bin/activate

$ python scripts/plots.py  # generate fixed comp. plots
$ python scripts/report.py  # fixed comp.
$ python scripts/report_dark.py  # fixed comp., dark mode

$ python scripts/plots_total.py  # generate total comp. plots
$ python scripts/report_total.py  # total comp.
$ python scripts/report_dark_total.py  # total comp., dark mode
```

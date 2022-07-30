# Leetcode Compensations report

Scraping and analysis of the `leetcode-compensations` page (for India).

> Check out https://github.com/kuutsav/LeetComp for an interactive version of this report.

![Salary](data/imgs/salary_distribution_dark.png)

## Reports

  - [fixed salary - 5th Jan 2019 - 18th Jan 2022](data/reports/report_2019_01_05_to_2022_01_18.md)
  - [total salary - 5th Jan 2019 - 18th Jan 2022](data/reports/report_2019_01_05_to_2022_01_18_tc.md)
  - [fixed salary, dark mode - 5th Jan 2019 - 18th Jan 2022](data/reports/report_2019_01_05_to_2022_01_18_dark.md)
  - [total salary, dark mode - 5th Jan 2019 - 18th Jan 2022](data/reports/report_2019_01_05_to_2022_01_18_dark_tc.md)

## Directory structure

  - data
    - imgs: images for reports
    - logs: scraping logs
    - mappings: standardized company, location and title mappings as well as unmapped entities
    - meta: meta information for the posts like post_id, date, title, href
    - out: data from `info.all_info.get_clean_records_for_india()`
    - posts: text from the post 
    - reports: salary analysis by companies, titles and experience 
  - info: functions to parse data from posts(along with the standardized entities) in a tabular format
  - leetcode: scraper
  - utils: helper methods

## Setup

1. Clone the repo.
2. Put the `chromedriver` in the utils directory.
3. Setup virual enviroment - `python -m venv leetcode`.
4. Install necessary packages - `pip install -r requirements.txt`.
5. To create the reports - `npm install vega-lite vega-cli canvas`(needed to save altair plots).

## Generating reports

### Scraping

```python
$ export PTYHONPATH=<project_directory>
$ python leetcode/posts_meta.py --till_date 2021/08/03

# sample output
2021-08-03 19:36:07.474 | INFO     | __main__:<module>:48 - page no: 1 | # posts: 15
```

```python
$ python leetcode/posts.py

# sample output
2021-08-03 19:36:25.997 | INFO     | __main__:<module>:45 - post_id: 1380805 done!
2021-08-03 19:36:28.995 | INFO     | __main__:<module>:45 - post_id: 1380646 done!
2021-08-03 19:36:31.631 | INFO     | __main__:<module>:45 - post_id: 1380542 done!
2021-08-03 19:36:34.727 | INFO     | __main__:<module>:45 - post_id: 1380068 done!
2021-08-03 19:36:37.280 | INFO     | __main__:<module>:45 - post_id: 1379990 done!
2021-08-03 19:36:40.509 | INFO     | __main__:<module>:45 - post_id: 1379903 done!
2021-08-03 19:36:41.096 | WARNING  | __main__:<module>:34 - sleeping extra for post_id: 1379487
2021-08-03 19:36:44.530 | INFO     | __main__:<module>:45 - post_id: 1379487 done!
2021-08-03 19:36:47.115 | INFO     | __main__:<module>:45 - post_id: 1379208 done!
2021-08-03 19:36:49.660 | INFO     | __main__:<module>:45 - post_id: 1378689 done!
2021-08-03 19:36:50.470 | WARNING  | __main__:<module>:34 - sleeping extra for post_id: 1378620
2021-08-03 19:36:53.866 | INFO     | __main__:<module>:45 - post_id: 1378620 done!
2021-08-03 19:36:57.203 | INFO     | __main__:<module>:45 - post_id: 1378334 done!
2021-08-03 19:37:00.570 | INFO     | __main__:<module>:45 - post_id: 1378288 done!
2021-08-03 19:37:03.226 | INFO     | __main__:<module>:45 - post_id: 1378181 done!
2021-08-03 19:37:05.895 | INFO     | __main__:<module>:45 - post_id: 1378113 done!
```

### Generating pandas DataFrame for the reports

```python
$ ipython

In [1]: from info.all_info import get_clean_records_for_india
In [2]: df = get_clean_records_for_india()
2021-08-04 15:47:11.615 | INFO     | info.all_info:get_raw_records:95 - n records: 4134
2021-08-04 15:47:11.616 | WARNING  | info.all_info:get_raw_records:97 - missing post_ids: ['1347044', '1193859', '1208031', '1352074', '1308645', '1206533', '1309603', '1308672', '1271172', '214751', '1317751', '1342147', '1308728', '1138584']
2021-08-04 15:47:11.696 | WARNING  | info.all_info:_save_unmapped_labels:54 - 35 unmapped company saved
2021-08-04 15:47:11.705 | WARNING  | info.all_info:_save_unmapped_labels:54 - 353 unmapped title saved
2021-08-04 15:47:11.708 | WARNING  | info.all_info:get_clean_records_for_india:122 - 1779 rows dropped(location!=india)
2021-08-04 15:47:11.709 | WARNING  | info.all_info:get_clean_records_for_india:128 - 385 rows dropped(incomplete info)
2021-08-04 15:47:11.710 | WARNING  | info.all_info:get_clean_records_for_india:134 - 7 rows dropped(internships)
In [3]: df.shape
Out[3]: (1963, 14)
```

### Generating the reports

```python
$ python reports/plots.py # generate fixed comp. plots
$ python reports/report.py # fixed comp.
$ python reports/report_dark.py # fixed comp., dark mode

$ python reports/plots_total.py # generate total comp. plots
$ python reports/report_total.py # total comp.
$ python reports/report_dark_total.py # total comp., dark mode
```

## Sample

| Key      | Value                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| title    | Flipkart Software Development Engineer-1, Bangalore                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| url      | https://leetcode.com/discuss/compensation/834212/Flipkart-or-Software-Development-Engineer-1-or-Bangalore                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| company  | `flipkart`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| title    | `sde 1`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| yoe      | `0.0` years                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| salary   | `₹ 1800000.0`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| location | `bangalore`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| post     | Education: B.Tech from NIT (2021 passout)\nYears of Experience: 0\nPrior Experience: Fresher\nDate of the Offer:\nAug 2020\nCompany: Flipkart\nTitle/Level: Software Development Engineer-1\nLocation: Bangalore\nSalary: INR 18,00,000\nPerformance Incentive: INR 1,80,000 (10% of base pay)\nESOPs: 48 units => INR 5,07,734 (vested over 4 years. 25% each year)\nRelocation Reimbursement: INR 40,000\nTelephone Reimbursement: INR 12,000\nHome Broadband Reimbursement: INR 12,000\nGratuity: INR 38,961\nInsurance: INR 27,000\nOther Benefits: INR 40,000 (15 days accomodation + travel) (this is different from the relocation reimbursement)\nTotal comp (Salary + Bonus + Stock): Total CTC: INR 26,57,695; First year: INR 22,76,895\nOther details: Standard Offer for On-Campus Hire\nAllowed Branches: B.Tech CSE/IT (6.0 CGPA & above)\nProcess consisted of Coding test & 3 rounds of interviews. I don't remember questions exactly. But they vary from topics such as Graph(Topological Sort, Bi-Partite Graph), Trie based questions, DP based questions both recursive and dp approach, trees, Backtracking. |

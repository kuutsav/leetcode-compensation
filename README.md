# Leetcode compensations report
Scraping and analysis of leetcode-compensations page.

## Directory structure
- data
    - mappings - standardized company, location and title mappings
    - ner - data for NER models
    - out - data for compensation analysis
    - posts - actual posts
    - stats - scraping stats
- info - functions to get tagged data as well as final data in tabular format
- lc - scraper
- ner - NER training and evaluation (WIP)
- utils - constants and helper methods

## Setup
1. Create the directory structure if starting from scratch
2. Put the `chromedriver` at the root of the project
3. Install necessary packages `pip install -r requirements.txt`.

## Scraping
```bash
export PTYHONPATH=<project_directory>
$ python lc/comps.py --start_page <start_page_no> --end_page <end_page_no>
```

## Report DataFrame
```python
from info.all_info import get_info_df
df = get_info_df()
```

## Sample
```python
from random import sample
from ner.label_prep import _get_ner_tagging_data, get_ner_printable_text

tagging_data = _get_ner_tagging_data()
for d in sample(tagging_data["tags"], 3):
    print(get_ner_printable_text(d))
    print("\n")
    print("-" * 10)
    print("\n")
```

```text
education: b.tech tier 3 college
years of experience: [fresher:yoe]
prior experience: na
company: [tcs:company]
title/level: [system software engineer:title]
location: [banglore:location]
salary: [366000:salary]
total comp (salary + bonus + stock): 366000
benefits: standard
offcampus placement


----------


years of experience: [5:yoe]
prior experience: non-faang company
date of the offer: march 2021
company: [informatica:company]
title/level: [senior software engineer:title]
location: [bangalore, india:location]
salary: ~26,00,000 inr
relocation: 50,000 inr
signing bonus: na
stock bonus: na
bonus: performance-based target bonus of 10% of salary every year
total comp (salary + bonus ): 26 lakh + 2.6 lakh = 28.6 lakh for first year
benefits: standard
other details: did not negotiate. declined offer.


----------


education: b.tech in computer science
years of experience: [8:yoe]
prior experience: samsung
date of the offer: feb, 2019
company: [informatica:company]
title/level: [lead engineer:title]
location: [bangalore, india:location]
salary: [24,00,000 inr:salary]
signing bonus: 0
stock bonus: none
bonus: performance- 10% of salary (2,40,000)
total comp (salary + bonus + stock): ~ 26,40,000
benefits: free food at office.
other details: employee provident fund, gratuity, medical not part of ctc. got 40% hike on current ctc.


----------
```
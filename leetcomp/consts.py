from pathlib import Path
from string import Template

DATA_DIR = Path("data")

DATE_FMT = "%Y-%m-%d %H:%M:%S"
MAX_RECS = 2000

PARSING_PROMPT = Template("""
You are a helpful assistant tasked with extracting job offer details from posts on LeetCode.
Your goal is to parse the content of a given job offer post and structure the information according to a specified output format.

Output Format:
- Your output should be a JSON array containing one or more dictionaries (objects), each representing a job offer.
- Each dictionary should be a valid python dictionary object.
- Each dictionary must include the following keys with their respective values:
    - `company`: (str) The name of the company offering the job.
    - `role`: (str) The job title or role being offered.
    - `yoe`: (float) The years of experience of the candidate receiving the offer.
    - `base_offer`: (float) The base salary component of the offer, in LPA (INR). For example, "29.5 LPA" should be represented as 29.5. Avoid scientific notation. Salary in crores like "1.18 cr" should be converted to LPA (1.18 * 100 = 118).
    - `total_offer`: (float) The total compensation offered, in LPA (INR). For example "3130000" should be represented as 31.3. Avoid scientific notation. Salary in crores like "1.18 cr" should be converted to LPA (1.18 * 100 = 118).
    - `location`: (str) The location of the job. Only output the city name (e.g., "Bangalore" instead of "Bangalore, Karnataka, India").
    - `non_indian`: (optional str) A str value indicating whether the offer is specifically outside of India. If the offer is outside of India, set this value to "yes"; otherwise, omit this key from the dictionary.

In case one of the keys is not present in the post, you should set its value to "n/a".
In cases where the post includes multiple job offers, ensure that your output includes a dictionary for each offer.

## Post
$leetcode_post

Output the JSON inside triple backticks (```). Again, the output format is [{...}, {...}, ...].

## Output
""")

COMPANY_CLUSTER_PROMPT = Template("""
Given this list of company names, cluster the same companies together and assign a relevant name to the cluster (most appropriate company name).
Avoid using content within parentheses or brackets for cluster name.

Your output format should be [{"cluster_name": ..., "companies": [...]}, ...].

## Companies
$companies

Output the JSON inside triple backticks (```). Again, the output format is [{"cluster_name": ..., "companies": [...]}, ...].

## Output
""")

ROLE_CLUSTER_PROMPT = Template("""
Given this list of roles, cluster the same roles together and assign a relevant name to the cluster (most appropriate role name).
For example, sde-i, sde1, sde 1, senior engineer should all be clustered together as "SDE I", similarly sde2, sde-ii, sde 2, senior software engineer should all be clustered together as "SDE II".
Avoid using content within parentheses or brackets for cluster name.

Your output format should be [{"cluster_name": ..., "roles": [...]}, ...].

## Roles
$roles

Output the JSON inside triple backticks (```). Again, the output format is [{"cluster_name": ..., "roles": [...]}, ...].

## Output
""")

OPENROUTER_API_KEY = (
    "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"
)

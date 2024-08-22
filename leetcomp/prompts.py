from string import Template

PARSING_PROMPT = Template("""
You are a helpful assistant tasked with extracting job offer details from posts on LeetCode.
Below is the expected output format.

## Output Format
The output should be a JSON array containing one or more dictionaries, each representing a job offer.
Each dictionary must include the following keys with their respective values:
- company (str): The name of the company offering the job.
- role (str): The job title or role being offered.
- yoe (float): The years of experience of the candidate receiving the offer.
- base_offer (float): The base salary component of the offer, in LPA (INR).
  For example, "29.5 LPA" should be represented as 29.5. Avoid scientific notation.
  Salary in crores like "1.18 cr" should be converted to LPA (1.18 * 100 = 118).
- total_offer (float): The total compensation offered, in LPA (INR).
  For example, "3130000" should be represented as 31.3. Avoid scientific notation.
  Salary in crores like "1.18 cr" should be converted to LPA (1.18 * 100 = 118).
- location (str): The location of the job. Only output the city name (e.g., "Bangalore" instead of "Bangalore, India").
- non_indian (optional str): If the post mentions a location outside of india or the currency is not in INR set this key to "yes"; otherwise omit this key.

## Instructions
- If a key is not present in the post, set its value to "n/a".
- For posts with multiple job offers, include a dictionary for each offer.
- Sometimes users metion details about their current role and salary, ignore these details.

Your goal is to parse the content of the post below and structure the information into a specified JSON format by
following the "Output Format" and "Instructions" mentioned above.

## Post
$leetcode_post

## Parsed Job Offer (Output the JSON inside triple backticks (```). The format is [{...}, {...}, ...])
""")

COMPANY_CLUSTER_PROMPT = Template("""
Given this list of companies, cluster the same companies together and assign a relevant name to the cluster.
Avoid using content within parentheses or brackets for the company cluster name.

Your output format should be [{"cluster_name": ..., "companies": [...]}, ...].

## Companies
$companies

## Output (Output the JSON inside triple backticks (```). Again, the output format is [{"cluster_name": ..., "companies": [...]}, ...])
""")

ROLE_CLUSTER_PROMPT = Template("""
Given this list of roles, cluster the same roles together and assign a relevant name to the cluster.
For example, sde-i, sde1, sde 1, senior engineer should all be clustered together as "SDE I",
similarly sde2, sde-ii, sde 2, senior software engineer should all be clustered together as "SDE II".
Avoid using content within parentheses or brackets for cluster name.

Your output format should be [{"cluster_name": ..., "roles": [...]}, ...].

## Roles
$roles

## Output (Output the JSON inside triple backticks (```). Again, the output format is [{"cluster_name": ..., "roles": [...]}, ...])
""")

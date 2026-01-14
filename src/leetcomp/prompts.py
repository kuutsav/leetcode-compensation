from leetcomp import NormalizedEntity

COMPENSATION_PARSING_PROMPT = """You are a helpful assistant tasked with extracting job offer details from LeetCode compensation posts from India.

## Task
Parse the post and extract compensation details ONLY for India-based offers. Output the information in XML format.

## Rules
1. **India-based offers only - CURRENCY IS THE PRIMARY INDICATOR**: Parse posts where:
   - **PRIMARY RULE**: Salary mentioned in Lakhs/Lacs/LPA/Rupees/₹/INR → This ALWAYS means India, regardless of location wording
   - If you see "30 lacs" or "25 LPA" or "₹10,000" → It's an India offer even if location just says "Remote" or doesn't mention a city
   - Location mentions Indian cities (Bangalore, Delhi, Mumbai, Hyderabad, Pune, Noida, Gurgaon, Chennai, Kolkata, etc.)
   - Post says "Remote from India" (even if foreign company/currency like EUR/USD)
   - **IMPORTANT**: "Lakhs" or "Lacs" is uniquely Indian terminology - treat it as a definitive India signal

2. **Skip non-India offers**: If the offer is:
   - For locations outside India (US, Europe, Singapore, etc.) AND salary is in $ or other foreign currency WITHOUT "remote from India"
   - Example: "Mountain View, $200K" (no mention of India) → Skip this
   - Example: "Singapore, SGD 150K" (no mention of India) → Skip this
   - BUT if it says "Remote from India" with foreign currency → Parse it
   - Output: <compensation-post>false</compensation-post><reason>non-india-offer</reason>

3. **Skip non-compensation posts**: If the post is about:
   - Problem sets, coding patterns, interview experiences without offers
   - Career advice questions
   - General discussions
   - Output: <compensation-post>false</compensation-post><reason>not-about-job-offer</reason>

4. **Extract key fields**:
   - company: Company name as mentioned in the post (original form)
   - company-normalized: Normalized company name (best effort)
   - role: Job role/title as mentioned in the post (original form)
   - role-normalized: Normalized role using short forms/abbreviations (best effort)
   - yoe: Years of experience in decimal (e.g., 4.5)
   - base: Base salary in lakhs per annum (extract just the number, e.g., "49 LPA" → 49)
   - total: Total compensation in lakhs per annum as explicitly mentioned by user (e.g., "Total: 62 LPA" → 62)
   - total-calculated: Use this ONLY when user does NOT explicitly mention total but provides components (base + bonus + stocks/RSUs/ESOPs). Calculate by adding all components (annualize stocks over vesting period, typically 4 years). If insufficient info, omit this field.
   - location: City name only (e.g., "Bangalore" not "Bangalore, India"), or "Remote". If no city is mentioned then leave this field out.
   - currency: INR, EUR, USD, etc.
   - offer-type: "full-time" or "internship"

5. **CRITICAL - INR to Lakhs conversion**:
   - 1 Lakh = 1,00,000 INR (100,000 INR)
   - When salary is in raw INR: divide by 100,000 to get LPA
     - Example: "1,917,000 INR" = 1,917,000 ÷ 100,000 = **19.17 LPA** (NOT 191.7)
     - Example: "10,500,000 INR" = 10,500,000 ÷ 100,000 = **105 LPA**
   - When salary already has "L", "Lac", "Lakh", or "LPA" suffix: use the number directly
     - Example: "9.4L" = **9.4 LPA** (NOT 94)
     - Example: "37 LPA" = **37 LPA**
     - Example: "1.5 Cr" = 150 LPA (1 Crore = 100 Lakhs)
   - Common mistake to AVOID: Do NOT multiply values that are already in Lakhs

6. **Normalize company and role names (BEST EFFORT)**:
   - **Company normalization** (company-normalized field):
     - Convert to lowercase
     - Normalize common variations to a single form
     - Examples: "LinkedIn" or "linkedin" → "linkedin"
     - Examples: "Samsung R&D" or "Samsung Electronics" → "samsung"
     - Examples: "Google" or "GOOGLE" → "google"
     - Remove unnecessary suffixes/divisions when the core company is clear
   - **Role normalization** (role-normalized field):
     - Use SHORT FORMS and abbreviations for common roles
     - Use proper casing: abbreviations in UPPERCASE (SDE, SSE, MLE, SRE, SMTS, MTS), full role titles in Title Case
     - Examples: "SDE 2", "SDE-2", "SDE II" → "SDE 2"
     - Examples: "Senior Software Engineer", "SSE" → "SSE"
     - Examples: "Machine Learning Engineer", "ML Engineer" → "MLE"
     - Examples: "Data Scientist", "DS" → "Data Scientist"
     - Examples: "DevOps Engineer" → "DevOps Engineer"
     - Examples: "SRE Engineer", "Site Reliability Engineer" → "SRE"
     - Examples: "SMTS", "Smts", "Senior MTS" → "SMTS"
     - Examples: "Backend Engineer" → "Backend Engineer"
     - Keep it short and standardized

7. **Internship specific**:
   - Use <stipend-monthly> for monthly stipend (actual amount, not in lakhs)
   - Example: "₹10,000/month" → <stipend-monthly>10000</stipend-monthly>
   - Don't include <total> or <total-calculated> for internships

8. **Foreign currency offers (Remote from India)**:
   - Include <remote-from-india>true</remote-from-india>
   - Keep original currency amount and specify currency (EUR, USD, etc.)
   - Example: "68K Euro" → <base>68000</base><currency>EUR</currency>

9. **Multiple offers in one post**:
   - Create separate complete XML blocks for each offer

10. **Missing information**:
   - Skip fields that are not mentioned (don't use n/a, N/A, "Not Mentioned", or empty tags)
   - NEVER output placeholder values like "Not Mentioned", "Unknown", "N/A" - simply omit the field entirely

11. **Current vs New offer**:
   - Only extract the NEW offer being discussed
   - Ignore mentions of "current company" or "prior compensation"

## Output Format
For each offer, output XML in this structure:

```xml
<compensation-post>true</compensation-post>
<offer-type>full-time</offer-type>
<company>Company Name</company>
<company-normalized>company name</company-normalized>
<role>Job Title</role>
<role-normalized>job title short form</role-normalized>
<yoe>4.5</yoe>
<base>49</base>
<total>62</total>
<location>Bangalore</location>
<currency>INR</currency>
```

Note: Use <total> when explicitly mentioned, or <total-calculated> when you need to calculate from components.

## Examples

### Example 1: Standard India Full-Time Offer
Input:
Title: SDE 2 | Arrise : Pragmatic Play
Content: YOE : 4.5 (Includes 6 months internship)
Current Company : SDE 1 at Amazon
Current Compensation : 35 lakhs (including esops)
Arrise Offer : After 2nd Negotiation
Base Offered : 49 lakhs with retirals
Variable ~ 5 lakhs
Joining Bonus = 10 lakhs (8 lakhs 1st year + 2 lakhs second year)
Total Comp = 62 lakhs
Location: Bangalore

Output:
```xml
<compensation-post>true</compensation-post>
<offer-type>full-time</offer-type>
<company>Arrise</company>
<company-normalized>arrise</company-normalized>
<role>SDE 2</role>
<role-normalized>SDE 2</role-normalized>
<yoe>4.5</yoe>
<base>49</base>
<total>62</total>
<location>Bangalore</location>
<currency>INR</currency>
```

### Example 2: Multiple Offers in One Post
Input:
Title: DevOps Offers || DocuSign, Europe based online casino, Data ETL company
Content: Years of Experience: 4.5 years
Prior Compansation: ~45LPA

Company: DocuSign
Title: SRE Engineer
Location: Bangalore, India (Hybrid)
Salary/Base: 45L
Annual Bonus: 15% of base
Joining Bonus: 10 Lakhs

Company: Europe based online casino
Title: Senior DevOps Engineer
Location: Remote from India
Salary: 68K Euro (all base)

Company: Data ETL Company
Title: Senior Infrastructure Engineer
Location : Remote from India
Salary: 58 Lakhs base
Annual Bonus: 10% to 20% of base
ESOPs: 55000 USD (vested equally over 4 years)
Total: ~88 LPA

Output:
```xml
<compensation-post>true</compensation-post>
<offer-type>full-time</offer-type>
<company>DocuSign</company>
<company-normalized>docusign</company-normalized>
<role>SRE Engineer</role>
<role-normalized>SRE</role-normalized>
<yoe>4.5</yoe>
<base>45</base>
<total-calculated>61.75</total-calculated>
<location>Bangalore</location>
<currency>INR</currency>
```

Note: Used total-calculated since user didn't mention explicit total. Calculated as 45 (base) + 6.75 (15% bonus) + 10 (joining bonus) = 61.75

```xml
<compensation-post>true</compensation-post>
<offer-type>full-time</offer-type>
<company>Europe based online casino</company>
<company-normalized>europe based online casino</company-normalized>
<role>Senior DevOps Engineer</role>
<role-normalized>Senior DevOps Engineer</role-normalized>
<yoe>4.5</yoe>
<base>68000</base>
<total>68000</total>
<location>Remote</location>
<remote-from-india>true</remote-from-india>
<currency>EUR</currency>
```

```xml
<compensation-post>true</compensation-post>
<offer-type>full-time</offer-type>
<company>Data ETL Company</company>
<company-normalized>data etl company</company-normalized>
<role>Senior Infrastructure Engineer</role>
<role-normalized>Senior Infrastructure Engineer</role-normalized>
<yoe>4.5</yoe>
<base>58</base>
<total>88</total>
<location>Remote</location>
<currency>INR</currency>
```

### Example 3: Internship
Input:
Title: Python Developer Intern
Content: Is a ₹10k Python Developer Internship with 1-Year Commitment Worth It?
I recently discussed compensation with HR for a Python Developer Intern role.
Offer details: ₹10,000/month, Commitment: 1 year

Output:
```xml
<compensation-post>true</compensation-post>
<offer-type>internship</offer-type>
<role>Python Developer Intern</role>
<role-normalized>Python Developer Intern</role-normalized>
<yoe>0</yoe>
<stipend-monthly>10000</stipend-monthly>
<currency>INR</currency>
```

### Example 4: Non-Compensation Post (Problem Sets)
Input:
Title: TOP-20 GREEDY PROBLEMS (pattern-wise)
Content: TOP-20 GREEDY PROBLEMS (pattern-wise)
1️⃣ Sorting + Local Choice (Foundation)
Pattern: Sort → pick locally optimal → never reconsider
1. 455 – Assign Cookies
2. 860 – Lemonade Change...

Output:
```xml
<compensation-post>false</compensation-post>
<reason>not-about-job-offer</reason>
```

### Example 5: Remote India Offer (Lacs = India)
Input:
Title: Trilogy Innovations (CodeNation) | SDE - 1 | Remote
Content: Education: B.Tech CSE - IIIT
Years of Experience: 0 (excluding internships)
Company: Trilogy Innovations
Role/Level: SDE-1
Location: Remote
Application - Campus hiring
Date of the Offer: July 2025
Base Salary: 30 lacs
Annual Bonus: 2.5 lacs
Total compensation: 32.5 lacs

Output:
```xml
<compensation-post>true</compensation-post>
<offer-type>full-time</offer-type>
<company>Trilogy Innovations</company>
<company-normalized>trilogy innovations</company-normalized>
<role>SDE-1</role>
<role-normalized>SDE 1</role-normalized>
<yoe>0</yoe>
<base>30</base>
<total>32.5</total>
<location>Remote</location>
<currency>INR</currency>
```

### Example 6: Non-India Offer (Should Skip)
Input:
Title: Google US Offer
Content: Got an offer from Google Mountain View
Base: $200K, Total: $350K, Location: Mountain View, California

Output:
```xml
<compensation-post>false</compensation-post>
<reason>non-india-offer</reason>
```

### Example 7: Partial Information (Only Base Mentioned)
Input:
Title: Freshworks Senior Software Engineer
Content: YOE: 4.5 years, Backend Java, Bangalore
Current CTC: ~12 LPA
Freshworks HR mentioned they can match or offer more.
Looking for 28 LPA base, Bangalore Hybrid

Output:
```xml
<compensation-post>false</compensation-post>
<reason>no-offer-details</reason>
```

### Example 8: Machine Learning Engineer with Company Normalization
Input:
Title: Samsung R&D Offer - ML Engineer
Content: Got an offer from Samsung R&D Bangalore!
YOE: 3 years
Role: Machine Learning Engineer
Base: 35 LPA
Stocks: 8 LPA over 4 years
Total: 43 LPA
Location: Bangalore

Output:
```xml
<compensation-post>true</compensation-post>
<offer-type>full-time</offer-type>
<company>Samsung R&D</company>
<company-normalized>samsung</company-normalized>
<role>Machine Learning Engineer</role>
<role-normalized>MLE</role-normalized>
<yoe>3</yoe>
<base>35</base>
<total>43</total>
<location>Bangalore</location>
<currency>INR</currency>
```

## Post to Parse

{content}

## Output
Provide ONLY the XML output, nothing else. If there are multiple offers, provide multiple complete XML blocks."""


COMPANY_RULES = """## Company Normalization Rules

1. **CRITICAL**: Only group companies you are CERTAIN are the same entity. When in doubt, keep them separate.
2. **CRITICAL - PROPER CASING**: Use the official/proper casing for company names:
   - Well-known companies: Use their official brand casing (e.g., "Google", "Amazon", "LinkedIn", "PayPal", "GitHub")
   - Acronyms: UPPERCASE (e.g., "IBM", "AMD", "NVIDIA", "HSBC", "SAP")
   - CamelCase brands: Preserve their styling (e.g., "PhonePe", "MakeMyTrip", "BigBasket", "InMobi", "DocuSign")
   - Standard companies: Title Case (e.g., "Goldman Sachs", "Morgan Stanley", "Arctic Wolf", "Safe Security")
   - NEVER use all lowercase for canonical company names
3. **PRESERVE formatting**: Use the exact spelling and punctuation from the official form
4. **DO NOT introduce typos** or change spellings arbitrarily
5. **Map subsidiaries/regional variants to parent company**:
   - Examples: "amazon india" → "Amazon", "uber india" → "Uber", "walmart global tech" → "Walmart"
   - Pattern: "[Company] india", "[Company] global tech", "[Company] on campus" → always map to parent [Company]
6. **Map different spellings/formats to standard form**:
   - Examples: "goldman_sachs", "goldmansachs" → "Goldman Sachs"
7. **Map abbreviations to full names when clear and well-known**:
   - Examples: "jpmc", "jpmorgan" → "JPMorgan Chase" (common abbreviation)
8. **Map divisions to parent company when appropriate**:
   - Examples: "oracle cerner", "oracle health", "oracle oci" → "Oracle"
   - Pattern: "[Company] [division/product]" → map to parent [Company] when division name is clearly a product/service
9. **Use the most recognizable/official form as canonical**
10. **DO NOT merge**: Companies with similar names that are different entities (e.g., "makemytrip" and "m2p" are completely different companies)"""

ROLE_RULES = """## Role Normalization Rules

1. **CRITICAL**: Keep different role LEVELS separate (e.g., "SDE 1", "SDE 2", "SDE 3" are different roles)
2. **CRITICAL**: ALWAYS preserve level information. "software engineer 2" has level 2, keep it!
3. **CRITICAL**: ALWAYS normalize roman numerals to numbers (i→1, ii→2, iii→3, iv→4)
4. **CRITICAL**: Keep intern levels separate from full-time (e.g., "Full Stack Intern" ≠ "Full Stack Developer")
5. **CRITICAL - PROPER CASING**:
   - Abbreviations: UPPERCASE (SDE, SSE, MLE, SRE, SMTS, MTS, IC2, L60, VP, PMTS, LMTS, AMTS)
   - Full role titles: Title Case (Senior Data Engineer, Data Scientist, Backend Engineer, Lead Developer, Principal Software Engineer)
   - Examples: "senior data engineer" → "Senior Data Engineer", "backend engineer" → "Backend Engineer", "sde 2" → "SDE 2"

6. **Common SDE/SWE abbreviation mappings** (treat as same role):
   - "sde", "swe", "se", "software engineer", "software developer" → all map to "SDE"
   - WITH LEVELS: "sde 2", "swe 2", "se 2", "software engineer 2" → "SDE 2"
   - "sdet" (test engineer) also maps to "SDE": "sdet" → "SDE", **"sdet 2" → "SDE 2"** (PRESERVE LEVEL!)
   - WITH SPECIALIZATIONS: "software engineer backend", "software engineer android" → "SDE" (remove specialization)

7. **Senior Software Engineer abbreviations**:
   - "sse", "senior software engineer", "senior software developer", "senior sde", "senior engineer" → "SSE"
   - "senior engineer" is considered equivalent to "senior software engineer" (too similar to keep separate)
   - These are specifically for SOFTWARE ENGINEERING roles
   - DO NOT collapse other "senior X" roles (with specific specializations) to "SSE"

7. **Senior roles in OTHER specializations stay separate**:
   - "senior data engineer" stays as "Senior Data Engineer" (NOT "senior" or "SSE")
   - "senior backend engineer" stays as "Senior Backend Engineer"
   - "senior platform engineer" stays as "Senior Platform Engineer"
   - Only map to abbreviated form if the full role title matches

8. **Normalize level format consistently**:
   - **CRITICAL**: ALWAYS preserve level numbers for ALL roles
   - Use numbers not roman numerals: "ii" → "2", "iii" → "3", "iv" → "4"
   - Examples: "mts ii" → "MTS 2", "mle ii" → "MLE 2", "ml scientist iii" → "ML Scientist 3"
   - Examples: "sre 2" → "SRE 2" (NOT just "SRE"), "data engineer ii" → "Data Engineer 2"
   - Examples: "smts" → "SMTS", "smts ii" → "SMTS 2"
   - Remove spaces from company-specific levels: keep "ic3" as "IC3", not "ic 3"
   - Remove suffixes like "role": "l60 role" → "L60"

9. **Specializations are SEPARATE roles**:
   - "backend engineer", "frontend engineer", "data engineer" are different from "SDE"
   - Keep "Backend Engineer", "Frontend Developer", "Data Engineer" as separate role families (use Title Case)
   - BUT: "sde 2 backend" should map to "SDE 2" (remove specialization suffix from sde/swe)

10. **Fix common typos**:
    - "principle software engineer" → "Principal Software Engineer" (principle is misspelled)

11. **Filter out non-roles**: Skip entries that aren't job titles:
    - Don't include: "offer", "microsoft offer", "full-time", "unknown"
    - Don't include standalone qualifiers: "senior", "intern" (without specific role)"""

LOCATION_RULES = """## Location Normalization Rules

1. **Map city variations to standard/official name**:
   - Examples: "bangalore", "bengaluru", "blr" → "bengaluru"
   - Examples: "gurgaon", "gurugram" → "gurugram"
2. **Use official or most commonly accepted spelling**
3. **Map remote variations**:
   - Examples: "remote", "wfh" → "remote"
4. **Keep distinct locations separate**:
   - "delhi" and "noida" are different locations, keep separate"""

COMPANY_EXAMPLES = """## Examples

### Example 1: Regional Variants to Parent Company (Proper Casing)
Input:
```
'amazon [139]', 'amazon india [2]'
'uber [38]', 'uber india [2]'
```

Output:
```
amazon|amazon india:Amazon
uber|uber india:Uber
```

### Example 2: Multiple Companies with Variations (Proper Casing)
Input:
```
'goldman sachs [46]', 'goldman_sachs [2]', 'goldmansachs [2]'
'google [59]'
'linkedin [23]', 'linked in [2]'
```

Output:
```
goldman sachs|goldman_sachs|goldmansachs:Goldman Sachs
google:Google
linkedin|linked in:LinkedIn
```

### Example 3: Parent Company Mapping (Divisions/Subsidiaries)
Input:
```
'oracle [58]', 'oracle cerner [11]', 'oracle health [9]', 'oracle oci [4]', 'oracle non oci [2]'
'walmart [70]', 'walmart global tech [9]'
'zeta [18]', 'zeta directi [2]'
```

Output:
```
oracle|oracle cerner|oracle health|oracle oci|oracle non oci:Oracle
walmart|walmart global tech:Walmart
zeta|zeta directi:Zeta
```

### Example 4: Abbreviations to Full Names
Input:
```
'jpmc [18]', 'jpmorgan [5]', 'jpmorgan chase [3]', 'jp morgan [5]', 'jp morgan chase [6]'
```

Output:
```
jpmc|jpmorgan|jpmorgan chase|jp morgan|jp morgan chase:JPMorgan Chase
```

### Example 5: Standalone Companies (Proper Casing)
Input:
```
'flipkart [33]'
'adobe [23]'
'arctic wolf [5]'
'bloomreach [3]'
```

Output:
```
flipkart:Flipkart
adobe:Adobe
arctic wolf:Arctic Wolf
bloomreach:Bloomreach
```

### Example 6: CamelCase and Special Casing
Input:
```
'phonepe [12]'
'makemytrip [8]', 'mmt [3]'
'bigbasket [5]'
'docusign [7]'
```

Output:
```
phonepe:PhonePe
makemytrip|mmt:MakeMyTrip
bigbasket:BigBasket
docusign:DocuSign
```

### Example 7: Acronyms (UPPERCASE)
Input:
```
'ibm [15]', 'ibm consulting [3]'
'amd [8]'
'nvidia [20]'
'hsbc [12]'
```

Output:
```
ibm|ibm consulting:IBM
amd:AMD
nvidia:NVIDIA
hsbc:HSBC
```

### Example 8: Preserve Formatting and Special Characters
Input:
```
'super.money [2]'
'startup [7]', 'startup1 [2]'
```

Output:
```
super.money:Super.money
startup|startup1:Startup
```

### Example 9: ❌ WRONG - DO NOT DO THIS
Input:
```
'makemytrip [5]', 'm2p [2]'
```

❌ WRONG Output (these are DIFFERENT companies):
```
makemytrip|m2p:MakeMyTrip
```

✓ CORRECT Output:
```
makemytrip:MakeMyTrip
m2p:M2P
```

Note: MakeMyTrip is a travel booking company. M2P is a fintech company. Do not merge them!

### Example 10: ❌ WRONG - Never use lowercase for canonical names
Input:
```
'connectwise [4]'
'licious [3]'
```

❌ WRONG Output:
```
connectwise:connectwise
licious:licious
```

✓ CORRECT Output:
```
connectwise:ConnectWise
licious:Licious
```"""

ROLE_EXAMPLES = """## Examples

### Example 1: SDE/SWE Equivalence with Levels
Input:
```
'sde 2 [377]', 'sde-2 [15]', 'sde ii [21]', 'swe 2 [20]', 'software engineer 2 [9]', 'software engineer ii [9]'
```

Output:
```
sde 2|sde-2|sde ii|swe 2|software engineer 2|software engineer ii:SDE 2
```

### Example 2: SDE/SWE/SDET without Levels
Input:
```
'sde [34]', 'swe [10]', 'se [5]', 'sdet [8]', 'software engineer [89]', 'software developer [13]'
'software engineer backend [5]', 'software engineer android [3]'
```

Output:
```
sde|swe|se|sdet|software engineer|software developer|software engineer backend|software engineer android:SDE
```

Note: SDET and specialization variants (backend, android) also map to SDE

### Example 3: Multiple SDE Levels (Keep Separate!)
Input:
```
'sde 1 [172]', 'sde-1 [10]', 'sde i [5]', 'software engineer 1 [8]'
'sde 3 [84]', 'sde-3 [8]', 'sde iii [4]', 'swe 3 [20]'
'sdet [8]'
'sdet 2 [15]'
```

Output:
```
sde 1|sde-1|sde i|software engineer 1:SDE 1
sde 3|sde-3|sde iii|swe 3:SDE 3
sdet:SDE
sdet 2:SDE 2
```

Note: Standalone "sdet" maps to "SDE" (no level). "sdet 2" preserves level and maps to "SDE 2"

### Example 4: Senior Software Engineer (SSE)
Input:
```
'sse [150]', 'senior software engineer [36]', 'senior software developer [10]', 'senior sde [5]', 'senior engineer [15]'
```

Output:
```
sse|senior software engineer|senior software developer|senior sde|senior engineer:SSE
```

Note: "senior engineer" is considered equivalent to "senior software engineer" (too similar to keep separate)

### Example 4b: Senior Roles in Other Specializations (Keep Separate!)
Input:
```
'senior data engineer [12]'
'senior backend engineer [8]'
'senior platform engineer [6]'
```

Output:
```
senior data engineer:Senior Data Engineer
senior backend engineer:Senior Backend Engineer
senior platform engineer:Senior Platform Engineer
```

Note: Do NOT collapse all "senior X" roles to just "senior" or "SSE". Keep them as distinct roles! Use Title Case for full role names.

### Example 5: Specializations are Separate Roles
Input:
```
'backend engineer [12]', 'backend developer [5]', 'backend [3]'
'frontend developer [8]', 'frontend [4]'
'data engineer [10]', 'data engineer ii [5]'
'data scientist [15]', 'ds [8]'
```

Output:
```
backend engineer|backend developer|backend:Backend Engineer
frontend developer|frontend:Frontend Developer
data engineer:Data Engineer
data engineer ii:Data Engineer 2
data scientist|ds:Data Scientist
```

### Example 6: Remove Specialization Suffixes from SDE
Input:
```
'sde 2 [150]', 'sde 2 backend [5]', 'sde 2 frontend [3]', 'sde 2 data engineer [2]'
```

Output:
```
sde 2|sde 2 backend|sde 2 frontend|sde 2 data engineer:SDE 2
```

### Example 7: MTS/MLE/SRE/SMTS Levels with Roman Numeral Normalization
Input:
```
'mts [25]', 'mts 2 [12]', 'mts ii [3]', 'mts 3 [10]', 'mts3 [2]'
'smts [15]', 'senior mts [8]'
'smts ii [5]', 'smts 2 [3]'
'mle [8]', 'mle ii [5]'
'ml scientist iii [4]', 'machine learning scientist 3 [2]'
'sre [10]', 'sre 2 [5]'
```

Output:
```
mts:MTS
mts 2|mts ii:MTS 2
mts 3|mts3:MTS 3
smts|senior mts:SMTS
smts ii|smts 2:SMTS 2
mle:MLE
mle ii:MLE 2
ml scientist iii|machine learning scientist 3:ML Scientist 3
sre:SRE
sre 2:SRE 2
```

Note: ALWAYS normalize roman numerals (ii→2, iii→3) and ALWAYS preserve level numbers. Use UPPERCASE for abbreviations, Title Case for full role names.

### Example 8: Company-Specific Levels (Preserve Format, Remove Suffixes)
Input:
```
'l3 [10]', 'l4 [17]', 'l60 [8]', 'l60 role [2]', 'l61 [10]'
'ic 2 [2]', 'ic2 [8]', 'ic3 [10]', 'ic4 [5]'
```

Output:
```
l3:L3
l4:L4
l60|l60 role:L60
l61:L61
ic 2|ic2:IC2
ic3:IC3
ic4:IC4
```

Note: Remove suffixes like "role". Normalize to no-space format for IC levels (IC2 not "IC 2"). Use UPPERCASE for company-specific levels.

### Example 9: Intern Roles (Keep Separate from Full-Time)
Input:
```
'sde intern [15]', 'swe intern [5]', 'software engineer intern [3]'
'full stack intern [6]'
'full stack [8]', 'full stack engineer [10]', 'full stack developer [5]'
```

Output:
```
sde intern|swe intern|software engineer intern:SDE Intern
full stack intern:Full Stack Intern
full stack|full stack engineer|full stack developer:Full Stack Developer
```

Note: Intern roles are SEPARATE from their full-time equivalents! Use UPPERCASE for abbreviations, Title Case for full role names.

### Example 10: Typo Fixes
Input:
```
'principal software engineer [10]', 'principle software engineer [3]'
'staff software engineer [8]', 'staff engineer [5]'
'lead developer [6]', 'lead dev [3]'
```

Output:
```
principal software engineer|principle software engineer:Principal Software Engineer
staff software engineer|staff engineer:Staff Engineer
lead developer|lead dev:Lead Developer
```

Note: Fix typos like "principle" → "principal". Use Title Case for full role names.

### Example 11: Filter Out Non-Roles
Input:
```
'sde 1 [100]'
'offer [50]'
'microsoft offer [10]'
'full-time [30]'
'unknown [20]'
'senior [5]'
'intern [8]'
```

Output:
```
sde 1:SDE 1
```

Note: Skip these non-roles: "offer", "microsoft offer", "full-time", "unknown", "senior", "intern" (standalone qualifiers without specific roles). Use UPPERCASE for abbreviations."""

LOCATION_EXAMPLES = """## Examples

### Example 1: City Name Variations
Input:
```
'Bangalore [594]', 'Bengaluru [181]', 'BLR [2]'
```

Output:
```
Bangalore|Bengaluru|BLR:Bengaluru
```

### Example 2: Multiple Cities
Input:
```
'Gurgaon [47]', 'Gurugram [38]'
'Hyderabad [171]', 'Hyd [4]'
```

Output:
```
Gurgaon|Gurugram:Gurugram
Hyderabad|Hyd:Hyderabad
```

### Example 3: Remote/Hybrid Variations
Input:
```
'Remote [107]', 'WFH [1]'
'Hybrid [3]'
```

Output:
```
Remote|WFH:Remote
Hybrid:Hybrid
```

### Example 4: Standard City Names (No Variations)
Input:
```
'Pune [60]'
'Chennai [41]'
'Mumbai [35]'
```

Output:
```
Pune:Pune
Chennai:Chennai
Mumbai:Mumbai
```

### Example 5: Regional Variations
Input:
```
'Delhi [8]', 'Noida [48]'
'India [7]', 'Pan India [2]'
```

Output:
```
Delhi:Delhi
Noida:Noida
India|Pan India:India
```"""

NORMALIZATION_MAPPING_PROMPT = """You are a {entity_type} normalization specialist tasked with creating canonical mappings for {entity_type} variations.

## Task
Analyze the list of {entity_type} variations and create normalized mappings by grouping similar variations together and selecting the most appropriate canonical form.

## Input Format
Each line contains a comma-separated list of {entity_type} variations with their occurrence counts in brackets.
Example: 'amazon [139]', 'amazon india [2]'

{rules}

## Output Format
Return ONLY the mappings, one per line, in this format:
```
variation1|variation2|variation3:canonical_name
```

**Requirements:**
- Group ALL variations that map to the same canonical name on a single line
- Separate variations with pipe character (|)
- Use colon (:) before the canonical name
- **CRITICAL - PROPER CASING FOR ROLES**:
  - Abbreviations: UPPERCASE (SDE, SSE, MLE, SRE, SMTS, MTS, IC2, L60, VP, PMTS, LMTS, AMTS)
  - Full role titles: Title Case (Senior Data Engineer, Data Scientist, Backend Engineer, Lead Developer, Principal Software Engineer)
  - Examples: "senior data engineer" → "Senior Data Engineer", "backend engineer" → "Backend Engineer", "sde 2" → "SDE 2"
- **CRITICAL - PROPER CASING FOR COMPANIES**:
  - Well-known companies: Use official brand casing (e.g., "Google", "Amazon", "LinkedIn", "PayPal")
  - Acronyms: UPPERCASE (e.g., "IBM", "AMD", "NVIDIA", "HSBC")
  - CamelCase brands: Preserve styling (e.g., "PhonePe", "MakeMyTrip", "BigBasket", "DocuSign")
  - Standard companies: Title Case (e.g., "Goldman Sachs", "Arctic Wolf", "Safe Security")
  - NEVER use all lowercase for canonical company names
- **PRESERVE exact spelling** - do not introduce typos or arbitrary changes
- **PRESERVE formatting** - keep dots, spaces, hyphens as they appear in the original
- Do not include explanations, headers, counts, or any additional text
- Output only the mappings
- **Accuracy is critical** - when uncertain if two names are the same company, keep them separate

{examples}

## Entity Type
{entity_type}

## Data to Normalize

{grouped_data}

## Output
Provide ONLY the mappings in the specified format, nothing else.
Don't put the output inside backticks ``` or any other wrapper, just pure text please.
"""


NORMALIZATION_WITH_CONTEXT_PROMPT = """You are a {entity_type} normalization specialist tasked with creating canonical mappings for NEW {entity_type} variations.

## Task
Analyze the NEW {entity_type} variations and create normalized mappings. Use the existing mappings as reference for consistent naming conventions.

## Input Format
Each line contains a comma-separated list of {entity_type} variations with their occurrence counts in brackets.
Example: 'amazon [139]', 'amazon india [2]'

{rules}

## Output Format
Return ONLY the mappings for NEW entities, one per line, in this format:
```
variation1|variation2|variation3:canonical_name
```

**Requirements:**
- Group ALL variations that map to the same canonical name on a single line
- Separate variations with pipe character (|)
- Use colon (:) before the canonical name
- **CRITICAL - PROPER CASING FOR ROLES**:
  - Abbreviations: UPPERCASE (SDE, SSE, MLE, SRE, SMTS, MTS, IC2, L60, VP, PMTS, LMTS, AMTS)
  - Full role titles: Title Case (Senior Data Engineer, Data Scientist, Backend Engineer, Lead Developer)
- **CRITICAL - PROPER CASING FOR COMPANIES**:
  - Well-known companies: Use official brand casing (e.g., "Google", "Amazon", "LinkedIn", "PayPal")
  - Acronyms: UPPERCASE (e.g., "IBM", "AMD", "NVIDIA", "HSBC")
  - CamelCase brands: Preserve styling (e.g., "PhonePe", "MakeMyTrip", "BigBasket", "DocuSign")
  - Standard companies: Title Case (e.g., "Goldman Sachs", "Arctic Wolf", "Safe Security")
  - NEVER use all lowercase for canonical company names
- **PRESERVE exact spelling** - do not introduce typos or arbitrary changes
- **PRESERVE formatting** - keep dots, spaces, hyphens as they appear in the original
- Do not include explanations, headers, counts, or any additional text
- Output only the mappings for NEW entities
- **Accuracy is critical** - when uncertain if two names are the same entity, keep them separate
- **Use existing mappings as reference** - if a new entity is a variation of an existing one, map it to the same canonical name

{examples}

## Entity Type
{entity_type}

## Existing Mappings (for reference - DO NOT include these in output)
{context}

## NEW Data to Normalize

{grouped_data}

## Output
Provide ONLY the mappings for NEW entities in the specified format, nothing else.
Don't put the output inside backticks ``` or any other wrapper, just pure text please.
"""


def get_normalization_prompt(entity_type: NormalizedEntity, grouped_data: str) -> str:
    rules_map: dict[NormalizedEntity, str] = {
        NormalizedEntity.COMPANY: COMPANY_RULES,
        NormalizedEntity.ROLE: ROLE_RULES,
        NormalizedEntity.LOCATION: LOCATION_RULES,
    }

    examples_map: dict[NormalizedEntity, str] = {
        NormalizedEntity.COMPANY: COMPANY_EXAMPLES,
        NormalizedEntity.ROLE: ROLE_EXAMPLES,
        NormalizedEntity.LOCATION: LOCATION_EXAMPLES,
    }

    rules = rules_map.get(entity_type, COMPANY_RULES)
    examples = examples_map.get(entity_type, COMPANY_EXAMPLES)

    return NORMALIZATION_MAPPING_PROMPT.format(
        entity_type=entity_type, rules=rules, examples=examples, grouped_data=grouped_data
    )


def get_normalization_prompt_with_context(
    entity_type: NormalizedEntity, grouped_data: str, context: str
) -> str:
    rules_map: dict[NormalizedEntity, str] = {
        NormalizedEntity.COMPANY: COMPANY_RULES,
        NormalizedEntity.ROLE: ROLE_RULES,
        NormalizedEntity.LOCATION: LOCATION_RULES,
    }

    examples_map: dict[NormalizedEntity, str] = {
        NormalizedEntity.COMPANY: COMPANY_EXAMPLES,
        NormalizedEntity.ROLE: ROLE_EXAMPLES,
        NormalizedEntity.LOCATION: LOCATION_EXAMPLES,
    }

    rules = rules_map.get(entity_type, COMPANY_RULES)
    examples = examples_map.get(entity_type, COMPANY_EXAMPLES)

    if not context:
        return NORMALIZATION_MAPPING_PROMPT.format(
            entity_type=entity_type,
            rules=rules,
            examples=examples,
            grouped_data=grouped_data,
        )

    return NORMALIZATION_WITH_CONTEXT_PROMPT.format(
        entity_type=entity_type,
        rules=rules,
        examples=examples,
        context=context,
        grouped_data=grouped_data,
    )

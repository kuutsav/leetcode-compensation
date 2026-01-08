from leetcomp.parse import parse_xml_to_json, should_parse_post, _parse_xml_block


def test_parse_xml_to_json_single_offer_basic():
    """Test parsing a single basic offer"""
    xml_output = """```xml
<compensation-post>true</compensation-post>
<offer-type>full-time</offer-type>
<company>Arrise</company>
<company-normalized>arrise</company-normalized>
<role>SDE 2</role>
<role-normalized>sde 2</role-normalized>
<yoe>4.5</yoe>
<base>49</base>
<total>62</total>
<currency>INR</currency>
```"""

    result = parse_xml_to_json(xml_output)

    assert len(result) == 1
    assert result[0]["compensation-post"] is True
    assert result[0]["offer-type"] == "full-time"
    assert result[0]["company"] == "Arrise"
    assert result[0]["company-normalized"] == "arrise"
    assert result[0]["role"] == "SDE 2"
    assert result[0]["role-normalized"] == "sde 2"
    assert result[0]["yoe"] == 4.5
    assert result[0]["base"] == 49
    assert result[0]["total"] == 62
    assert result[0]["currency"] == "INR"


def test_parse_xml_to_json_multiple_offers():
    """Test parsing multiple offers in one response"""
    xml_output = """```xml
<compensation-post>true</compensation-post>
<offer-type>full-time</offer-type>
<company>DocuSign</company>
<company-normalized>docusign</company-normalized>
<role>SRE Engineer</role>
<role-normalized>sre</role-normalized>
<yoe>4.5</yoe>
<base>45</base>
<location>Bangalore</location>
<currency>INR</currency>
```

```xml
<compensation-post>true</compensation-post>
<offer-type>full-time</offer-type>
<company>Europe based online casino</company>
<company-normalized>europe based online casino</company-normalized>
<role>Senior DevOps Engineer</role>
<role-normalized>senior devops engineer</role-normalized>
<yoe>4.5</yoe>
<base>68000</base>
<total>68000</total>
<location>Remote</location>
<remote-from-india>true</remote-from-india>
<currency>EUR</currency>
```"""

    result = parse_xml_to_json(xml_output)

    assert len(result) == 2
    assert result[0]["company"] == "DocuSign"
    assert result[0]["location"] == "Bangalore"
    assert result[1]["company"] == "Europe based online casino"
    assert result[1]["remote-from-india"] is True
    assert result[1]["currency"] == "EUR"


def test_parse_xml_to_json_not_compensation_post():
    """Test parsing when compensation-post is false"""
    xml_output = """```xml
<compensation-post>false</compensation-post>
<reason>not-about-job-offer</reason>
```"""

    result = parse_xml_to_json(xml_output)

    assert len(result) == 1
    assert result[0]["compensation-post"] is False
    assert result[0]["reason"] == "not-about-job-offer"


def test_parse_xml_to_json_numeric_fields_with_decimals():
    """Test that numeric fields with decimals are parsed as floats"""
    xml_output = """```xml
<compensation-post>true</compensation-post>
<yoe>4.5</yoe>
<base>49.5</base>
<total>62.75</total>
```"""

    result = parse_xml_to_json(xml_output)

    assert len(result) == 1
    assert result[0]["yoe"] == 4.5
    assert result[0]["base"] == 49.5
    assert result[0]["total"] == 62.75


def test_parse_xml_to_json_numeric_fields_without_decimals():
    """Test that numeric fields without decimals are parsed as ints"""
    xml_output = """```xml
<compensation-post>true</compensation-post>
<yoe>4</yoe>
<base>49</base>
<total>62</total>
```"""

    result = parse_xml_to_json(xml_output)

    assert len(result) == 1
    assert result[0]["yoe"] == 4
    assert result[0]["base"] == 49
    assert result[0]["total"] == 62


def test_parse_xml_to_json_stipend_monthly_field():
    """Test that stipend-monthly is parsed as numeric"""
    xml_output = """```xml
<compensation-post>true</compensation-post>
<offer-type>internship</offer-type>
<stipend-monthly>50000</stipend-monthly>
```"""

    result = parse_xml_to_json(xml_output)

    assert len(result) == 1
    assert result[0]["stipend-monthly"] == 50000


def test_parse_xml_to_json_remote_from_india_boolean():
    """Test that remote-from-india is parsed as boolean"""
    xml_output = """```xml
<compensation-post>true</compensation-post>
<remote-from-india>true</remote-from-india>
```"""

    result = parse_xml_to_json(xml_output)

    assert len(result) == 1
    assert result[0]["remote-from-india"] is True


def test_parse_xml_to_json_xml_without_code_blocks():
    """Test parsing XML not wrapped in code blocks"""
    xml_output = """<compensation-post>true</compensation-post>
<company>TestCo</company>
<role>Engineer</role>"""

    result = parse_xml_to_json(xml_output)

    assert len(result) == 1
    assert result[0]["compensation-post"] is True
    assert result[0]["company"] == "TestCo"
    assert result[0]["role"] == "Engineer"


def test_parse_xml_to_json_empty_tags_ignored():
    """Test that empty tags are not included in the result"""
    xml_output = """```xml
<compensation-post>true</compensation-post>
<company>TestCo</company>
<location></location>
<role>Engineer</role>
```"""

    result = parse_xml_to_json(xml_output)

    assert len(result) == 1
    assert "location" not in result[0]
    assert result[0]["company"] == "TestCo"


def test_parse_xml_to_json_malformed_xml_skipped():
    """Test that malformed XML blocks are skipped gracefully"""
    xml_output = """```xml
<compensation-post>true</compensation-post>
<company>TestCo
<role>Engineer</role>
```"""

    # Should not raise an exception, just return empty or skip
    result = parse_xml_to_json(xml_output)
    # Malformed XML should be skipped
    assert isinstance(result, list)


def test_parse_xml_to_json_invalid_numeric_values():
    """Test that invalid numeric values are kept as strings"""
    xml_output = """```xml
<compensation-post>true</compensation-post>
<yoe>unknown</yoe>
<base>negotiable</base>
```"""

    result = parse_xml_to_json(xml_output)

    assert len(result) == 1
    assert result[0]["yoe"] == "unknown"
    assert result[0]["base"] == "negotiable"


def test_parse_xml_block_direct_xml_parsing():
    """Test the _parse_xml_block function directly"""
    xml_content = """<compensation-post>true</compensation-post>
<company>TestCo</company>
<role>Engineer</role>"""

    result = _parse_xml_block(xml_content)

    assert len(result) == 1
    assert result[0]["compensation-post"] is True
    assert result[0]["company"] == "TestCo"
    assert result[0]["role"] == "Engineer"


def test_parse_xml_block_multiple_blocks_in_one_string():
    """Test parsing multiple compensation-post blocks"""
    xml_content = """<compensation-post>true</compensation-post>
<company>Company1</company>
<role>Role1</role>
<compensation-post>true</compensation-post>
<company>Company2</company>
<role>Role2</role>"""

    result = _parse_xml_block(xml_content)

    assert len(result) == 2
    assert result[0]["company"] == "Company1"
    assert result[1]["company"] == "Company2"


def test_should_parse_post_more_upvotes_than_downvotes():
    """Test that posts with more upvotes than downvotes are parsed"""
    post = {"upvotes": 10, "downvotes": 2}
    assert should_parse_post(post) is True


def test_should_parse_post_equal_votes():
    """Test that posts with equal votes are parsed"""
    post = {"upvotes": 5, "downvotes": 5}
    assert should_parse_post(post) is True


def test_should_parse_post_more_downvotes_than_upvotes():
    """Test that posts with more downvotes are skipped"""
    post = {"upvotes": 2, "downvotes": 10}
    assert should_parse_post(post) is False


def test_should_parse_post_zero_upvotes_one_downvote():
    """Test that posts with 0 upvotes and 1 downvote are skipped"""
    post = {"upvotes": 0, "downvotes": 1}
    assert should_parse_post(post) is False


def test_should_parse_post_zero_votes():
    """Test that posts with no votes are parsed"""
    post = {"upvotes": 0, "downvotes": 0}
    assert should_parse_post(post) is True

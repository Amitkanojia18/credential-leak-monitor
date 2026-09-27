from config.settings import SOURCE_TYPE_WEIGHT


def calculate_score(finding):
    """
    Calculate a severity score based on keywords, emails found,
    and how trustworthy/dangerous the source type is.
    """
    keywords = finding["matched_keywords"]
    emails = finding["emails_found"]
    source_type = finding["source_type"]

    base_score = 0

    # Points per threat keyword matched
    base_score += len(keywords) * 10

    # Extra weight for especially severe keywords
    high_risk_keywords = {"breach", "credential", "password", "dump"}
    for kw in keywords:
        if kw in high_risk_keywords:
            base_score += 10

    # Points for actual emails found (real exposed accounts)
    if emails:
        base_score += 15
    if len(emails) > 1:
        base_score += 10

    # Apply source type multiplier
    weight = SOURCE_TYPE_WEIGHT.get(source_type, 1.0)
    final_score = base_score * weight

    return round(final_score)


def determine_severity(score):
    if score >= 80:
        return "Critical"
    elif score >= 50:
        return "High"
    elif score >= 25:
        return "Medium"
    else:
        return "Low"


def score_finding(finding):
    """Takes a finding dict, adds score + severity, returns updated finding."""
    score = calculate_score(finding)
    severity = determine_severity(score)

    finding["score"] = score
    finding["severity"] = severity

    return finding
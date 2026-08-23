def calculate_risk(test_pass_rate, vulnerabilities, build_time):
    risk_score = (1 - test_pass_rate) * 0.5 + (vulnerabilities * 0.1) + (build_time / 1000)

    if risk_score > 0.7:
        decision = "BLOCK"
    else:
        decision = "DEPLOY"

    return round(risk_score, 2), decision

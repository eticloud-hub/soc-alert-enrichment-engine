import json
from .enrichment import enrich_alert

class AlertScorer:
    """
    Calculates risk scores for alerts based on:
    - IP reputation
    - Alert type severity
    - Geolocation risk
    - Message indicators
    """

    def __init__(self):
        self.high_risk_countries = ["CN", "RU", "KP", "IR"]  # Example high-risk countries
        self.vpn_risk_boost = 15
        self.repeat_offender_boost = 20

    def calculate_risk_score(self, source_ip, destination_ip, alert_type, message, enrichment):
        """
        Calculate overall risk score (0-100)
        """
        score = 0

        # 1. Base alert type severity (weight: 35%)
        alert_severity = enrichment.get("alert_type_severity", 50)
        score += alert_severity * 0.35

        # 2. Source IP reputation (weight: 30%)
        source_rep = enrichment["source_reputation"].get("reputation", 0)
        score += (source_rep / 100) * 30

        # 3. Geolocation risk (weight: 15%)
        source_country = enrichment["source_geo"].get("country", "Unknown")
        if source_country in self.high_risk_countries:
            score += 15
        elif source_country == "Unknown":
            score += 5

        # 4. VPN detection (weight: 10%)
        if enrichment["source_reputation"].get("is_vpn", False):
            score += 10

        # 5. Message indicators (weight: 10%)
        message_risk = self._analyze_message(message)
        score += message_risk * 0.10

        return min(score, 100)  # Cap at 100

    def _analyze_message(self, message):
        """
        Analyze alert message for high-risk keywords
        """
        high_risk_keywords = [
            "ransomware", "exploit", "backdoor", "trojan",
            "credential", "breach", "compromise", "payload"
        ]

        message_lower = message.lower()
        found_keywords = sum(1 for keyword in high_risk_keywords if keyword in message_lower)

        return min(found_keywords * 15, 100)

    def assign_priority(self, risk_score):
        """
        Assign priority level based on risk score
        """
        if risk_score >= 75:
            return "High"
        elif risk_score >= 50:
            return "Medium"
        else:
            return "Low"

def score_alert(alert_id, source_ip, destination_ip, alert_type, message):
    """
    Score a single alert and return risk score + priority
    """
    from .database import update_alert_enrichment

    scorer = AlertScorer()

    # Enrich alert
    enrichment = enrich_alert(source_ip, destination_ip, alert_type, message)

    # Calculate risk score
    risk_score = scorer.calculate_risk_score(
        source_ip, destination_ip, alert_type, message, enrichment
    )

    # Assign priority
    priority = scorer.assign_priority(risk_score)

    # Store enrichment data as JSON
    enrichment_json = json.dumps(enrichment)

    # Update database
    update_alert_enrichment(alert_id, risk_score, priority, enrichment_json)

    return {
        "alert_id": alert_id,
        "risk_score": round(risk_score, 2),
        "priority": priority,
        "enrichment": enrichment
    }

def score_all_alerts(alerts):
    """
    Score all alerts in the database
    """
    results = []
    for alert in alerts:
        result = score_alert(
            alert[0],  # alert_id
            alert[2],  # source_ip
            alert[3],  # destination_ip
            alert[4],  # alert_type
            alert[5]   # message
        )
        results.append(result)

    return results
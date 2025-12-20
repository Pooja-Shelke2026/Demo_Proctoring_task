from collections import defaultdict

EVENT_WEIGHTS = {
    "PHONE": 15,
    "MULTIPLE_PERSON": 20,
    "AUDIO_SPIKE": 5,
    "NO_FACE": 10
}

class RiskEngine:
    def calculate_score(self, events):
        """
        events = list of tuples:
        [(event_type, severity), ...]
        """
        score = 0
        freq = defaultdict(int)

        for event_type, severity in events:
            freq[event_type] += 1

        for event_type, count in freq.items():
            weight = EVENT_WEIGHTS.get(event_type, 0)
            score += weight * count

        return score

    def map_risk_level(self, score):
        if score < 20:
            return "Low"
        elif score <= 50:
            return "Medium"
        else:
            return "High"

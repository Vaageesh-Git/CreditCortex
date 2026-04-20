class HITLRouter:
    def __init__(self):
        self.AUTO_APPROVE_THRESHOLD = 0.02
        self.AUTO_REJECT_THRESHOLD = 0.25

    def determine_routing_action(self, risk_score, rag_output=None, features=None):
        rag_decision = None
        if rag_output:
            rag_decision = str(rag_output.get("final_decision", "")).upper()

        borderline = False
        if features:
            cibil = features.get("cibil_score", 0)
            foir = features.get("foir", 0)
            enquiries = features.get("recent_enquiries_6m", 0)
            bounces = features.get("cheque_bounce_count_6m", 0)

            if foir > 1:
                foir = foir / 100

            borderline = (
                650 <= cibil <= 700 or
                0.45 <= foir <= 0.6 or
                enquiries >= 3 or
                bounces >= 1
            )

        if rag_decision == "REJECT":
            return {
                "status": "REJECTED",
                "assigned_queue": "AUTO_REJECT",
                "reason": "RAG policy decision is reject."
            }

        if rag_decision == "REVIEW" or borderline:
            return {
                "status": "PENDING_REVIEW",
                "assigned_queue": "HUMAN_UNDERWRITER_L1",
                "reason": "ML and/or policy signals indicate borderline risk."
            }

        if rag_decision == "APPROVE" and risk_score < self.AUTO_APPROVE_THRESHOLD:
            return {
                "status": "APPROVED",
                "assigned_queue": "AUTO_APPROVE",
                "reason": f"Low risk ({risk_score*100:.2f}%) and policy aligned."
            }

        if risk_score >= self.AUTO_REJECT_THRESHOLD:
            return {
                "status": "REJECTED",
                "assigned_queue": "AUTO_REJECT",
                "reason": f"High ML risk ({risk_score*100:.2f}%)."
            }

        return {
            "status": "PENDING_REVIEW",
            "assigned_queue": "HUMAN_UNDERWRITER_L1",
            "reason": "Mixed ML and policy signals."
        }
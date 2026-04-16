class HITLRouter:
    def __init__(self):
        print("Initializing Human-in-the-Loop Governance Matrix...")
        
        self.AUTO_APPROVE_THRESHOLD = 0.15
        self.AUTO_REJECT_THRESHOLD = 0.40

    def determine_routing_action(self, risk_score: float, orchestrator_memo: str) -> dict:

        memo_upper = orchestrator_memo.upper()

        if "RECOMMENDED THAT THE LOAN APPLICATION BE REJECTED" in memo_upper:
            return {
                "status": "REJECTED",
                "assigned_queue": "AUTO_REJECT",
                "reason": "Policy violations detected (DTI, FICO, delinquencies)."
            }

        if "MANUAL REVIEW REQUIRED" in memo_upper or "POLICY CONFLICT DETECTED" in memo_upper:
            return {
                "status": "PAUSED",
                "assigned_queue": "HUMAN_UNDERWRITER_L2",
                "reason": "Explicit policy conflict flagged by AI."
            }

        if risk_score <= self.AUTO_APPROVE_THRESHOLD:
            return {
                "status": "APPROVED",
                "assigned_queue": "AUTO_APPROVE",
                "reason": f"Low risk ({risk_score*100:.2f}%). Meets approval criteria."
            }

        elif risk_score >= self.AUTO_REJECT_THRESHOLD:
            return {
                "status": "REJECTED",
                "assigned_queue": "AUTO_REJECT",
                "reason": f"High risk ({risk_score*100:.2f}%). Exceeds threshold."
            }

        return {
            "status": "PENDING_REVIEW",
            "assigned_queue": "HUMAN_UNDERWRITER_L1",
            "reason": f"Moderate risk ({risk_score*100:.2f}%). Requires human judgment."
        }
class Controller:
    def __init__(self):
        self.vitality = 1.0
        self.breach_count = 0
        self.recovery_rate = 0.02 # قدرة النظام على الشفاء الذاتي

    def calculate_breach_cost(self):
        # تكلفة الإصلاح تزداد كلما ضعف النظام
        base_cost = 0.15
        vulnerability_penalty = 1.0 + (1.0 - self.vitality)
        return base_cost * vulnerability_penalty

    def apply_recovery(self, risk):
        # إذا كان الخطر منخفضاً (أقل من 30%)، يستعيد النظام قوته
        if risk < 30 and self.vitality < 1.0:
            boost = self.recovery_rate * (1.0 - risk/100)
            self.vitality = min(1.0, self.vitality + boost)
            return boost
        return 0

    def execute_breach(self):
        cost = self.calculate_breach_cost()
        self.vitality -= cost
        self.breach_count += 1
        return cost
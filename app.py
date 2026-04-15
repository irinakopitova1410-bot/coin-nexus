class NexusScorer:
    def __init__(self, revenue, costs, debt):
        self.revenue = float(revenue)
        self.costs = float(costs)
        self.debt = float(debt)
        self.ebitda = self.revenue - self.costs

    def calculate_isa_320(self):
        # Materialità Professionale (Standard Revisione)
        return max(self.ebitda * 0.05, self.revenue * 0.01)

    def calculate_bep(self):
        # Punto di Pareggio e Sicurezza
        fixed_costs = self.costs * 0.45
        cont_margin_ratio = 1 - ((self.costs * 0.55) / self.revenue)
        bep = fixed_costs / cont_margin_ratio if cont_margin_ratio > 0 else self.revenue
        safety_margin = ((self.revenue - bep) / self.revenue) * 100
        return bep, round(max(0, safety_margin), 2)

    def get_nexus_rating(self):
        # Rating Basel IV
        dscr = self.ebitda / (self.debt if self.debt > 0 else 1)
        score = ((self.ebitda / self.revenue) * 60) + (min(dscr, 5) * 8)
        if score > 75: return "AAA", "Massima Solvibilità"
        if score > 50: return "BBB", "Solvibilità Buona"
        return "CCC", "Rischio Monitorato"

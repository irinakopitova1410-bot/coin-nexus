import numpy as np

class NexusScorer:
    def __init__(self, revenue, costs, debt):
        self.revenue = float(revenue)
        self.costs = float(costs)
        self.debt = float(debt)
        self.ebitda = self.revenue - self.costs

    def calculate_isa_320(self):
        """Calcolo Materialità Professionale standard Revisione"""
        materiality = max(self.ebitda * 0.05, self.revenue * 0.01)
        tolerable_error = materiality * 0.75
        return materiality, tolerable_error

    def calculate_bep(self):
        """Calcolo Break-Even Point e Margine di Sicurezza"""
        fixed_costs = self.costs * 0.45
        variable_costs_ratio = (self.costs * 0.55) / self.revenue
        
        if (1 - variable_costs_ratio) <= 0:
            return self.revenue, 0
            
        bep = fixed_costs / (1 - variable_costs_ratio)
        safety_margin = ((self.revenue - bep) / self.revenue) * 100
        return bep, round(max(0, safety_margin), 2)

    def get_nexus_rating(self):
        """Algoritmo di Rating Basilea IV Proprietiario"""
        dscr = self.ebitda / (self.debt if self.debt > 0 else 1)
        margin_pct = (self.ebitda / self.revenue) * 100
        score = (margin_pct * 0.6) + (min(dscr, 5) * 8)
        
        if score > 75: return "AAA", "Massima Solvibilità (Prime)"
        if score > 50: return "BBB", "Solvibilità Buona (Investment Grade)"
        if score > 25: return "CCC", "Vulnerabilità (Speculative)"
        return "D", "Rischio Default"

def compute_metrics(d):

    dscr = d.ebitda / d.debt if d.debt else 0
    liquidity = (d.cash + d.receivables) / d.payables if d.payables else 0
    leverage = d.debt / (d.ebitda + 1)

    return {
        "dscr": dscr,
        "liquidity": liquidity,
        "leverage": leverage
    }

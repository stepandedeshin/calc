async def count_percent(amount: int, percent: int) -> float:
    return float((amount * (100-percent))/100)


async def count_divisor(amount: float, divisor: int) -> float:
    return float(amount/divisor)


async def count_percentages(amount: float) -> list[float]:
    return [float(amount*0.03), float(amount*0.045), float(amount*0.075)]
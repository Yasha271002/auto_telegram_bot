from ai_features import car_podbor, compare_cars, should_buy, detect_intent


async def route(text: str):
    intent = await detect_intent(text)

    if "COMPARE" in intent:
        return await compare_cars(text)

    if "BUY" in intent:
        return await should_buy(text)

    if "PODBOR" in intent:
        return await car_podbor(text)

    return await car_podbor(text)
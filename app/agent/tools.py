from app.tools.look_up import lookup_offer


def lookup_offering(arguments: dict) -> dict:
    if not isinstance(arguments, dict) or set(arguments) != {"offering_id"}:
        return {"status": "invalid_argument"}

    offering_id = arguments["offering_id"]
    if not isinstance(offering_id, str) or not offering_id.strip():
        return {"status": "invalid_argument"}

    return lookup_offer(offering_id)

TIER_RATES = {
    "VIP": 150.0,
    "PREMIUM": 90.0,
    "GENERAL": 45.0,
}
MAX_ROW = 1000
MAX_AGE = 120
MAX_DIGITS = 10


def _parse_nonneg_int(text, max_value):
    """Return int for a plain ASCII decimal string within [0, max_value], else None."""
    text = text.strip()
    if not text or len(text) > MAX_DIGITS or not (text.isascii() and text.isdigit()):
        return None
    value = int(text)
    return value if value <= max_value else None


def decode_promo_voucher(voucher_code):
    if not isinstance(voucher_code, str):
        return "Invalid voucher: expected text like EARLY-20"
    parts = voucher_code.strip().split('-')
    if len(parts) != 2:
        return "Invalid voucher: expected format PREFIX-PERCENT"
    prefix = parts[0].strip()
    percentage = _parse_nonneg_int(parts[1], 100)
    if not prefix:
        return "Invalid voucher: missing prefix"
    if percentage is None:
        return "Invalid voucher: percentage must be a whole number from 0 to 100"
    return f"Valid {prefix.upper()}: {percentage}% OFF"


def calculate_seat_tier_price(tier_spec):
    """Return the seat price as a float, or None if the spec is invalid."""
    if not isinstance(tier_spec, str):
        return None
    parts = tier_spec.split('@')
    if len(parts) != 2:
        return None
    tier = parts[0].strip().upper()
    row = _parse_nonneg_int(parts[1], MAX_ROW)
    if tier not in TIER_RATES or row is None:
        return None
    return TIER_RATES[tier] + (row * 2.0)


def parse_attendee_badge(badge_csv):
    if not isinstance(badge_csv, str):
        return "Invalid badge: expected text like Name,Age,Seat"
    tokens = badge_csv.split(',')
    if len(tokens) != 3:
        return "Invalid badge: expected exactly 3 fields (Name,Age,Seat)"
    name = tokens[0].strip()
    seat = tokens[2].strip()
    age = _parse_nonneg_int(tokens[1], MAX_AGE)
    if not name or not seat:
        return "Invalid badge: name and seat must not be empty"
    if age is None:
        return f"Invalid badge: age must be a whole number from 0 to {MAX_AGE}"
    category = "Child" if age < 18 else "Adult"
    return f"{name} [{category}] - Seat {seat}"


def main():
    print("==== Running decode_promo_voucher ====")
    v_input = input("Enter voucher (e.g. EARLY-20): ")
    print("Voucher:", decode_promo_voucher(v_input))

    print("\n==== Running calculate_seat_tier_price ====")
    t_input = input("Enter tier spec (e.g. VIP@4): ")
    price = calculate_seat_tier_price(t_input)
    if price is None:
        print("Invalid tier spec: expected TIER@ROW, TIER in VIP/PREMIUM/GENERAL, ROW 0-%d" % MAX_ROW)
    else:
        print("Seat Price: $", price)

    print("\n==== Running parse_attendee_badge ====")
    b_input = input("Enter badge CSV (Name,Age,Seat): ")
    print("Badge:", parse_attendee_badge(b_input))


if __name__ == "__main__":
    main()

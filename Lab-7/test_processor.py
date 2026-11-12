from hypothesis import given, strategies as st
from processor import decode_promo_voucher, calculate_seat_tier_price, parse_attendee_badge


@given(st.text() | st.none())
def test_decode_promo_voucher_no_crash(s):
    try:
        decode_promo_voucher(s)
    except Exception as e:
        assert False, f"decode_promo_voucher crashed with: {e!r} for input {s!r}"


@given(st.text() | st.none())
def test_calculate_seat_tier_price_safe(s):
    try:
        calculate_seat_tier_price(s)
    except Exception as e:
        assert False, f"calculate_seat_tier_price crashed with: {e!r} for input {s!r}"


@given(st.text() | st.none())
def test_parse_attendee_badge_safe(s):
    try:
        parse_attendee_badge(s)
    except Exception as e:
        assert False, f"parse_attendee_badge crashed with: {e!r} for input {s!r}"

"""
Branch-coverage tests for event_ticket_tier.py (Lab 6, PES1UG24AM244).

Goal: make every decision (if/elif/else, loop entry and exit, break) go
both ways, including combinations that line coverage alone misses.

Run:
    coverage run --branch -m pytest BranchCoverageTest_event_ticket_tier.py
    coverage report -m
"""

import pytest
from event_ticket_tier import process_ticket_manifest, monitor_gate_flow


def manifest(tier="general", orders=None, confirmed=True, lounge=False):
    return {
        "is_confirmed": confirmed,
        "tier": tier,
        "exclusive_lounge": lounge,
        "orders": orders if orders is not None else [],
    }


def run(manifests, rate=0.0):
    return process_ticket_manifest(manifests, rate)


# ---- input validation: both operands of the `or`, and the passing case ----

def test_single_general_order():
    result = run([manifest(orders=[{"qty": 2, "promo": ""}])], 0.1)
    assert result == {"total_revenue": 99.0, "status": "COMPLETED"}


def test_manifests_not_a_list_raises():
    with pytest.raises(ValueError):
        run("not a list", 0.1)


def test_negative_tax_rate_raises():
    with pytest.raises(ValueError):
        run([], -0.01)


def test_zero_tax_rate_is_valid():
    assert run([manifest(orders=[{"qty": 1, "promo": ""}])], 0.0)["status"] == "COMPLETED"


# ---- confirmation branch ----

def test_unconfirmed_manifest_skipped():
    assert run([manifest(confirmed=False, orders=[{"qty": 1, "promo": ""}])]) == {
        "total_revenue": 0.0, "status": "ZERO_SALES"}


def test_missing_keys_use_defaults():
    # No is_confirmed key -> treated as unconfirmed.
    assert run([{"tier": "vip", "orders": [{"qty": 1}]}])["status"] == "ZERO_SALES"


def test_confirmed_manifest_with_defaults_has_no_orders():
    # Only is_confirmed: tier defaults to general, orders to [] -> loop never runs.
    assert run([{"is_confirmed": True}]) == {"total_revenue": 0.0, "status": "ZERO_SALES"}


# ---- tier if / elif / elif / else ----

def test_vip_tier_price():
    assert run([manifest("vip", [{"qty": 1, "promo": ""}])])["total_revenue"] == 150.0


def test_premium_tier_price():
    assert run([manifest("premium", [{"qty": 1, "promo": ""}])])["total_revenue"] == 90.0


def test_general_tier_price():
    assert run([manifest("general", [{"qty": 1, "promo": ""}])])["total_revenue"] == 45.0


def test_unknown_tier_rejected():
    result = run([manifest("gold", [{"qty": 1, "promo": ""}]),
                  manifest("general", [{"qty": 1, "promo": ""}])])
    assert result == {"total_revenue": 45.0, "status": "COMPLETED"}


# ---- order loop: empty / non-empty, qty guard ----

def test_empty_orders_list_skips_loop():
    assert run([manifest(orders=[])])["status"] == "ZERO_SALES"


def test_qty_zero_rejected():
    result = run([manifest(orders=[{"qty": 0}, {"qty": 1, "promo": ""}])])
    assert result == {"total_revenue": 45.0, "status": "COMPLETED"}


def test_qty_negative_rejected():
    result = run([manifest(orders=[{"qty": -3}, {"qty": 1, "promo": ""}])])
    assert result == {"total_revenue": 45.0, "status": "COMPLETED"}


def test_order_missing_qty_defaults_to_zero_and_is_rejected():
    assert run([manifest(orders=[{}])])["status"] == "ZERO_SALES"


# ---- promo branches: FRAUD_RISK (vip / non-vip), EARLYBIRD, none ----

def test_vip_fraud_risk_wipes_manifest_and_breaks():
    orders = [
        {"qty": 1, "promo": "EARLYBIRD"},
        {"qty": 2, "promo": "FRAUD_RISK"},
        {"qty": 1, "promo": ""},  # unreachable after the break
    ]
    assert run([manifest("vip", orders)])["status"] == "ZERO_SALES"


def test_vip_fraud_risk_keeps_lounge_fee():
    orders = [{"qty": 2, "promo": "FRAUD_RISK"}]
    assert run([manifest("vip", orders, lounge=True)]) == {
        "total_revenue": 75.0, "status": "COMPLETED"}


def test_non_vip_fraud_risk_is_rejected_but_still_billed():
    # Documents current behaviour: for non-VIP tiers the fraud order is
    # counted as rejected yet its price is still added to the manifest total.
    orders = [{"qty": 2, "promo": "FRAUD_RISK"}]
    result = run([manifest("general", orders)])
    assert result == {"total_revenue": 90.0, "status": "COMPLETED"}


def test_earlybird_discount():
    result = run([manifest(orders=[{"qty": 2, "promo": "EARLYBIRD"}])])
    assert result["total_revenue"] == pytest.approx(72.0)


def test_earlybird_ignores_bulk_discount():
    result = run([manifest(orders=[{"qty": 5, "promo": "EARLYBIRD"}])])
    assert result["total_revenue"] == pytest.approx(180.0)  # 225 * 0.8, no -20


def test_bulk_discount_applies_at_exactly_five():
    assert run([manifest(orders=[{"qty": 5, "promo": ""}])])["total_revenue"] == pytest.approx(205.0)


def test_no_bulk_discount_at_four():
    assert run([manifest(orders=[{"qty": 4, "promo": ""}])])["total_revenue"] == pytest.approx(180.0)


def test_unrecognised_promo_behaves_like_no_promo():
    assert run([manifest(orders=[{"qty": 5, "promo": "SUMMER"}])])["total_revenue"] == pytest.approx(205.0)


# ---- lounge branch ----

def test_lounge_fee_added():
    result = run([manifest(orders=[{"qty": 1, "promo": ""}], lounge=True)])
    assert result["total_revenue"] == pytest.approx(120.0)


def test_lounge_fee_not_added_when_false():
    result = run([manifest(orders=[{"qty": 1, "promo": ""}], lounge=False)])
    assert result["total_revenue"] == pytest.approx(45.0)


# ---- final status: AUDIT_REJECTED / ZERO_SALES / COMPLETED ----

def test_exactly_four_rejections_is_not_audit_rejected():
    orders = [{"qty": 0}] * 4 + [{"qty": 1, "promo": ""}]
    assert run([manifest(orders=orders)])["status"] == "COMPLETED"


def test_five_rejections_is_audit_rejected_with_revenue():
    orders = [{"qty": 0}] * 5 + [{"qty": 1, "promo": ""}]
    result = run([manifest(orders=orders)], 0.1)
    assert result == {"total_revenue": 49.5, "status": "AUDIT_REJECTED"}


def test_audit_rejected_takes_priority_over_zero_sales():
    result = run([manifest(orders=[{"qty": 0}] * 5)])
    assert result == {"total_revenue": 0.0, "status": "AUDIT_REJECTED"}


def test_empty_manifest_list_is_zero_sales():
    assert run([]) == {"total_revenue": 0.0, "status": "ZERO_SALES"}


def test_tax_is_applied_and_rounded():
    result = run([manifest(orders=[{"qty": 1, "promo": ""}])], 0.2)
    assert result == {"total_revenue": 54.0, "status": "COMPLETED"}  # 45 * 1.2


# ---- monitor_gate_flow ----

def test_gate_flow_empty_is_no_data():
    assert monitor_gate_flow([]) == "NO_DATA"


def test_gate_flow_none_is_no_data():
    assert monitor_gate_flow(None) == "NO_DATA"


def test_gate_flow_two_consecutive_high_rates_overflow():
    assert monitor_gate_flow([[10, 60, 60]]) == "OVERFLOW"


def test_gate_flow_single_high_rate_is_not_overflow():
    assert monitor_gate_flow([[60]]) == "FLOW_NORMAL"


def test_gate_flow_streak_resets_on_low_rate():
    assert monitor_gate_flow([[60, 10, 60, 10]]) == "FLOW_NORMAL"


def test_gate_flow_rate_of_exactly_fifty_is_not_congested():
    assert monitor_gate_flow([[50, 50, 50]]) == "FLOW_NORMAL"


def test_gate_flow_empty_stream_is_normal():
    assert monitor_gate_flow([[]]) == "FLOW_NORMAL"


def test_gate_flow_overflow_in_later_stream():
    assert monitor_gate_flow([[10, 20], [70, 80]]) == "OVERFLOW"


def test_gate_flow_streak_does_not_carry_between_streams():
    assert monitor_gate_flow([[10, 60], [60, 10]]) == "FLOW_NORMAL"

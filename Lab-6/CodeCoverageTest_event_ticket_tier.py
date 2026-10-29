"""
Line-coverage tests for event_ticket_tier.py (Lab 6, PES1UG24AM244).

Goal: execute every line of process_ticket_manifest and monitor_gate_flow
at least once.

Run:
    coverage run -m pytest CodeCoverageTest_event_ticket_tier.py
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


# ---------------- process_ticket_manifest ----------------

def test_single_general_order():
    result = process_ticket_manifest([manifest(orders=[{"qty": 2, "promo": ""}])], 0.1)
    assert result["total_revenue"] == 99.0
    assert result["status"] == "COMPLETED"


def test_invalid_manifests_type_raises():
    with pytest.raises(ValueError):
        process_ticket_manifest("not a list", 0.1)


def test_negative_tax_rate_raises():
    with pytest.raises(ValueError):
        process_ticket_manifest([], -0.5)


def test_unconfirmed_manifest_is_skipped_zero_sales():
    result = process_ticket_manifest(
        [manifest(confirmed=False, orders=[{"qty": 3, "promo": ""}])], 0.1
    )
    assert result == {"total_revenue": 0.0, "status": "ZERO_SALES"}


def test_vip_premium_and_unknown_tier():
    manifests = [
        manifest("vip", [{"qty": 1, "promo": ""}]),        # 150
        manifest("premium", [{"qty": 1, "promo": ""}]),    # 90
        manifest("gold", [{"qty": 1, "promo": ""}]),       # unknown -> rejected
    ]
    result = process_ticket_manifest(manifests, 0.0)
    assert result == {"total_revenue": 240.0, "status": "COMPLETED"}


def test_non_positive_quantity_is_rejected():
    result = process_ticket_manifest(
        [manifest(orders=[{"qty": 0, "promo": ""}, {"qty": 1, "promo": ""}])], 0.0
    )
    assert result == {"total_revenue": 45.0, "status": "COMPLETED"}


def test_vip_fraud_risk_stops_manifest_but_lounge_fee_remains():
    orders = [
        {"qty": 1, "promo": "EARLYBIRD"},   # 120, later wiped by the fraud order
        {"qty": 2, "promo": "FRAUD_RISK"},  # vip -> total reset to 0, break
        {"qty": 1, "promo": ""},            # never processed
    ]
    result = process_ticket_manifest([manifest("vip", orders, lounge=True)], 0.0)
    assert result == {"total_revenue": 75.0, "status": "COMPLETED"}


def test_earlybird_discount():
    result = process_ticket_manifest(
        [manifest(orders=[{"qty": 2, "promo": "EARLYBIRD"}])], 0.0
    )
    assert result["total_revenue"] == pytest.approx(72.0)  # 90 * 0.8


def test_bulk_discount_for_five_or_more():
    result = process_ticket_manifest([manifest(orders=[{"qty": 5, "promo": ""}])], 0.0)
    assert result["total_revenue"] == pytest.approx(205.0)  # 225 - 20


def test_exclusive_lounge_surcharge():
    result = process_ticket_manifest(
        [manifest(orders=[{"qty": 1, "promo": ""}], lounge=True)], 0.0
    )
    assert result["total_revenue"] == pytest.approx(120.0)  # 45 + 75


def test_audit_rejected_when_more_than_four_rejections():
    orders = [{"qty": 0, "promo": ""}] * 5 + [{"qty": 1, "promo": ""}]
    result = process_ticket_manifest([manifest(orders=orders)], 0.1)
    assert result["status"] == "AUDIT_REJECTED"
    assert result["total_revenue"] == pytest.approx(49.5)  # 45 * 1.1


# ---------------- monitor_gate_flow ----------------

def test_gate_flow_no_data():
    assert monitor_gate_flow([]) == "NO_DATA"


def test_gate_flow_overflow():
    assert monitor_gate_flow([[10, 60, 60]]) == "OVERFLOW"


def test_gate_flow_normal_with_streak_reset():
    assert monitor_gate_flow([[60, 10, 60, 10]]) == "FLOW_NORMAL"

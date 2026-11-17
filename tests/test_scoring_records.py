from pathlib import Path

from scs_gate.scoring_policy import ScoringPolicy
from scs_gate.scoring_records import ScoringRecordChain
from scs_gate.receipts import ZERO_HASH


def test_scoring_record_chain_links_hashes(tmp_path: Path):
    policy = ScoringPolicy.from_dict({
        "policy_id": "scorer-test",
        "rule_variants": [],
        "sizing_variants": [],
    })
    chain = ScoringRecordChain(tmp_path / "scoring.jsonl", b"test-key")
    first = chain.append({"signal_id": "a", "settled": True}, policy)
    second = chain.append({"signal_id": "b", "settled": False, "excluded": True}, policy)
    assert first["prev_hash"] == ZERO_HASH
    assert second["prev_hash"] == first["this_hash"]
    assert first["policy_hash"] == policy.policy_hash
    assert first["signature"].startswith("hmac-sha256:")

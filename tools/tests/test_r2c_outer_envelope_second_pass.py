"""Fail-closed checks of scoped, source-free 26.2 outer-field review evidence.

This does not qualify the full outer packet or make source VAR/SEM admission.
It prevents a second-pass *candidate* from drifting from the previously
fingerprinted official-method excerpts or becoming an authority flag.
"""
from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PARENT = ROOT / "vanilla/reviews/network/r2c-first-pass-source-free-observations.json"
SECOND = ROOT / "vanilla/reviews/network/r2c-outer-envelope-second-pass-source-findings.json"
SOURCE_SHA256 = "1e9bca3dff83cd83e7905f8810f1ec9899361fa2dc83fe893bb48beeb04df750"
PINNED_DIRECT_METHODS = {
    11: "1b44c24dfefe344f01d9ac6a9b813491e6d8e3ca05d430b5c31c5a6192cd9918",
    12: "3e65a6cbd53ec9f015aeb1d27b4d80037ec425847df65b79e112722ee0c4151b",
    13: "301b54bda0182b88f20afbe248551d5fe261e337f55f8f53ebada2184a53b7d6",
    14: "ba4362c0be9a8ec404fd41c5d057925643311b072d85fcbe5ede5e281a78cca6",
    16: "45ca45c1557008f36283f634989d69c6effc350c68b161fb27e64c434409b6fe",
}
FALSE_AUTHORITY = (
    "all_outer_delegates_and_errors_reviewed",
    "independent_human_var_sem_approved",
    "independent_atlas_gate_passed",
    "client_biome_numeric_ids_admitted",
    "heightmap_state_facts_admitted",
    "outer_chunk_packet_lifecycle_admitted",
    "production_chunk_publication_admitted",
)


def validate(review: dict, original: dict) -> None:
    if review.get("source_archive_sha256") != SOURCE_SHA256:
        raise ValueError("source lock drift")
    if original.get("source_archive_sha256") != SOURCE_SHA256:
        raise ValueError("first-pass source lock drift")
    if review.get("evidence_parent_source_rich_sha256") != original.get(
        "source_rich_local_review_file_sha256"
    ):
        raise ValueError("source-rich provenance drift")
    if review.get("commit_policy") != (
        "DIRECT_METHOD_SOURCE_READ_NO_INDEPENDENT_ATLAS_VAR_SEM_ADMISSION"
    ):
        raise ValueError("source-review policy drift")
    if review.get("source_text_committed") is not False:
        raise ValueError("official source may not be committed")
    if review.get("schema") != 1 or review.get("minecraft_version") != "26.2":
        raise ValueError("target schema drift")
    if review.get("protocol_version") != 776 or review.get("data_version") != 4903:
        raise ValueError("protocol/world-version drift")
    for flag in FALSE_AUTHORITY:
        if review.get(flag) is not False:
            raise ValueError(f"unadmitted source authority: {flag}")
    methods = review.get("methods")
    if not isinstance(methods, list) or len(methods) != len(PINNED_DIRECT_METHODS):
        raise ValueError("incorrect bounded method selection")
    indexed = {entry["review_index"]: entry for entry in original["methods"]}
    if [item.get("original_review_index") for item in methods] != list(PINNED_DIRECT_METHODS):
        raise ValueError("review index drift or duplicate methods")
    for method in methods:
        index = method["original_review_index"]
        observed = indexed[index]
        if (
            method.get("body_sha256") != PINNED_DIRECT_METHODS[index]
            or method["body_sha256"] != observed["body_sha256"]
            or method.get("source_excerpt_sha256") != observed["source_excerpt_sha256"]
        ):
            raise ValueError(f"source body/excerpt fingerprint drift at method {index}")
        if method.get("second_pass_direct_method_read") is not True:
            raise ValueError(f"missing direct read at method {index}")
        if method.get("all_reached_delegates_reviewed") is not False:
            raise ValueError(f"unsafe delegate closure at method {index}")
        if method.get("independent_source_var_sem_admitted") is not False:
            raise ValueError(f"unsafe VAR/SEM at method {index}")
        if "source_excerpt" in method or "source_text" in method:
            raise ValueError("source-rich method content is forbidden")
        if not method.get("direct_method_finding"):
            raise ValueError("missing direct method finding")
    required_law_ids = {
        "CANDIDATE-NET-R2C-OUTER-COORDINATES-AND-ORDER",
        "CANDIDATE-NET-R2C-CHUNK-RECEIVE-BOUNDARY",
        "CANDIDATE-NET-R2C-LIGHT-RECEIVE-ORDER",
    }
    laws = review.get("directly_supported_candidate_laws")
    if not isinstance(laws, list) or {item["id"] for item in laws} != required_law_ids:
        raise ValueError("direct-only semantic law selection drift")
    expected_links = {
        "CANDIDATE-NET-R2C-OUTER-COORDINATES-AND-ORDER": [11, 12, 13],
        "CANDIDATE-NET-R2C-CHUNK-RECEIVE-BOUNDARY": [14],
        "CANDIDATE-NET-R2C-LIGHT-RECEIVE-ORDER": [16],
    }
    for law in laws:
        if law.get("method_indices") != expected_links[law["id"]]:
            raise ValueError("semantic law method evidence drift")
    if len(review.get("open_delegates_and_semantics", [])) < 6:
        raise ValueError("reached delegate closure was prematurely erased")


class OuterPacketDirectReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.original = json.loads(PARENT.read_text())
        cls.review = json.loads(SECOND.read_text())

    def test_pinned_scoped_second_pass_is_source_free_and_unadmitted(self) -> None:
        validate(self.review, self.original)

    def test_no_source_id_fingerprint_or_delegate_gap_may_disappear(self) -> None:
        changed = copy.deepcopy(self.review)
        changed["methods"][2]["body_sha256"] = "a" * 64
        with self.assertRaisesRegex(ValueError, "fingerprint drift"):
            validate(changed, self.original)
        changed = copy.deepcopy(self.review)
        changed["methods"].pop()
        with self.assertRaisesRegex(ValueError, "selection"):
            validate(changed, self.original)
        changed = copy.deepcopy(self.review)
        changed["open_delegates_and_semantics"] = []
        with self.assertRaisesRegex(ValueError, "prematurely erased"):
            validate(changed, self.original)

    def test_no_direct_source_review_can_promote_production_authority(self) -> None:
        for flag in FALSE_AUTHORITY:
            changed = copy.deepcopy(self.review)
            changed[flag] = True
            with self.subTest(flag=flag), self.assertRaisesRegex(ValueError, "unadmitted"):
                validate(changed, self.original)
        changed = copy.deepcopy(self.review)
        changed["methods"][0]["all_reached_delegates_reviewed"] = True
        with self.assertRaisesRegex(ValueError, "delegate closure"):
            validate(changed, self.original)
        changed = copy.deepcopy(self.review)
        changed["methods"][0]["source_excerpt"] = "no source allowed"
        with self.assertRaisesRegex(ValueError, "forbidden"):
            validate(changed, self.original)

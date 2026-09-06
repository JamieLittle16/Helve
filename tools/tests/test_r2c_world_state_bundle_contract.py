from __future__ import annotations

import unittest

from tools import r2c_world_state_parent_review_complete as parent_review
from tools import r2c_world_state_source_review_bundle as source_bundle


class WorldStateBundleContractTests(unittest.TestCase):
    def test_parent_review_accepts_exact_canonical_source_bundle_shape(self) -> None:
        self.assertEqual(
            set(parent_review.BUNDLE_REGULAR_FILES),
            set(source_bundle.REQUIRED_ARCHIVE_MEMBERS),
        )


if __name__ == "__main__":
    unittest.main()

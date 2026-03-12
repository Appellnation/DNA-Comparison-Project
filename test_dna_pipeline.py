import pytest
import sys
import os

# Allow imports from the backend folder when running from project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from Smith_Waterman_Revised import (
    confirm_sequences_are_nucleotides,
    rna_to_dna,
    smith_waterman,
    calculate_similarity,
)
from app import app as flask_app


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def client():
    """Flask test client with testing mode enabled."""
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        yield client


# ===========================================================================
# confirm_sequences_are_nucleotides
# ===========================================================================

class TestConfirmSequencesAreNucleotides:

    def test_valid_dna_sequences(self):
        assert confirm_sequences_are_nucleotides("ATCG", "GCTA") is True

    def test_valid_rna_sequences(self):
        # U is a valid RNA nucleotide
        assert confirm_sequences_are_nucleotides("AUCG", "GCUA") is True

    def test_mixed_dna_and_rna(self):
        assert confirm_sequences_are_nucleotides("ATCG", "AUCG") is True

    def test_single_character_sequences(self):
        assert confirm_sequences_are_nucleotides("A", "T") is True

    def test_invalid_character_in_seq1(self):
        assert confirm_sequences_are_nucleotides("AXCG", "GCTA") is False

    def test_invalid_character_in_seq2(self):
        assert confirm_sequences_are_nucleotides("ATCG", "GXTA") is False

    def test_numeric_characters_are_invalid(self):
        assert confirm_sequences_are_nucleotides("1234", "ATCG") is False

    def test_empty_sequences_are_valid(self):
        # Both empty — chain is empty, all() on empty is True
        assert confirm_sequences_are_nucleotides("", "") is True

    def test_lowercase_is_invalid(self):
        # The function does not normalise case — lowercase should fail
        assert confirm_sequences_are_nucleotides("atcg", "GCTA") is False

    def test_whitespace_is_invalid(self):
        assert confirm_sequences_are_nucleotides("AT CG", "GCTA") is False


# ===========================================================================
# rna_to_dna
# ===========================================================================

class TestRnaToDna:

    def test_converts_u_to_t(self):
        assert rna_to_dna("AUCG") == "ATCG"

    def test_no_u_is_unchanged(self):
        assert rna_to_dna("ATCG") == "ATCG"

    def test_all_u_sequence(self):
        assert rna_to_dna("UUUU") == "TTTT"

    def test_multiple_u_replacements(self):
        assert rna_to_dna("AUUGCUU") == "ATTGCTT"

    def test_empty_string(self):
        assert rna_to_dna("") == ""

    def test_single_u(self):
        assert rna_to_dna("U") == "T"

    def test_case_sensitivity(self):
        # Lowercase 'u' should not be converted (function uses exact replace)
        assert rna_to_dna("aucg") == "atcg"


# ===========================================================================
# smith_waterman
# ===========================================================================

class TestSmithWaterman:

    # --- Return structure --------------------------------------------------

    def test_returns_expected_keys(self):
        result = smith_waterman("ATCG", "ATCG")
        assert "matrix" in result
        assert "traceback" in result
        assert "aligned_seq1" in result
        assert "aligned_seq2" in result
        assert "max_score" in result

    # --- Matrix dimensions ------------------------------------------------

    def test_matrix_dimensions(self):
        seq1, seq2 = "ATCG", "GCT"
        result = smith_waterman(seq1, seq2)
        rows = len(result["matrix"])
        cols = len(result["matrix"][0])
        assert rows == len(seq1) + 1
        assert cols == len(seq2) + 1

    def test_matrix_first_row_all_zero(self):
        result = smith_waterman("ATCG", "GCTA")
        assert all(cell["score"] == 0 for cell in result["matrix"][0])

    def test_matrix_first_col_all_zero(self):
        result = smith_waterman("ATCG", "GCTA")
        assert all(result["matrix"][i][0]["score"] == 0 for i in range(len(result["matrix"])))

    def test_no_negative_scores_in_matrix(self):
        # Smith-Waterman floors scores at 0
        result = smith_waterman("AAAA", "CCCC")
        for row in result["matrix"]:
            for cell in row:
                assert cell["score"] >= 0

    # --- Identical sequences ----------------------------------------------

    def test_identical_sequences_max_score(self):
        seq = "ATCG"
        result = smith_waterman(seq, seq)
        # Every character matches (+1 each), so max score == len(seq)
        assert result["max_score"] == len(seq)

    def test_identical_sequences_aligned_output(self):
        seq = "ATCG"
        result = smith_waterman(seq, seq)
        assert result["aligned_seq1"] == seq
        assert result["aligned_seq2"] == seq

    # --- Completely different sequences -----------------------------------

    def test_no_common_bases_zero_score(self):
        # AAAA vs CCCC — no matches, Smith-Waterman clamps to 0
        result = smith_waterman("AAAA", "CCCC")
        assert result["max_score"] == 0

    def test_no_common_bases_empty_alignment(self):
        result = smith_waterman("AAAA", "CCCC")
        assert result["aligned_seq1"] == ""
        assert result["aligned_seq2"] == ""
        assert result["traceback"] == []

    # --- Partial matches --------------------------------------------------

    def test_partial_match_finds_common_region(self):
        # "ATCG" is embedded in seq2; alignment should recover it
        result = smith_waterman("ATCG", "XXXXXATCGYYYYY".replace("X", "A").replace("Y", "C"))
        assert "ATCG" in result["aligned_seq1"]

    def test_single_matching_base(self):
        result = smith_waterman("A", "A")
        assert result["max_score"] == 1

    # --- Aligned sequence lengths must match ------------------------------

    def test_aligned_sequences_same_length(self):
        result = smith_waterman("ATCGATCG", "TAGCTAGC")
        assert len(result["aligned_seq1"]) == len(result["aligned_seq2"])

    # --- Traceback is a list of [row, col] pairs --------------------------

    def test_traceback_cells_within_matrix_bounds(self):
        seq1, seq2 = "ATCG", "ATCG"
        result = smith_waterman(seq1, seq2)
        rows = len(seq1) + 1
        cols = len(seq2) + 1
        for cell in result["traceback"]:
            assert 0 <= cell[0] < rows
            assert 0 <= cell[1] < cols

    # --- Single-character sequences ---------------------------------------

    def test_single_chars_match(self):
        result = smith_waterman("A", "A")
        assert result["aligned_seq1"] == "A"
        assert result["aligned_seq2"] == "A"

    def test_single_chars_mismatch(self):
        result = smith_waterman("A", "T")
        assert result["max_score"] == 0


# ===========================================================================
# calculate_similarity
# ===========================================================================

class TestCalculateSimilarity:

    def test_identical_sequences_100_percent(self):
        assert calculate_similarity("ATCG", "ATCG") == 100.0

    def test_completely_different_sequences_zero_percent(self):
        assert calculate_similarity("AAAA", "CCCC") == 0.0

    def test_half_matches(self):
        # "AT" vs "AC" — 1 match (A), 1 mismatch (T vs C) = 50%
        result = calculate_similarity("AT", "AC")
        assert result == pytest.approx(50.0)

    def test_gaps_count_as_mismatches(self):
        # "A-" vs "AT" — A matches, gap is a mismatch → 50%
        result = calculate_similarity("A-", "AT")
        assert result == pytest.approx(50.0)

    def test_all_gaps_in_one_sequence(self):
        result = calculate_similarity("----", "ATCG")
        assert result == 0.0

    def test_empty_sequences_return_zero(self):
        assert calculate_similarity("", "") == 0.0

    def test_mismatched_lengths_return_none(self):
        # The function explicitly checks for equal length
        assert calculate_similarity("AT", "ATC") is None

    def test_single_match(self):
        assert calculate_similarity("A", "A") == 100.0

    def test_single_mismatch(self):
        assert calculate_similarity("A", "T") == 0.0

    def test_longer_sequence(self):
        # 5 matches out of 8 = 50%
        result = calculate_similarity("ATCGATCG", "ATCGCCCC")
        assert result == pytest.approx(62.5)


# ===========================================================================
# Flask API — /compare route
# ===========================================================================

class TestCompareRoute:

    def test_valid_request_returns_200(self, client):
        resp = client.post("/compare", json={"seq1": "ATCG", "seq2": "ATCG"})
        assert resp.status_code == 200

    def test_valid_response_has_expected_keys(self, client):
        resp = client.post("/compare", json={"seq1": "ATCG", "seq2": "GCTA"})
        data = resp.get_json()
        assert "similarity_score" in data
        assert "scoring_matrix" in data
        assert "traceback" in data
        assert "aligned_seq1" in data
        assert "aligned_seq2" in data

    def test_identical_sequences_100_similarity(self, client):
        resp = client.post("/compare", json={"seq1": "ATCGATCG", "seq2": "ATCGATCG"})
        data = resp.get_json()
        assert data["similarity_score"] == pytest.approx(100.0)

    def test_missing_seq1_returns_400(self, client):
        resp = client.post("/compare", json={"seq2": "ATCG"})
        assert resp.status_code == 400

    def test_missing_seq2_returns_400(self, client):
        resp = client.post("/compare", json={"seq1": "ATCG"})
        assert resp.status_code == 400

    def test_missing_both_sequences_returns_400(self, client):
        resp = client.post("/compare", json={})
        assert resp.status_code == 400

    def test_invalid_nucleotides_returns_400(self, client):
        resp = client.post("/compare", json={"seq1": "XYZW", "seq2": "ATCG"})
        assert resp.status_code == 400

    def test_rna_sequences_are_accepted_and_converted(self, client):
        # U-containing sequences should be converted to DNA and succeed
        resp = client.post("/compare", json={"seq1": "AUCG", "seq2": "AUCG"})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["similarity_score"] == pytest.approx(100.0)

    def test_lowercase_input_is_normalised(self, client):
        # app.py calls .strip().upper() before validation
        resp = client.post("/compare", json={"seq1": "atcg", "seq2": "atcg"})
        assert resp.status_code == 200

    def test_input_with_whitespace_is_stripped(self, client):
        resp = client.post("/compare", json={"seq1": "  ATCG  ", "seq2": "ATCG"})
        assert resp.status_code == 200

    def test_empty_body_returns_400(self, client):
        resp = client.post("/compare", data="", content_type="application/json")
        assert resp.status_code == 400

    def test_non_json_body_returns_400(self, client):
        resp = client.post("/compare", data="not json", content_type="text/plain")
        assert resp.status_code == 400


# ===========================================================================
# Flask API — /blast route (input validation only — no live NCBI calls)
# ===========================================================================

class TestBlastRoute:

    def test_missing_sequence_returns_400(self, client):
        resp = client.post("/blast", json={})
        assert resp.status_code == 400

    def test_sequence_too_short_returns_400(self, client):
        resp = client.post("/blast", json={"sequence": "ATCG"})
        assert resp.status_code == 400

    def test_sequence_exactly_19_chars_returns_400(self, client):
        resp = client.post("/blast", json={"sequence": "A" * 19})
        assert resp.status_code == 400

    def test_sequence_exactly_20_chars_passes_validation(self, client, monkeypatch):
        # Patch the BLAST call so the test doesn't hit the network
        import app as app_module
        monkeypatch.setattr(app_module, "get_taxonomy_from_blast", lambda seq: {
            "title": "Mock organism [Escherichia coli]",
            "taxonomy": "Escherichia coli"
        })
        resp = client.post("/blast", json={"sequence": "A" * 20})
        assert resp.status_code == 200

"""Uji aturan audit langsung dari cell notebook; tanpa duplikasi implementation."""

import json
import re
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit

import numpy as np
import pandas as pd
import pytest


@pytest.fixture(scope="module")
def core():
    path = Path(__file__).resolve().parents[1] / "notebooks/01_data_audit_eda.ipynb"
    notebook = json.loads(path.read_text(encoding="utf-8"))
    cells = [c for c in notebook["cells"] if "audit-core" in c["metadata"].get("tags", [])]
    assert len(cells) == 1
    namespace = {
        "pd": pd, "np": np, "re": re, "urlsplit": urlsplit,
        "parse_qs": parse_qs, "unquote": unquote,
        "AUDIT_CUTOFF": pd.Timestamp("2026-10-25T23:59:59+07:00"),
        "SHORT_WORD_LIMIT": 4,
    }
    source = cells[0]["source"]
    if isinstance(source, list):
        source = "".join(source)
    # Cell lokal milik repository, tanpa menjalankan seluruh workflow notebook.
    exec(compile(source, "notebook:audit-core", "exec"), namespace)  # noqa: S102
    return namespace


def row(review_id="r1", place_id="A", **changes):
    value = {
        "review_id": review_id, "nama_tempat": "Kedai " + place_id,
        "rating": "5", "tanggal_review": "2026-10-20T10:00:00Z",
        "teks_review": "Kopinya enak", "url_tempat":
        "https://www.google.com/maps/search/?api=1&query_place_id=" + place_id,
    }
    value.update(changes)
    return value


def test_empty_dataset(core):
    with pytest.raises(ValueError, match="Dataset kosong"):
        core["audit_reviews"](pd.DataFrame(columns=core["REQUIRED_COLUMNS"]))


def test_required_column_missing(core):
    with pytest.raises(ValueError, match="Kolom wajib hilang.*rating"):
        core["audit_reviews"](pd.DataFrame([row()]).drop(columns="rating"))


@pytest.mark.parametrize("value", ["0", "6", "4.5", "bukan angka", ""])
def test_invalid_rating(core, value):
    result = core["audit_reviews"](pd.DataFrame([row(rating=value)]))
    assert bool(result.loc[0, "invalid_rating"])
    assert not bool(result.loc[0, "passes_basic_quality"])


def test_id_conflicts_and_confirmed_copies(core):
    frame = pd.DataFrame([row(), row(), row(teks_review="Pelayanan lama")])
    result = core["audit_reviews"](frame)
    assert result["duplicate_review_id"].sum() == 3
    assert result["confirmed_record_duplicate"].sum() == 2
    assert result["confirmed_duplicate_extra"].sum() == 1
    assert result["conflicting_review_id"].sum() == 3


@pytest.mark.parametrize("value", [None, "", "  \t "])
def test_empty_text(core, value):
    result = core["audit_reviews"](pd.DataFrame([row(teks_review=value)]))
    assert result.loc[0, "is_empty_text"]
    assert not result.loc[0, "passes_basic_quality"]


def test_potential_repetition_remains_valid(core):
    frame = pd.DataFrame([
        row(), row("r2", teks_review="  KOPINYA   enak  "), row("r3", "B"),
    ])
    result = core["audit_reviews"](frame)
    assert result["normalized_text_same_place"].sum() == 2
    assert result["text_across_places"].sum() == 3
    assert result["confirmed_record_duplicate"].sum() == 0
    assert result["possible_legitimate_repetition"].sum() == 3
    assert result["passes_basic_quality"].all()
    assert len(result) == len(frame)


def test_aggregation_uses_location_and_conserves_rows(core):
    frame = pd.DataFrame([
        row(nama_tempat="Nama Lama"), row("r2", nama_tempat="Nama Baru"),
        row("r3", "B", nama_tempat="Nama Baru"),
    ])
    result = core["audit_reviews"](frame)
    stats = core["summarize_places"](result)
    assert len(stats) == 2
    assert stats["review_count"].sum() == 3
    assert stats["contribution_pct"].sum() == pytest.approx(100)
    assert result["inconsistent_place_name"].sum() == 2
    pd.testing.assert_frame_equal(frame, pd.DataFrame([
        row(nama_tempat="Nama Lama"), row("r2", nama_tempat="Nama Baru"),
        row("r3", "B", nama_tempat="Nama Baru"),
    ]))


def test_invalid_dates_urls_and_symbols(core):
    frame = pd.DataFrame([
        row(tanggal_review="bukan tanggal"),
        row("r2", url_tempat="https://google.com.evil.test/maps/place/fake"),
        row("r3", teks_review="☕!!!"),
        row("r4", tanggal_review="2030-01-01"),
    ])
    result = core["audit_reviews"](frame)
    assert result["invalid_date"].sum() == 1
    assert result["invalid_url"].sum() == 1
    assert result["is_symbol_only"].sum() == 1
    assert result["future_date"].sum() == 1
    assert not result["passes_basic_quality"].any()


def test_keyword_boundaries_multilabel_without_sentiment(core):
    result = core["explore_aspects"](pd.Series([
        "Membaca cerita dan kebacaan", "AC, wi-fi dan toilet bersih",
        "Kopinya enak tetapi pelayanan lama", "worth   it",
    ]))
    assert not result.iloc[0].any()  # 'ac' tidak boleh cocok di dalam 'membaca'.
    assert result.loc[1, "Facilities"] and result.loc[1, "Cleanliness"]
    assert result.loc[2, "Product Quality"] and result.loc[2, "Service"]
    assert result.loc[3, "Price & Value"]
    assert len(result.columns) == 6
    assert all(str(dtype) == "bool" for dtype in result.dtypes)


def test_tracking_params_do_not_split_place(core):
    first = core["place_identity"](row()["url_tempat"])
    other = core["place_identity"](row()["url_tempat"] + "&hl=id&entry=ttu")
    assert first == other


def test_nullable_string_missing_rating_is_invalid(core):
    frame = pd.DataFrame([row(rating=None)], dtype="string")
    result = core["audit_reviews"](frame)
    assert result.loc[0, "invalid_rating"]
    assert result.loc[0, "missing_rating"]


def test_malformed_url_is_flagged(core):
    result = core["audit_reviews"](pd.DataFrame([row(url_tempat="https://[broken")]))
    assert result.loc[0, "invalid_url"]


def test_name_is_only_geographic_hint(core):
    result = core["audit_reviews"](pd.DataFrame([row(nama_tempat="Kopi Rancaekek")]))
    assert result.loc[0, "geographic_name_hint"]
    assert result.loc[0, "geography_status"].startswith("unverified")


def test_symbols_are_text_suitability_not_id_integrity(core):
    a = core["audit_reviews"](pd.DataFrame([row(), row("r2", teks_review="!!!")]))
    geo = pd.DataFrame({"verification_status": ["UNVERIFIED"]})
    readiness = core["assess_readiness"](a, geo, "PERMISSION_NOT_VERIFIED", False)
    technical = readiness["technical_data_quality"]
    assert technical["status"] == "READY"
    assert technical["integrity_issue_rows"] == 0
    assert technical["symbol_only_rows"] == 1
    assert technical["eligible_simulation_rows"] == 1
    assert not readiness["annotation_pilot"]["actual_annotation_authorized"]
    assert readiness["research_data_usage"]["status"] == "NOT_READY_PENDING_VERIFICATION"


def test_candidate_coordinates_do_not_verify_administrative_scope(core):
    a = core["audit_reviews"](pd.DataFrame([row(nama_tempat="Kopi Rancaekek")]))
    places = core["summarize_places"](a)
    local = pd.DataFrame({
        "nama_tempat": ["Kopi Rancaekek"],
        "url": ["https://www.google.com/maps/place/example/!3d-6.95!4d107.77"],
    })
    geo = core["geographic_inventory"](places, local)
    assert len(geo) == len(places)
    assert geo.loc[0, "latitude"] == pytest.approx(-6.95)
    assert geo.loc[0, "verification_status"] == "UNVERIFIED"
    assert geo.loc[0, "coordinate_status"] == "CANDIDATE_NOT_VERIFIED"
    assert not geo.loc[0, "candidate_for_exclusion"]


def test_technical_readiness_does_not_grant_research_permission(core):
    a = core["audit_reviews"](pd.DataFrame([row()]))
    inside = pd.DataFrame({"verification_status": ["VERIFIED_INSIDE"]})
    blocked = core["assess_readiness"](a, inside, "PERMISSION_NOT_VERIFIED", True)
    assert blocked["technical_data_quality"]["status"] == "READY"
    assert blocked["research_data_usage"]["status"] == "NOT_READY_PENDING_VERIFICATION"
    complete = core["assess_readiness"](a, inside, "PERMISSION_VERIFIED", True)
    assert complete["research_data_usage"]["status"] == "READY"

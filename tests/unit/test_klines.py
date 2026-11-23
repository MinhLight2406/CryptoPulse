import io
import zipfile

from cryptopulse_common import klines


def _row(open_time: int, price: float = 100.0) -> str:
    return (
        f"{open_time},{price},{price + 1},{price - 1},{price},10,{open_time + 59999},1000,5,4,400,0"
    )


def test_to_millis_handles_both_units():
    assert klines.to_millis(1_735_689_600_000) == 1_735_689_600_000  # mili giây
    assert klines.to_millis(1_735_689_600_010_866) == 1_735_689_600_010  # micro giây


def test_parse_csv_skips_header_and_normalizes_time():
    text = "open_time,open,high,low,close,volume,close_time,qv,n,tb,tq,ignore\n"
    text += _row(1_735_689_600_000_000) + "\n"
    rows = klines.parse_csv(text)
    assert len(rows) == 1
    assert rows[0]["open_time"] == 1_735_689_600_000
    assert rows[0]["trades"] == 5


def test_read_zip_text_roundtrip():
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("BTCUSDT-1m-2024-12.csv", _row(1_733_011_200_000))
    text = klines.read_zip_text(buf.getvalue())
    assert klines.parse_csv(text)[0]["open_time"] == 1_733_011_200_000


def test_quality_detects_duplicates_gaps_and_bad_prices():
    base = 1_733_011_200_000
    lines = [_row(base), _row(base + 60_000), _row(base + 60_000), _row(base + 240_000)]
    report = klines.check_quality(klines.parse_csv("\n".join(lines)))
    assert report.rows == 4
    assert report.duplicates == 1
    assert report.missing_candles == 2  # thiếu 2 nến giữa +60s và +240s
    assert report.bad_prices == 0
    assert not report.ok

    bad = klines.parse_csv(f"{base},0,1,0,0,1,{base + 59999},1,1,1,1,0")
    assert klines.check_quality(bad).bad_prices == 1


def test_quality_ok_for_clean_data():
    base = 1_733_011_200_000
    rows = klines.parse_csv("\n".join(_row(base + i * 60_000) for i in range(5)))
    report = klines.check_quality(rows)
    assert report.ok and report.missing_candles == 0

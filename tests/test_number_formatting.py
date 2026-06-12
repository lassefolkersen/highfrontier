import primitives


def test_nicefy_numbers_uses_compact_suffixes_without_scientific_notation():
    cases = {
        999: "999",
        1_000: "1K",
        1_500: "1.5K",
        1_000_000: "1M",
        1_200_000_000: "1.2B",
        2_000_000_000_000: "2T",
        1_500_000_000_000_000: "1.5Qa",
    }

    for value, expected in cases.items():
        formatted = primitives.nicefy_numbers(value)
        assert formatted == expected
        assert "e" not in formatted.lower()


def test_nicefy_numbers_handles_negative_and_decimal_values_compactly():
    assert primitives.nicefy_numbers(-1_500) == "-1.5K"
    assert primitives.nicefy_numbers(12.3456) == "12.35"
    assert primitives.nicefy_numbers(0.000123) == "0.000123"
    assert "e" not in primitives.nicefy_numbers(10**30).lower()

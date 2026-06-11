import xml.etree.ElementTree as ET
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _trade_resources():
    rows = (REPO_ROOT / "data" / "economy" / "trade resources.txt").read_text().splitlines()
    return {row.split("\t")[0] for row in rows[2:] if row.strip()}


def _technology_resources():
    root = ET.parse(REPO_ROOT / "data" / "technology" / "technology.txt").getroot()
    resources = set()
    for process in root.findall(".//abstract_process_dict"):
        for tag in ("input", "output"):
            for resource in process.findall(tag):
                if resource.text:
                    resources.add(resource.text.strip())
    return resources


def test_all_technology_inputs_and_outputs_are_declared_trade_resources():
    missing_resources = _technology_resources() - _trade_resources()

    assert missing_resources == set()

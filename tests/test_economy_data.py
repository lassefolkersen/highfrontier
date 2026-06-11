import random
import xml.etree.ElementTree as ET
from pathlib import Path

from technology import Tree


REPO_ROOT = Path(__file__).resolve().parents[1]

# Technology input/output entries should normally name stockpiled/traded
# resources. Keep explicit non-stockpiled gameplay effects here if technology
# data ever needs an effect output that should not be listed in trade resources.
NON_STOCKPILED_TECHNOLOGY_EFFECTS = set()


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


class _OneSubjectCoreTree:
    def __init__(self, subject):
        self.subject_list = [subject]

    def calculate_technology_web(self, _radial_distance):
        return {self.subject_list[0]["technology_name"]: 0}


class _FakeSolarSystem:
    message_printing = {"debugging": False}
    messages = []


def test_all_technology_inputs_and_outputs_are_trade_resources_or_documented_effects():
    missing_resources = (
        _technology_resources()
        - _trade_resources()
        - NON_STOCKPILED_TECHNOLOGY_EFFECTS
    )

    assert missing_resources == set()


def test_nuclear_fuel_technologies_generate_radioactive_waste_byproduct():
    subject = {
        "technology_name": "nuclear power",
        "productivity_multiplier": 1,
        "abstract_process_dict": {"input": ["nuclear fuel"], "output": ["power"]},
        "co_descriptors": {
            "connecting_word": [],
            "adjective": ["test"],
            "noun": ["reactor"],
        },
        "importance_function": None,
    }
    random.seed(0)
    tree = Tree(_OneSubjectCoreTree(subject), _FakeSolarSystem())

    technology_name = tree.new_iteration((5, 45))
    byproducts = tree.vertex_dict[technology_name]["input_output_dict"]["byproducts"]

    assert "radioactive waste" in byproducts

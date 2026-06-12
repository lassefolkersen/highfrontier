import os
import subprocess
import sys

from paths import asset_path, data_path, repo_root


def test_asset_and_data_paths_are_absolute_existing_files():
    assert repo_root().is_absolute()
    assert asset_path("images", "window_icon.png").is_absolute()
    assert asset_path("images", "window_icon.png").exists()
    assert data_path("planets.txt").is_absolute()
    assert data_path("planets.txt").exists()


def run_python_from_non_repo_cwd(tmp_path, code):
    env = os.environ.copy()
    env.update(
        {
            "PYTHONPATH": str(repo_root()),
            "PYGAME_HIDE_SUPPORT_PROMPT": "1",
            "SDL_VIDEODRIVER": "dummy",
            "SDL_AUDIODRIVER": "dummy",
        }
    )

    return subprocess.run(
        [sys.executable, "-c", code],
        cwd=tmp_path,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def test_global_variables_imports_from_non_repo_cwd(tmp_path):
    result = run_python_from_non_repo_cwd(
        tmp_path,
        "import global_variables; print(global_variables.courier_font.size('x'))",
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip()


def test_technology_backbone_tree_loads_from_non_repo_cwd(tmp_path):
    result = run_python_from_non_repo_cwd(
        tmp_path,
        "from technology import Backbone_Tree; tree = Backbone_Tree(); print(len(tree.subject_list))",
    )

    assert result.returncode == 0, result.stderr
    assert int(result.stdout.strip()) > 0


def test_solar_system_initializes_from_non_repo_cwd(tmp_path):
    result = run_python_from_non_repo_cwd(
        tmp_path,
        "import global_variables; from solarsystem import solarsystem; "
        "system = solarsystem(global_variables.start_date); "
        "print(len(system.planets), len(system.trade_resources))",
    )

    assert result.returncode == 0, result.stderr
    planet_count, resource_count = [int(value) for value in result.stdout.split()[-2:]]
    assert planet_count > 0
    assert resource_count > 0

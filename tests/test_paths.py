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


def test_global_variables_imports_from_non_repo_cwd(tmp_path):
    env = os.environ.copy()
    env.update(
        {
            "PYTHONPATH": str(repo_root()),
            "PYGAME_HIDE_SUPPORT_PROMPT": "1",
            "SDL_VIDEODRIVER": "dummy",
            "SDL_AUDIODRIVER": "dummy",
        }
    )

    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import global_variables; print(global_variables.courier_font.size('x'))",
        ],
        cwd=tmp_path,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip()

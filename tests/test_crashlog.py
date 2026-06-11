import logging
import threading

import pytest

import crashlog


def _read_log_files(log_dir):
    text = ""
    for log_file in log_dir.glob("*.log"):
        text += log_file.read_text()
    return text


def test_run_with_crash_logging_logs_and_reraises(tmp_path, monkeypatch):
    monkeypatch.setenv("HIGHFRONTIER_LOG_DIR", str(tmp_path))
    crashlog.configure_logging()

    def fail():
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError, match="boom"):
        crashlog.run_with_crash_logging("unit test context", fail)

    log_text = _read_log_files(tmp_path)
    assert "unit test context" in log_text
    assert "boom" in log_text
    assert "Traceback" in log_text


def test_threading_excepthook_logs_thread_exception(tmp_path, monkeypatch):
    monkeypatch.setenv("HIGHFRONTIER_LOG_DIR", str(tmp_path))
    crashlog.configure_logging()
    crashlog.install_excepthooks()

    def fail_in_thread():
        raise RuntimeError("thread boom")

    thread = threading.Thread(target=fail_in_thread, name="crashlog-test-thread")
    thread.start()
    thread.join()

    log_text = _read_log_files(tmp_path)
    assert "crashlog-test-thread" in log_text
    assert "thread boom" in log_text

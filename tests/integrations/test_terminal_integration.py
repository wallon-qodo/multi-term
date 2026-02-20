"""Tests for Terminal integration."""

import pytest
import time
from pathlib import Path
from claude_multi_terminal.integrations.terminal import (
    TerminalIntegration,
    CommandResult,
    CommandHistory,
)


@pytest.fixture
def terminal(tmp_path):
    """Create a TerminalIntegration instance."""
    return TerminalIntegration(working_dir=tmp_path)


def test_terminal_integration_init(tmp_path):
    """Test TerminalIntegration initialization."""
    terminal = TerminalIntegration(working_dir=tmp_path)
    assert terminal.working_dir == tmp_path
    assert isinstance(terminal.history, CommandHistory)


def test_execute_simple_command(terminal):
    """Test executing a simple command."""
    result = terminal.execute("echo 'Hello World'")

    assert result.success
    assert result.exit_code == 0
    assert "Hello World" in result.stdout
    assert result.command == "echo 'Hello World'"


def test_execute_failed_command(terminal):
    """Test executing a command that fails."""
    result = terminal.execute("nonexistent_command_xyz")

    assert not result.success
    assert result.exit_code != 0
    assert len(result.stderr) > 0


def test_execute_with_timeout(terminal):
    """Test command timeout."""
    result = terminal.execute("sleep 10", timeout=0.5)

    assert not result.success
    assert result.exit_code == -1
    assert "timed out" in result.stderr.lower()


def test_execute_with_input(terminal):
    """Test executing command with stdin input."""
    result = terminal.execute_with_input("cat", "Hello from stdin\n")

    assert result.success
    assert "Hello from stdin" in result.stdout


def test_execute_pipeline(terminal):
    """Test executing a command pipeline."""
    result = terminal.execute_pipeline(["echo 'test'", "tr '[:lower:]' '[:upper:]'"])

    assert result.success
    assert "TEST" in result.stdout


def test_command_history_add(terminal):
    """Test adding commands to history."""
    terminal.execute("echo 'test1'")
    terminal.execute("echo 'test2'")
    terminal.execute("echo 'test3'")

    history = terminal.history.get_all()
    assert len(history) == 3
    assert history[0].command == "echo 'test1'"


def test_command_history_recent(terminal):
    """Test getting recent commands from history."""
    for i in range(10):
        terminal.execute(f"echo 'test{i}'")

    recent = terminal.history.get_recent(count=3)
    assert len(recent) == 3
    assert recent[-1].command == "echo 'test9'"


def test_command_history_search(terminal):
    """Test searching command history."""
    terminal.execute("echo 'hello'")
    terminal.execute("ls -la")
    terminal.execute("echo 'world'")

    results = terminal.history.search("echo")
    assert len(results) == 2
    assert all("echo" in r.command for r in results)


def test_command_history_statistics(terminal):
    """Test getting history statistics."""
    terminal.execute("echo 'test1'")  # Success
    terminal.execute("echo 'test2'")  # Success
    terminal.execute("nonexistent_cmd")  # Failure

    stats = terminal.history.get_statistics()
    assert stats["total_commands"] == 3
    assert 0 < stats["success_rate"] < 100
    assert stats["average_duration"] > 0
    assert len(stats["most_common"]) > 0


def test_command_history_clear(terminal):
    """Test clearing command history."""
    terminal.execute("echo 'test'")
    assert len(terminal.history.get_all()) > 0

    terminal.history.clear()
    assert len(terminal.history.get_all()) == 0


def test_execute_async(terminal):
    """Test asynchronous command execution."""
    results = []

    def callback(result):
        results.append(result)

    thread = terminal.execute_async("echo 'async test'", callback=callback)
    thread.join(timeout=2.0)

    assert len(results) == 1
    assert results[0].success
    assert "async test" in results[0].stdout


def test_output_listener(terminal):
    """Test output listener."""
    outputs = []

    def listener(output):
        outputs.append(output)

    terminal.add_output_listener(listener)
    terminal.execute("echo 'test output'")

    assert len(outputs) > 0
    assert any("test output" in o for o in outputs)


def test_remove_output_listener(terminal):
    """Test removing output listener."""
    outputs = []

    def listener(output):
        outputs.append(output)

    terminal.add_output_listener(listener)
    terminal.execute("echo 'test1'")
    count1 = len(outputs)

    terminal.remove_output_listener(listener)
    terminal.execute("echo 'test2'")

    # Count should not increase
    assert len(outputs) == count1


def test_env_var_operations(terminal):
    """Test environment variable operations."""
    terminal.set_env_var("TEST_VAR", "test_value")
    assert terminal.get_env_var("TEST_VAR") == "test_value"

    result = terminal.execute("echo $TEST_VAR")
    assert "test_value" in result.stdout

    terminal.clear_env_vars()
    assert terminal.get_env_var("TEST_VAR") is None


def test_get_completion_suggestions(terminal):
    """Test shell completion suggestions."""
    # Execute some commands to build history
    terminal.execute("git status")
    terminal.execute("git log")
    terminal.execute("python test.py")

    suggestions = terminal.get_completion_suggestions("gi")
    assert "git" in suggestions

    suggestions = terminal.get_completion_suggestions("git")
    assert len(suggestions) > 0


def test_validate_command(terminal):
    """Test command validation."""
    # Valid command
    valid, msg = terminal.validate_command("echo 'test'")
    assert valid

    # Empty command
    valid, msg = terminal.validate_command("   ")
    assert not valid

    # Dangerous command
    valid, msg = terminal.validate_command("rm -rf /")
    assert not valid
    assert "dangerous" in msg.lower()


def test_get_command_help(terminal):
    """Test getting command help."""
    help_text = terminal.get_command_help("ls")
    assert len(help_text) > 0


def test_change_directory(terminal, tmp_path):
    """Test changing working directory."""
    new_dir = tmp_path / "subdir"
    new_dir.mkdir()

    success = terminal.change_directory(new_dir)
    assert success
    assert terminal.get_working_directory() == new_dir

    # Test invalid directory
    success = terminal.change_directory(tmp_path / "nonexistent")
    assert not success


def test_working_directory_isolation(tmp_path):
    """Test that commands execute in working directory."""
    test_dir = tmp_path / "test_dir"
    test_dir.mkdir()

    terminal = TerminalIntegration(working_dir=test_dir)

    # Create file in working directory
    result = terminal.execute("touch test_file.txt")
    assert result.success

    # Verify file exists in working directory
    assert (test_dir / "test_file.txt").exists()


def test_command_result_string_representation():
    """Test CommandResult string representation."""
    from datetime import datetime

    result = CommandResult(
        command="echo test",
        exit_code=0,
        stdout="test\n",
        stderr="",
        duration=0.1,
        timestamp=datetime.now(),
        success=True,
    )

    result_str = str(result)
    assert "SUCCESS" in result_str
    assert "echo test" in result_str
    assert "0.1" in result_str


def test_multiple_commands_in_history(terminal):
    """Test executing multiple commands and verifying history."""
    commands = ["echo 'cmd1'", "echo 'cmd2'", "echo 'cmd3'"]

    for cmd in commands:
        terminal.execute(cmd)

    history = terminal.history.get_all()
    assert len(history) == len(commands)

    for i, cmd in enumerate(commands):
        assert history[i].command == cmd


def test_history_max_size():
    """Test command history size limit."""
    history = CommandHistory(max_size=5)

    # Add more than max_size commands
    from datetime import datetime

    for i in range(10):
        result = CommandResult(
            command=f"cmd{i}",
            exit_code=0,
            stdout="",
            stderr="",
            duration=0.1,
            timestamp=datetime.now(),
            success=True,
        )
        history.add(result)

    all_history = history.get_all()
    assert len(all_history) == 5
    # Should keep most recent
    assert all_history[-1].command == "cmd9"


def test_get_history_statistics(terminal):
    """Test getting command history statistics."""
    stats = terminal.get_history_statistics()
    assert "total_commands" in stats
    assert "success_rate" in stats
    assert "average_duration" in stats
    assert "most_common" in stats

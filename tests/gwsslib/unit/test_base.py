import gwsslib
import logging
import pytest


@pytest.mark.parametrize(
    "modules",
    [
        [
            "core: missing_command, stub",
            "gsa: _Gsa__gsa_data, _Gsa__process_networks, colour_range, load_data, network_termination, networks",
        ]
    ],
)
def test_modules(modules):
    """
    Test the correct modules are being loaded. This needs to be updated as routes/commands are added.
    """
    log = logging.getLogger("unit_tests")
    commands = gwsslib.Commands(logger=log)

    result = commands.functions_list()
    for m in modules:
        assert m in result


def test_loader():
    """
    Test a couple of the core functions to make sure the invocatoin and return structure hasn't changed.
    """
    log = logging.getLogger("unit_tests")
    commands = gwsslib.Commands(logger=log)

    result = commands.run("core.stub", {})
    assert result == {"endpoint": "stub", "request": "core.stub", "success": True}
    result = commands.run("core.missing_command", {})
    assert result == {
        "endpoint": "missing_command",
        "reason": "request missing from payload - no command executed",
        "request": "core.missing_command",
        "success": False,
    }

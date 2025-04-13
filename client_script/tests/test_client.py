import pytest
import aio_pika
import asyncio
from unittest import mock
import main as client_main
from typing import List

@pytest.mark.asyncio
async def test_send_tc_and_receive_tm():
    """
    Tests the sending of a test command (TC) and the reception of a test message (TM).
    This test verifies that a test command is successfully sent and received by the client.
    """
    # Setup RabbitMQ connection
    connection = await aio_pika.connect_robust("amqp://user:pass@rabbitmq/")
    channel = await connection.channel()

    # Create temporary queue bound to 'tc'
    queue = await channel.declare_queue(exclusive=True)
    await queue.bind("tc")

    # Send test command
    test_message: bytes = b"HELLO_TEST"
    await client_main.send_tc(test_message)

    # Receive the test message
    incoming = await queue.get(timeout=5)
    assert incoming is not None, "No message received from 'tc' queue"
    assert incoming.body == test_message, f"Expected {test_message}, got {incoming.body}"
    await incoming.ack()
    await connection.close()

@pytest.mark.asyncio
async def test_get_metrics(monkeypatch):
    """
    Tests the retrieval of metrics from the modem.
    This test verifies that all expected metric endpoints are called during the get_metrics function.
    """
    calls: List[str] = []

    async def mock_get(url: str, *args, **kwargs):
        calls.append(url)
        class MockResp:
            async def json(self): return {"mock": "data"}
            async def __aenter__(self): return self
            async def __aexit__(self, *a): pass
        return MockResp()

    monkeypatch.setattr("aiohttp.ClientSession.get", mock_get)

    # Run get_metrics for a short duration
    task = asyncio.create_task(client_main.get_metrics())
    await asyncio.sleep(1)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task

    # Assert that we hit all expected metric endpoints
    expected_endpoints: List[str] = [
        "http://modem:8000/metrics/status",
        "http://modem:8000/metrics/signal_strength",
        "http://modem:8000/metrics/bit_error_rate",
        "http://modem:8000/metrics/statistics"
    ]
    for endpoint in expected_endpoints:
        assert endpoint in calls, f"{endpoint} not called"

@pytest.mark.asyncio
async def test_main_partial(monkeypatch):
    """
    Partially tests the main function by verifying that all critical components are called.
    This test ensures that the main function calls receive_tm, send_tc, and get_metrics as expected.
    """
    flags = {"received": False, "sent": False, "metrics": False}

    async def fake_receive_tm():
        flags["received"] = True
        await asyncio.sleep(0.1)

    async def fake_send_tc(data: bytes = b"TEST"):
        flags["sent"] = True

    async def fake_get_metrics():
        flags["metrics"] = True
        await asyncio.sleep(0.1)

    monkeypatch.setattr(client_main, "receive_tm", fake_receive_tm)
    monkeypatch.setattr(client_main, "get_metrics", fake_get_metrics)
    monkeypatch.setattr(client_main, "send_tc", fake_send_tc)

    await client_main.main()

    assert flags["received"], "receive_tm() was not called"
    assert flags["sent"], "send_tc() was not called"
    assert flags["metrics"], "get_metrics() was not called"

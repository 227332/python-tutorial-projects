import pytest

from src.consumer.main import process_messages


@pytest.fixture()
def good_kafka_message(mocker):
    msg = mocker.MagicMock()
    msg.value.return_value = "I am encoded".encode("utf-8")
    msg.error.return_value = None
    return msg


@pytest.fixture()
def bad_kafka_message(mocker):
    msg = mocker.MagicMock()
    msg.value.return_value = "I am not encoded"
    msg.error.return_value = None
    return msg


class TestConsumer:

    @pytest.mark.parametrize("limit", [1, 2, 3])
    def test_process_messages_limit_loop(self, mocker, good_kafka_message, limit):
        limit = 3
        mock_consumer_class = mocker.patch("src.consumer.main.Consumer")
        mock_consumer = mock_consumer_class()
        mock_consumer.poll.return_value = good_kafka_message
        process_messages(consumer=mock_consumer, limit=limit)
        assert mock_consumer.poll.call_count == limit
        assert mock_consumer.store_offsets.call_count == limit

    @pytest.mark.parametrize(
        "fail_on_error,expected_poll_call_count,expected_store_offsets_call_count",
        [(False, 3, 3), (True, 2, 1)],
    )
    def test_process_messages_error_handling(
        self,
        mocker,
        good_kafka_message,
        bad_kafka_message,
        fail_on_error,
        expected_poll_call_count,
        expected_store_offsets_call_count,
    ):
        mock_consumer_class = mocker.patch("src.consumer.main.Consumer")
        mock_consumer = mock_consumer_class()
        mock_consumer.poll.side_effect = [
            good_kafka_message,
            bad_kafka_message,
            good_kafka_message,
        ]
        limit = 3
        if fail_on_error:
            with pytest.raises(AttributeError):
                process_messages(
                    consumer=mock_consumer, limit=limit, fail_on_error=fail_on_error
                )
        else:
            # no exception should be raised here
            process_messages(
                consumer=mock_consumer, limit=limit, fail_on_error=fail_on_error
            )
        assert mock_consumer.poll.call_count == expected_poll_call_count
        assert (
            mock_consumer.store_offsets.call_count == expected_store_offsets_call_count
        )

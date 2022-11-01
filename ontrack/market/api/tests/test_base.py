from ontrack.utils.datetime import DateTimeHelper

test_date = DateTimeHelper.get_date_time(2022, 10, 20)


def assert_record_creation(result):
    assert result is not None
    records = result[0]
    assert len(records) > 0
    record_created = result[1][0]
    record_updated = result[1][1]
    assert record_created > 0
    assert record_updated == 0


def assert_record_updation(result):
    assert result is not None
    records = result[0]
    assert len(records) > 0
    record_created = result[1][0]
    record_updated = result[1][1]
    assert record_created == 0
    assert record_updated > 0

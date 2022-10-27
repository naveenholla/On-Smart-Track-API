from ontrack.market.data.endofdata import EndOfDayData
from ontrack.market.data.initialize import InitializeData
from ontrack.market.data.livedata import LiveData
from ontrack.utils.datetime import DateTimeHelper


def initilize_data(step=1):

    if step == 1:
        obj = InitializeData("nse")
        obj.load_initial_data()

    if step <= 2:
        date = DateTimeHelper.get_date_time(2022, 10, 20)
        obj = EndOfDayData("nse")
        obj.load_eod_data(date)

    if step <= 3:
        obj = LiveData("nse")
        obj.load_equity_live_data()

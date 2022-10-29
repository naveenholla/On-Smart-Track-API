from .datetime import DateTimeHelper


class StringHelper:
    @staticmethod
    def format_url(url_record, date):
        url = DateTimeHelper.datetime_to_str(date, f"{url_record['url']}")
        if "args" in url_record:
            index = 0
            for arg in url_record["args"]:
                if "format" in arg:
                    value = DateTimeHelper.datetime_to_str(date, arg["format"])
                    if "is_upper" in arg and bool(arg["is_upper"]):
                        value = value.upper()
                    url = url.replace("{" + str(index) + "}", value)
                    index += 1
        return url

    # Creating a function which will remove extra leading
    # and tailing whitespace from the data.
    # pass dataframe as a parameter here
    @staticmethod
    def whitespace_remover(dataframe):
        # iterating over the columns
        for i in dataframe.columns:
            # checking datatype of each columns
            if dataframe[i].dtype == "object":
                # applying strip function on column
                dataframe[i] = dataframe[i].map(str.strip)
            else:
                # if condn. is False then it will do nothing.
                pass

"""Wrapper around the pageviewapi, from Wikipedia."""

import datetime as dt
import logging
import pageviewapi
import pandas as pd

logging.getLogger().setLevel(logging.INFO)


class ZeroOrDataNotLoadedException(Exception):
    """Raised for 404 Error

    404 may happen when there is no data or data has not been filled yet.
    https://wikitech.wikimedia.org/wiki/Analytics/PageviewAPI#Gotchas
    """


class ThrottlingException(Exception):
    """Raise for 429 Error

    Client doing too many request may be subject to throttling.
    Requests in cache are not throttled (throttling is done at storage layer).
    https://wikitech.wikimedia.org/wiki/Analytics/PageviewAPI#Gotchas
    """


class WikiAnalyzer:
    """Main class."""

    def __init__(self, language):
        self.language = language  # e.g. pt or en
        if self.language != "pt":
            logging.error("Error: Only portuguese available. Setting up to portuguese")
            self.language = "pt"

    def __clean_data(self, df_input):
        """Minor data enhancements, removes generic Wikipages and re-applies ranking accordingly."""

        df_output = df_input.copy()

        # add portuguese url
        df_output["url"] = df_output["article"].apply(
            lambda x: "https://pt.wikipedia.org/wiki/" + x
        )

        # string treatments and removal of wikipedia's internal pages
        df_output["article"] = df_output["article"].str.replace("_", " ")
        df_output = df_output[
            ~df_output["article"].str.contains("Wikipédia:|Especial:Pesquisar")
        ].reset_index(drop=True)

        # re-ranking after page removal
        df_output["rank"] = df_output.index + 1

        # returning only top10
        return df_output[:10]

    def get_data_for_date(self, date_input, max_results) -> pd.DataFrame:
        """For a given date, get data."""

        year = date_input.year
        month = str(date_input.month).zfill(2)
        day = str(date_input.day).zfill(2)

        if max_results < 1:
            max_results = 1
        elif max_results > 1000:
            max_results = 1000

        # request data
        try:
            raw = pageviewapi.top("pt.wikipedia", year, month, day, access="all-access")
        except ZeroOrDataNotLoadedException:
            logging.exception("No data, or data not filled yet.")
            return None
        except ThrottlingException:
            logging.exception("Too many requests.")
            return None

        # load into dataframe
        df_output = pd.DataFrame(raw["items"][0]["articles"])

        # add date
        df_output["date"] = date_input.strftime("%Y-%m-%d")

        # clean
        df_output = self.__clean_data(df_output)

        # max results
        df_output = df_output[:max_results]

        return df_output

    def get_historical_data(self, date_range, max_results_per_day) -> pd.DataFrame:
        """Collects all data for a given date range, using function previously defined.
        Default: 2024.
        """
        logging.info("started getting historical data for 2024.")

        frames = []

        for date in date_range:
            raw = self.get_data_for_date(date, max_results_per_day)
            clean = self.__clean_data(raw)
            frames.append(clean)

        df_output = pd.concat(frames).reset_index(drop=True)

        logging.info("finished getting historical data for 2024.")

        return df_output


'''def main():
    """Main function."""

    DATE_RANGE = pd.date_range("2024-02-01", "2024-02-16")
    MAX_RESULTS = 5

    wa = WikiAnalyzer("pt")
    df = wa.get_historical_data(DATE_RANGE, MAX_RESULTS)
    # df = wa.get_data_for_date(DATE_RANGE[0], MAX_RESULTS)
    print(df)


if __name__ == "__main__":
    main()
'''

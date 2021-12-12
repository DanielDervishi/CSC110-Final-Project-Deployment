"""
Processes the csv for faster computations.
"""
from crime_data import CrimeData
import pandas as pd
import datetime


def build_crime_data_class(path: str, col_num_crime_type: int,
                           col_num_year: int, col_num_month: int, col_num_neighbourhood: int,
                           reading_processed_data: bool, col_num_occurrences=None,
                           start_year_month=None, end_year_month=None) -> CrimeData:
    """
    Converts the data from the dataframe to the desired format using the a CrimeData object.

    Only to be used with the pre-processed-crime-data-vancouver and crime_data_vancouver datasets.

    Parameters:
        - path: specifies which csv file where data will be read
        - col_num_crime_type: specifies the column of the dataframe in which crime type is stored
        - col_num_year: specifies the column of the dataframe in which year is stored
        - col_num_month: specifies the column of the dataframe in which month is stored
        - col_num_neighbourhood: specifies the column of the dataframe in which neighbourhood is stored
        - col_num_occurrences: specifies the column of the dataframe in which number of occurrences is stored
        (if applicable), defaults to 1 otherwise.
        - start_year_month - end_year_month, range in which data will stored (should only be specified when
        processing raw csv)
        - reading_processed_csv: True if you are reading a processed csv and false otherwise.
    """

    pre_processed_data = pd.read_csv(path)
    post_processing_data = CrimeData()

    # useful for first pass through when building the processed data
    if not reading_processed_data:
        for _, row in pre_processed_data.iterrows():
            if check_date_in_range(start_year_month, end_year_month, (row[col_num_year], row[col_num_month])):
                post_processing_data.increment_crime(row[col_num_crime_type], row[col_num_neighbourhood],
                                                     row[col_num_year], row[col_num_month], 1)
        post_processing_data.fill_gaps(start_year_month, end_year_month)

    # useful for second pass through when reading processed data
    else:
        for _, row in pre_processed_data.iterrows():
            post_processing_data.increment_crime(row[col_num_crime_type], row[col_num_neighbourhood],
                                                 row[col_num_year], row[col_num_month], row[col_num_occurrences])
    return post_processing_data


def create_csv(crime_data_class: CrimeData) -> None:
    """
    Creates new csv by first converting the data into the correct format and then using methods
    from the pandas module.

    Code run in console to create the new dataframe
    >>> df = build_crime_data_class('./pre-processed-crime-data-vancouver.csv', \
    col_num_crime_type= 0, col_num_year = 1, col_num_month = 2, col_num_neighbourhood = 7, \
    reading_processed_data=False, start_year_month=(2003,1), end_year_month=(2021,11))
    >>> create_csv(df)

    Parameters:
        crime_data_class: CrimeData object with data that we wish to convert to csv
    """

    # create a dictionary to properly format data before converting it to csv
    formatted_dict = {'crime_type': [], 'neighbourhood': [], 'year': [], 'month': [], 'count': []}
    for crime in crime_data_class.crime_occurrences:
        for neighbourhood in crime_data_class.crime_occurrences[crime]:
            for year in crime_data_class.crime_occurrences[crime][neighbourhood].occurrences:
                for month in crime_data_class.crime_occurrences[crime][neighbourhood].occurrences[year]:
                    count = crime_data_class.crime_occurrences[crime][neighbourhood].occurrences[year][month]
                    if isinstance(crime, str) and isinstance(neighbourhood, str) and isinstance(year, int)\
                            and isinstance(month, int) and isinstance(count, int):
                        formatted_dict['crime_type'].append(crime)
                        formatted_dict['neighbourhood'].append(neighbourhood)
                        formatted_dict['year'].append(year)
                        formatted_dict['month'].append(month)
                        formatted_dict['count'].append(count)

    # convert the dictionary to a dataframe
    dataframe = pd.DataFrame(formatted_dict)

    # convert the dataframe to a csv with this path
    dataframe.to_csv('./crime_data_vancouver.csv', index=False)


def get_vancouver_data() -> CrimeData:
    """
    Return data formatted using CrimeData from crime_data_vancouver.csv.
    """
    return build_crime_data_class(path='./crime_data_vancouver.csv', col_num_crime_type=0, col_num_year=2,
                                  col_num_month=3, col_num_neighbourhood=1, col_num_occurrences=4,
                                  reading_processed_data=True)


def check_date_in_range(start_year_month: tuple[int, int],
                        end_year_month: tuple[int, int], date_year_month: tuple[int, int]) -> bool:
    """Checks if a date is between start_year_month and end_year_month inclusive
    """
    start = datetime.date(year=start_year_month[0], month=start_year_month[1], day=1)
    end = datetime.date(year=end_year_month[0], month=end_year_month[1], day=1)
    date = datetime.date(year=date_year_month[0], month=date_year_month[1], day=1)
    return start <= date <= end

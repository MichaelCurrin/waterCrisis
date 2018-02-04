#!/usr/bin/env python3
"""Parse a dam CSV.

Read in a CSV of data around dam levels, clean the data and convert it
to a dictionary. This is written out to a CSV if running as the main script.
"""
import csv
import datetime

from config import FILE_PATH, ENCODING, OUT_PATH, CAPACITY


def parse_to_float(value):
    """Expect a cell value as a string an attempt to cast to a float.

    The logic handles known edgecases in the data (Excel formulae errors
    or negative values) and returns a None value to represent an invalid value.
    A space for a thousands separator is removed.
    """
    if value and value != '#VALUE!' and not value.startswith("-"):
        return float(value.replace(" ", ""))
    else:
        return None


def extract_storage_values(row):
    """Convert a row of CSV dam data into a dict of values and calculated sums.

    Read in and process the date column and storage values for specific
    dams (measured in Megalitres). Ignore the percent values.

    Ignore the big six storage value and rather calculate big six, small dams
    and total for all dams. For those calculated sums, any None value will
    cause an error and this is handled by setting the sum to None. Since
    a total is not valid if one of the elements is missing.

    @param row: Tuple of CSV row values, including a date in the first
        column followed by metrics for Western Cape dams.

    @return: Dict of parsed and cleaned values. Includes a datetime.date object
        and dam storage levels for that date, as floats or None values.
    """
    try:
        date = datetime.datetime.strptime(row[0], "%d-%b-%y").date()
    except ValueError:
        # Handle irregularities in date values. The sequence of values for
        # the month of May in 2017 follows a format with a forward slash
        # and has inconsistent years in place of 2017. In one row, the
        # month appears incorrectly as August.
        date = datetime.datetime.strptime(row[0], "%d/%m/%Y").date()
        date = date.replace(month=5, year=2017)

    wemmershoek_storage = parse_to_float(row[2])
    steensbras_lower_storage = parse_to_float(row[6])
    steensbras_upper_storage = parse_to_float(row[10])
    voelvlei_storage = parse_to_float(row[14])
    hely_hutchison_storage = parse_to_float(row[18])
    woodhead_storage = parse_to_float(row[22])
    victoria_storage = parse_to_float(row[26])
    alexandra_storage = parse_to_float(row[30])
    de_villiers_storage = parse_to_float(row[34])
    kleinplaats_storage = parse_to_float(row[38])
    lewis_gay_storage = parse_to_float(row[42])
    theewaterskloof_storage = parse_to_float(row[46])
    berg_river_storage = parse_to_float(row[50])
    land_en_zeezicht_storage = parse_to_float(row[58])

    # This dam is special case where source data is null for the first few
    # years, then starts (at a value less than 100 Ml). A zero is used is place
    # of None, to ensure there is still a sum that be calculated for small
    # dams for the first few years.
    if land_en_zeezicht_storage is None:
        land_en_zeezicht_storage = 0

    try:
        big_six_storage = sum(
            theewaterskloof_storage, wemmershoek_storage,
            steensbras_lower_storage, steensbras_upper_storage,
            voelvlei_storage, berg_river_storage
        )
    except TypeError:
        big_six_storage = None

    try:
        small_storage = sum(
            hely_hutchison_storage,
            woodhead_storage,
            victoria_storage,
            alexandra_storage,
            de_villiers_storage,
            kleinplaats_storage,
            lewis_gay_storage,
            land_en_zeezicht_storage
        )
    except TypeError:
        small_storage = None

    try:
        all_storage = big_six_storage + small_storage
    except TypeError:
        all_storage = None

    return {
        'Date': date,
        'Wemmershoek': wemmershoek_storage,
        'Steensbras Lower': steensbras_lower_storage,
        'Steenbras Upper': steensbras_upper_storage,
        'Voëlvlei': voelvlei_storage,
        'Hely-Hutchinson': hely_hutchison_storage,
        'Woodhead': woodhead_storage,
        'Victoria': victoria_storage,
        'De Villiers': de_villiers_storage,
        'Kleinplaats': kleinplaats_storage,
        'Lewis Gay': lewis_gay_storage,
        'Theewaterskloof': theewaterskloof_storage,
        'Berg River': berg_river_storage,
        'Land-en-Zeezicht': land_en_zeezicht_storage,
        'Small Dams': small_storage,
        'Big Six Dams': big_six_storage,
        'All Dams': all_storage
    }


def calc_percent_storage(row_dict):
    """Calculate relative volume of dams and return in a new dict object.

    Expects date and absolute volume by day for dams. Adds calculated
    value for relative volume of the dam, using the absolute volume and
    the known full capacity from the config file.

    @param row_dict: Dict with keys as set in the output dict of the
        extract_storage_values function.

    @return out_dict: A new dict object. Includes the input dict's date
        and two values for each dam, to cover the provided storage value
        and the calculated relative volume (or None if storage is None).
    """
    out_dict = {'Date': row_dict.pop('Date')}
    for k, v in row_dict.items():
        storage_key = "{} Storage".format(k)
        percent_key = "{} Percent".format(k)

        out_dict[storage_key] = v
        out_dict[percent_key] = v / CAPACITY[k] if v is not None else None

    return out_dict

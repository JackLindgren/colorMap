#!/usr/bin/python

from colour import Color
import csv
import xml.etree.ElementTree as ET


class ColorMap(object):
    def __init__(self, states_csv, increment=False, truncate=False, low=None, medium=None, high=None, output=None):
        self.colors_needed = 0
        self.colors = []

        self.output_filename = output or "newMap.svg"

        self.increment = increment
        self.truncate = truncate
        self.low = low
        self.medium = medium
        self.high = high

        self.csv = states_csv

        # get the values from the CSV
        self.values_dict = self._get_state_values_dict()

        # get the states and values that we're working with
        self.states = self.values_dict.keys()
        self.values = self.values_dict.values()

        # determine which countries we're working with
        self.is_us_map = self._is_usa()
        self.is_canada_map = self._is_canada()

        # sets the colors
        self._get_colors_needed()

        self._get_colors()

        self.color_matches = None
        self._match_values_to_colors()

    def _get_state_values_dict(self):
        """
        Takes a CSV and returns a dict of states with their values from the CSV
        e.g., {"CA": 23, "TX": 45}
        """
        # create a dictionary of {State: Value}
        state_value_dict = {}

        # all {Name: Abbreviation} pairs for US and Canada in one dict
        states_by_name = {"Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA",
                          "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE", "District of Columbia": "DC",
                          "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL",
                          "Indiana": "IN", "Iowa": "IA", "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA",
                          "Maine": "ME", "Maryland": "MD", "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN",
                          "Mississippi": "MS", "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV",
                          "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY",
                          "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK", "Oregon": "OR",
                          "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC", "South Dakota": "SD",
                          "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT", "Virginia": "VA",
                          "Washington": "WA", "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY",
                          "Ontario": "ON", "Quebec": "QC", "Nova Scotia": "NS", "New Brunswick": "NB", "Manitoba": "MB",
                          "British Columbia": "BC", "Prince Edward Island": "PE", "Saskatchewan": "SK", "Alberta": "AB",
                          "Newfoundland and Labrador": "NL", "Northwest Territories": "NT", "Yukon": "YT",
                          "Nunavut": "NU"}

        with open(self.csv) as input_csv:
            reader = csv.DictReader(input_csv)
            for row in reader:
                if row["region"] in states_by_name:
                    # file uses the full name, adjust to the abbreviation
                    abbrev = states_by_name[row["region"]]
                elif row["region"] in states_by_name.values():
                    # file already using the abbreviation
                    abbrev = row["territory"]
                else:
                    # drop any regions that don't match a US state or Canadian province/territory
                    continue
                state_value_dict[abbrev] = row["value"]

        return state_value_dict

    def _is_usa(self):
        """
        Returns True if the state list contains any US states
        Otherwise returns False
        """
        us_states = ["WA", "WI", "WV", "FL", "WY", "NH", "NJ", "NM", "NC", "ND", "NE", "NY", "RI", "NV", "CO", "CA",
                     "GA", "CT", "OK", "OH", "KS", "SC", "KY", "OR", "SD", "DE", "DC", "HI", "TX", "LA", "TN", "PA",
                     "VA", "AK", "AL", "AR", "VT", "IL", "IN", "IA", "AZ", "ID", "ME", "MD", "MA", "UT", "MO", "MN",
                     "MI", "MT", "MS"]
        for place in self.states:
            if place in us_states:
                return True
        return False

    def _is_canada(self):
        """
        Returns True if the state list contains any canadian provinces or territories
        Otherwise returns False
        """
        canadian_provinces = ["ON", "QC", "NS", "NB", "MB", "BC", "PE", "SK", "AB", "NL", "NT", "YT", "NU"]
        for place in self.states:
            if place in canadian_provinces:
                return True
        return False

    def _get_colors_needed(self):
        if self.increment or self.truncate:
            self.colors_needed = (int(max(self.values)) - int(min(self.values))) + 1
        else:
            self.colors_needed = len(list(set(self.values)))

    def _get_colors(self):
        # default values
        first_color = Color("#F4EB37")
        middle_color = Color("#FFA500")
        last_color = Color("#8B0000")

        if self.colors_needed % 2 == 0:
            self.colors_needed += 2
        else:
            self.colors_needed += 1

        # if the user has specified both "low" and "high" values, use those
        # if they have specified one or the other, but not both, we will use the defaults
        # if invalid values have been given for any of the, default will be used instead
        if self.low and self.high:
            try:
                first_color = Color(self.low)
            except ValueError:
                first_color = Color("#F4EB37")
            try:
                last_color = Color(self.high)
            except ValueError:
                last_color = Color("#8B0000")
            if self.medium:
                try:
                    middle_color = Color(self.medium)
                except ValueError:
                    middle_color = Color("#FFA500")
            else:
                middle_color = None

        # TODO: problem here
        if middle_color:
            colors_one = list(first_color.range_to(middle_color, int(self.colors_needed / 2)))
            colors_two = list(middle_color.range_to(last_color, int(self.colors_needed / 2)))
        else:
            colors_one = list(first_color.range_to(last_color, int(self.colors_needed)))
            colors_two = []
        all_colors = []
        for color in colors_one:
            all_colors.append(color.hex)
        for color in colors_two[1:]:
            all_colors.append(color.hex)
        self.colors = all_colors

    def _match_values_to_colors(self):
        value_range = list(set(self.values))
        if self.increment:
            value_range = range(int(min(self.values)), int(max(self.values)) + 1)

        color_matches = {}
        i = 0
        while i < len(value_range):
            color_matches[value_range[i]] = self.colors[i]
            i += 1
        self.color_matches = color_matches

    def color_states(self):
        """
        takes the {Value: Color} and {State: Value} dicts
        and colors in the map
        """
        # check to see if it's US, Canada, or both
        # loop through the states in the map and assign corresponding values from the dictionaries
        if self.is_us_map and not self.is_canada_map:
            tree = ET.parse("USMap.svg")
            root = tree.getroot()
            for child in root:
                try:
                    if child.attrib["id"] == "outlines":
                        for state in child:
                            try:
                                # find the state's value
                                state_value = self.values_dict[state.attrib["id"]]
                                # find the corresponding color
                                state_color = self.color_matches[state_value]
                                # write that color to the shape's space on the map
                                state.attrib["fill"] = state_color
                            except KeyError:
                                continue
                except KeyError:
                    continue
        elif self.is_canada_map and not self.is_us_map:
            tree = ET.parse("CanadaMap.svg")
            root = tree.getroot()
            for child in root:
                if child.attrib["id"] == "Canada":
                    for province in child:
                        try:
                            prov_value = self.values_dict[province.attrib["id"]]
                            prov_color = self.color_matches[prov_value]
                            province.attrib["fill"] = prov_color
                        except KeyError:
                            continue
        elif self.is_us_map and self.is_canada_map:
            tree = ET.parse("USCanadaMap.svg")
            root = tree.getroot()
            for child in root:
                if child.attrib["id"] == "US-CAN":
                    for country in child:
                        for state in country:
                            try:
                                state_value = self.values_dict[state.attrib["id"]]
                                state_color = self.color_matches[state_value]
                                state.attrib["fill"] = state_color
                            except KeyError:
                                continue
        else:
            return

        # write the new XML to the output file
        output = ET.tostring(root).decode("utf-8")
        f = open(self.output_filename, "w")
        f.write(output)
        f.close()

#!/usr/bin/python

import argparse
from colour import Color
import csv
import re
import xml.etree.ElementTree as ET

parser = argparse.ArgumentParser()
parser.add_argument('input_file', metavar='N', type=str, nargs=1, help='an input filename')
parser.add_argument('--increment', help="color range assigned incrementally for full range in input value set", action="store_true")
parser.add_argument('--truncate', help="color range assigned incrementally, but only for values in input set", action="store_true")
parser.add_argument('--outputfile', help="specify an SVG output filename")
parser.add_argument('--low', help="specify the 'low' color in gradient either as color name (e.g. 'red') or hex value")
parser.add_argument('--high', help="specify the 'high' color in gradient")
parser.add_argument('--medium', help="specify the 'medium' color in the gradient")
args = parser.parse_args()

statesByAbbrev = {"AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware", "DC": "District of Columbia", "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland", "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi", "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York", "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina", "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah", "VT": "Vermont", "VA": "Virginia", "WA": "Washington", "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming"}

provincesByAbbrev = {"ON": "Ontario", "QC": "Quebec", "NS": "Nova Scotia", "NB": "New Brunswick", "MB":"Manitoba", "BC":"British Columbia", "PE":"Prince Edward Island", "SK":"Saskatchewan", "AB":"Alberta", "NL":"Newfoundland and Labrador", "NT":"Northwest Territories", "YT":"Yukon", "NU":"Nunavut"}

def getColors(numberNeeded, args):
	"""
	takes the number needed and returns a list of hex color values
	"""
	if(numberNeeded % 2 == 0):
		numberNeeded += 2
	else:
		numberNeeded += 1

	# if the user has specified both 'low' and 'high' values, use those
	# if they have specified one or the other, but not both, we will use the defaults
	if args.low and args.high:
		firstColor = Color(args.low)
		lastColor  = Color(args.high)
		if args.medium:
			middleColor = Color(args.medium)
		else:
			middleColor = None
	else:
		firstColor  = Color("#F4EB37")
		middleColor = Color("#FFA500")
		lastColor   = Color("#8B0000")

	if middleColor:
		colors1 = list( firstColor.range_to(middleColor, (numberNeeded / 2)))
		colors2 = list(middleColor.range_to(lastColor,   (numberNeeded / 2)))
	else:
		colors1 = list(firstColor.range_to(lastColor, numberNeeded))
		colors2 = []

	allColors = []
	for color in colors1:
		allColors.append(color.hex)
	for color in colors2[1:]:
		allColors.append(color.hex)
	return allColors

def matchValuesToColors(values, colors):
	"""
	takes a list of values and a list of colors
	returns a dictionary of color matches {Value: Color}
	"""
	colorMatches = {}
	i = 0
	while i < len(values):
		colorMatches[values[i]] = colors[i]
		i += 1
	return colorMatches

def getStateValuesDict(inputCSV):
	"""
	Takes a CSV and returns a dict of states with their values from the CSV
	e.g. {"CA": 23, "TX": 45}
	"""

	# create a dictionary of {State: Value}
	stateValueDict = {}

	# all {Name: Abbreviation} pairs for US and Canada in one dict
	statesByName = {"Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA", "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE", "District of Columbia": "DC", "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD", "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS", "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY", "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC", "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT", "Virginia": "VA", "Washington": "WA", "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY", "Ontario": "ON", "Quebec":"QC", "Nova Scotia": "NS", "New Brunswick":"NB", "Manitoba":"MB", "British Columbia":"BC", "Prince Edward Island":"PE", "Saskatchewan":"SK", "Alberta":"AB", "Newfoundland and Labrador":"NL", "Northwest Territories":"NT", "Yukon":"YT", "Nunavut":"NU"}

	with open(inputCSV) as myCSV:
		for line in myCSV:
			# clear whitespace
			line = re.sub(' ', '', line)
			# clear special characters
			line = re.sub('[^0-9a-zA-Z.,]', '', line)
			# split on the comma
			line = line.split(',')
			# only proceed if it's a state or province name or abbreviation
			if line[0] in statesByName.keys() or line[0] in statesByName.values():
				if len(line[0]) > 2:
					stateValueDict[statesByName[line[0]]] = float(line[1])
				else:
					stateValueDict[line[0]] = float(line[1])
				
	myCSV.close()

	return stateValueDict

def colorStates(colorDict, stateValueDict, outFile, needUSMap, needCanMap):
	"""
	takes the {Value: Color} and {State: Value} dicts
	and colors in the map
	"""
	# check to see if it's US, Canada, or both
	# loop through the states in the map and assign corresponding values from the dictionaries

	# US map
	if (needUSMap == True)  and (needCanMap == False):
		tree = ET.parse('USMap.svg')
		root = tree.getroot()
		for child in root:
			try:
				if child.attrib['id'] == "outlines":
					for state in child:
						try:
							# find the state's value
							stateValue = stateValueDict[state.attrib["id"]]
							# find the corresponding color
							stateColor = colorDict[stateValue]
							# write that color to the shape's space on the map
							state.attrib["fill"] = stateColor
						except KeyError:
							continue
			except KeyError:
				continue

	# Canadian map
	elif (needUSMap == False) and (needCanMap == True):
		tree = ET.parse('CanadaMap.svg')
		root = tree.getroot()
		for child in root:
			if child.attrib['id'] == 'Canada':
				for province in child:
					try:
						provValue = stateValueDict[province.attrib['id']]
						provColor = colorDict[provValue]
						province.attrib["fill"] = provColor
					except KeyError:
						continue

	# US + Canada map
	elif (needUSMap == True) and (needCanMap == True):
		tree = ET.parse('USCanadaMap.svg')
		root = tree.getroot()
		for child in root:
			if child.attrib['id'] == "US-CAN":
				for country in child:
					for state in country:
						try:
							stateValue = stateValueDict[state.attrib['id']]
							stateColor = colorDict[stateValue]
							state.attrib["fill"] = stateColor
						except KeyError:
							continue

	# write the new XML to the output file
	output = ET.tostring(root)
	f = open(outFile, 'w')
	f.write(output)
	f.close()

def isAmerica(potentialStates):
	"""
	Returns True if the state list contains any US states
	Otherwise returns False
	"""
	USstates = ['WA', 'WI', 'WV', 'FL', 'WY', 'NH', 'NJ', 'NM', 'NC', 'ND', 'NE', 'NY', 'RI', 'NV', 'CO', 'CA', 'GA', 'CT', 'OK', 'OH', 'KS', 'SC', 'KY', 'OR', 'SD', 'DE', 'DC', 'HI', 'TX', 'LA', 'TN', 'PA', 'VA', 'AK', 'AL', 'AR', 'VT', 'IL', 'IN', 'IA', 'AZ', 'ID', 'ME', 'MD', 'MA', 'UT', 'MO', 'MN', 'MI', 'MT', 'MS']
	for place in potentialStates:
		if place in USstates:
			return True
	return False

def isCanada(potentialProvinces):
	"""
	Returns True if the state list contains any canadian provinces or territories
	Otherwise returns False
	"""
	canadianProvinces = ["ON", "QC", "NS", "NB", "MB", "BC", "PE", "SK", "AB", "NL", "NT", "YT", "NU"]
	for place in potentialProvinces:
		if place in canadianProvinces:
			return True
	return False

stateValueDict = getStateValuesDict(args.input_file[0])

allStates = stateValueDict.keys()
allValues = stateValueDict.values()

# determine whether we need a US map, a Canadian map, or both
needUSMap  = isAmerica(allStates)
needCanMap = isCanada(allStates)

# get the unique values in our CSV
uniqValues = list(set(allValues))
uniqValues.sort()

# figure out how many colors we need
# if they choose to "increment" 
# then we'll get as many color values as there are ints between min and max
# otherwise, we'll only get as many color values as there 
#    are UNIQUE values in the CSV
if args.increment or args.truncate:
	colorsNeeded = (max(allValues) - min(allValues)) + 1
else:
	colorsNeeded = len(uniqValues)

# get the color palette
ourColors = getColors(colorsNeeded, args)

# get the color dictionary
if args.increment:
	valueRange = range(min(allValues), max(allValues) + 1)
	colorDict = matchValuesToColors(valueRange, ourColors)
else:
	colorDict = matchValuesToColors(uniqValues, ourColors)

if args.outputfile:
	outputCSV = args.outputfile
else:
	outputCSV = "newMap.svg"

colorStates(colorDict, stateValueDict, outputCSV, needUSMap, needCanMap)
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from willie import module

from suds import *
from suds.client import Client
from lxml import etree


def listToString(l):
	r = ""
	for e in l:
		r = r + str(e).rjust(3)
	return r

def print_usage(bot):
	bot.say ("Usage: .snow <location> <symptomgroup>")
	bot.say ("    location: TROMS, FINNMARK or NORDLAND")
	bot.say ("    symptomgroup: Luftvei or Gastrointestinalt")
	exit()

def printTitle(bot):
	
	n = 4
	r = "Week number relative to this week (0)".ljust(40)
	for i in range(0,n):
		if i == 3:
			c = str(3-i)
		else:
			c = "-"+ str(3-i)
		r = r + c.rjust(3)
	bot.say (r)

def printSymptomGroupTree():
	symptomGroupTree = client.service.getSymptomGroupTree()
	bot.say (symptomGroupTree)

def printAgentValues(bot, client, url, county, symptomgroup):

	if symptomgroup is None or county is None:
		print_usage(bot)

	symptomgroup = symptomgroup.capitalize().strip()
	county = county.upper().strip()

	if county == "TROMS":
		county = "19_ALL"
		countycode = "19"
	elif county == "FINNMARK":
		county = "20_ALL"
		countycode = "20"
	elif county == "NORDLAND":
		county = "18_ALL"
		countycode = "18"
	else:
		print_usage(bot)
		return 

	if symptomgroup != "Luftvei" and symptomgroup != "Gastrointestinalt":
		print_usage(bot)

	updated = client.service.getLastImportDate()
	report = client.service.getReport(county, symptomgroup)
	root = etree.fromstring(report[38:])
	printTitle(bot)
	a = root.xpath("/ResultSet/items/item/areas/area[@code="+countycode+"]/onLocation[@type='requester']/AggregatedCollection/DataSet/dataResults/result")
	for b in a:
		i = 0
		for c in list(b):
			if i == 0:
				# Label
				r = c.text.split("=")[1]
				if r == "Generell":
					r = "Influensa A (Generell)"
				r = r + ": "
				r = r.ljust(40)
			else:
				values = c.text.split(",")[-4:] # last 4 weeks
				#r = r + c.text
				r = r + listToString(values)
			i = i + 1
		bot.say (r)
	bot.say("Data last updated: " + updated)


@module.commands('snow')
def snow(bot, trigger):
	try:
		url = 'http://snow.telemed.no/axis2/services/ReportService?wsdl'
		client = Client(url)
		printAgentValues(bot, client, url, trigger.group(3), trigger.group(4))
 	except Exception, e:
		print (e)

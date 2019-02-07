import requests
import json
import time

class RNVStartInfoApi:
    baseurl = "http://rnv.the-agent-factory.de:8080/easygo2/api"

    API_TOKEN = ""

    headers = {}

    def getupdate(self, timestationpackage, timelinepackage, timeunused="2011-11-11+11:11", regionid="1"):
        r"""Sends an update request
        :param timestationpackage: time from time package when station package was updated/retrieved
            format: YYYY-MM-DD+HH:mm
        :param timelinepackage: time from time package when line package was updated/retrieved
            format: YYYY-MM-DD+HH:mm
        :param timeunused: (optional) this param is unused (in v1.11) but still required.
            format: YYYY-MM-DD+HH:mm
            per default 2011-11-11+11:11 is used
        :return: json response Update
        :rtype: json dict"""

        timestationpackage = time.strftime("%Y-%m-%d+%H:%M", timestationpackage)
        timelinepackage = time.strftime("%Y-%m-%d+%H:%M", timelinepackage)

        params = "regionID=" + regionid + "&time=" +\
                 timestationpackage + "$" + timelinepackage + "$" + timeunused

        basereq = "/update"
        r = requests.get(self.baseurl + basereq, params=params, headers=self.headers)

        return json.loads(r.text)

    def getstationpackage(self, regionid="1"):
        r"""Request the stationpackage
        :param regionid: (optional) in v1.11 only regionid = 1 is available
        :return: json response StationPackage
        :rtype: json dict"""

        if regionid == "":
            raise Exception("Not a valid regionid.")

        basereq = "/regions/rnv/modules/stations/packages/"
        basereq += str(regionid)

        r = requests.get(self.baseurl + basereq, headers=self.headers)

        return json.loads(r.text)

    def getlinepackage(self):
        r"""Request the linepackage
        :return: json response LineJourney
        :rtype: json dict"""

        basereq = "/regions/rnv/modules/lines/allJourney"
        r = requests.get(self.baseurl + basereq, headers=self.headers)

        return json.loads(r.text)

    def getalllines(self):
        r"""Request info for all lines
        :return: json response Line
        :rtype: json dict"""

        basereq = "/regions/rnv/modules/lines/all"
        r = requests.get(self.baseurl + basereq, headers=self.headers)

        return json.loads(r.text)

    def getstationmonitor(self, hafas="", timepoint="null", mode="DEP", poles="", needplatformdetail="true"):
        r"""Request info about a station, eg. arrival or depature times
        :param hafas: station id
        :param time: from time package list information from timepoint
        :param mode: default is DEP for departures, ARR is for arrival
        :param poles: comma separated list of poles, to restrict information about the station
        :param needplatformdetail: true or false, on true prints the poles at the output
        :return: json response Journey
        :rtype: json dict"""

        if hafas == "" or mode == "" or needplatformdetail == "":
            raise Exception("Not a valid hafas or mode or needplatfromdetail.")

        if timepoint != "null":
            timepoint = time.strftime("%Y-%m-%d+%H:%M", timepoint)

        params = "hafasID=" + str(hafas) + "&time=" + timepoint + \
                 "&mode=" + mode + \
                 "&needPlatformDetail=" + needplatformdetail

        if poles != "":
            params += "&poles=" + poles

        basereq = "/regions/rnv/modules/stationmonitor/element"
        r = requests.get(self.baseurl + basereq, headers=self.headers, params=params)

        return json.loads(r.text)

    def getnextstops(self, lineid="", timepoint="", tourtype="", tourid="", hafas="", stopindex="0"):
        r"""Similar to getlinepackage, but more specific for a single line
        :param lineid: id of the specific line
        :param timepoint: time from time package
        :param tourtype: "452" or "454" type can be extracted from stationmonitor attribute kindOfTour
        :param tourid: id of the tour
        :param hafas: station id
        :param stopindex: (optional) default is 0, display all stops from the beginning of the route
        other value x -> skip the first x stops
        :return: json response LineJourney
        :rtype: json dict"""

        if lineid == "" or timepoint == "" or tourtype == "" or tourid == "" or hafas == "" or stopindex == "":
            raise Exception("Not a valid lineid or timepoint or tourtype or tourid or hafas or stopindex.")

        timepoint = time.strftime("%Y-%m-%d+%H:%M", timepoint)

        params = "hafasID=" + str(hafas) + "&time=" + timepoint + \
                 "&lineID=" + str(lineid) + "&stopIndex=" + str(stopindex) + \
                 "&tourType=" + tourtype + "&tourID=" + str(tourid)

        basereq = "/regions/rnv/modules/lines"
        r = requests.get(self.baseurl + basereq, headers=self.headers, params=params)

        return json.loads(r.text)

    def getnews(self):
        r"""Get current news for affected lines
        :return: json response NewsEntry
        :rtype: json dict"""

        basereq = "/regions/rnv/modules/news"
        r = requests.get(self.baseurl + basereq, headers=self.headers)

        return json.loads(r.text)

    def getticker(self, lines=""):
        r"""Get current ticker for affected lines
        :param lines: semicolon seperated list of lines
        :return: json response NewsEntry
        :rtype: json dict"""

        if lines == "":
            raise Exception("No valid lines.")

        params = "lines=" + str(lines)

        basereq = "/regions/rnv/modules/ticker"
        r = requests.get(self.baseurl + basereq, headers=self.headers, params=params)

        return json.loads(r.text)

    def getcanceledline(self, lineid, departuretime):
        r"""Get information about canceled line valid at timepoint time
        :param lineid: id for requested line info
        :param departuretime: epoch time in ms
        :return: json response CanceledLineTransfer
        :rtype: json dict"""

        if lineid == "" or departuretime == "":
            raise Exception("Not a valid lineid or departuretime.")

        params = "line=" + str(lineid) + "&departureTime=" + departuretime

        basereq = "/regions/rnv/modules/canceled/line"
        r = requests.get(self.baseurl + basereq, headers=self.headers, params=params)

        return json.loads(r.text)

    def getstationinfo(self, lines="", departuretime="", hafas=""):
        r"""Get current information for specific lines at station at timepoint time
        :param lines: semicolon seperated lines (if more than one)
        :param hafas: (optional) station id to get info for a specific station
        :param departuretime: epoch time in ms
        :return: json response StationInfoTransfer
        :rtype: json dict"""

        if lines == "" or departuretime == "":
            raise Exception("Not a valid departuretime or lines.")

        params = ""
        if (lines != "") and (departuretime != ""):
            params += "lines=" + str(lines) + "&departureTime=" + str(departuretime)
            if hafas != "":
                params += "&hafasID=" + str(hafas)

        basereq = "/regions/rnv/modules/info/station"
        r = requests.get(self.baseurl + basereq, headers=self.headers, params=params)

        return json.loads(r.text)

    def getstationdetail(self, stationid=""):
        r""""Get information about the specified station
        :param stationid: station id
        :return: json response StationDetail
        :rtype: json dict
        """

        if stationid == "":
            raise Exception("Not a valid stationid.")

        params = ""

        basereq = "/regions/rnv/modules/stations/detail"
        params += "stationId=" + str(stationid)

        r = requests.get(self.baseurl + basereq, headers=self.headers, params=params)

        return json.loads(r.text)

    def getjourneyinfo(self, hafas="", poles="", departuretime=""):
        r"""Get current information about journey. Similar to ticker
        :param hafas: (optional) station id
        :param poles: (optional) specify pole, can only be set if hafas is set
        :param departuretime: (optional) epoch time in ms
        :return: json response JourneyInfoTransfer
        :rtype: json dict"""

        params = ""
        if hafas == "":
            params += "departureTime=" + departuretime
        else:
            params += "hafasID=" + str(hafas)
            if departuretime != "":
                params += "&departureTime=" + departuretime
            if poles != "":
                params += "&poles=" + poles

        basereq = "/regions/rnv/modules/info/journey"
        r = requests.get(self.baseurl + basereq, headers=self.headers, params=params)

        return json.loads(r.text)

    def getmap(self, thumbnailsize="128", format="png"):
        r"""Get all current available maps
        This means also detour maps
        :param thumnailsize: Size of the thumbnail. Default value is 128,
        possible values are 32, 64, 128, 256 and 512
        :param format: Format of returned map. Default is png, possible values are png or pdf
        :return: json response MapEntity
        :rtype: json dict"""

        if thumbnailsize == "" or format == "":
            raise Exception("Not a valid thumbnailsize or format.")

        params = "thumbnailSize=" + thumbnailsize + "&format=" + format

        basereq = "/regions/rnv/modules/maps"
        r = requests.get(self.baseurl + basereq, headers=self.headers, params=params)

        return json.loads(r.text)

    def __init__(self, apitoken=""):
        if apitoken == "":
            raise Exception("APItoken not set!")

        self.API_TOKEN = apitoken
        self.headers = {"RNV_API_TOKEN": self.API_TOKEN,
                        "Accept": "application/json"}

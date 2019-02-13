import requests
import json
import time
import inspect


class RNVStartInfoApi:
    baseurl = "http://rnv.the-agent-factory.de:8080/easygo2/api"

    API_TOKEN = ""

    headers = {}

    def sendrequest(self, basereq, parameter=""):
        """
        This function wraps the get function from the requests library.

        Parameters
        ----------
        basereq : `str`
            Contains the basereq which is added to the baseurl of the api endpoint
        parameter : `str`
            Contains all the parameters for the api endpoint

        Returns
        -------
        json dict : `dict`
            Converts the result from the request to a json dictionary. If parameters have wrong type or the result
            status_code is not 200 an exception is raised.
        """

        if not (isinstance(basereq, str)):
            errormsg = "Basereq is not string! Current type of baseurl: {}".format(type(basereq))
            raise TypeError(errormsg)
        if not (isinstance(parameter, str)):
            errormsg = "Parameter is not string! Current type of parameter: {}".format(type(parameter))
            raise TypeError(errormsg)

        r = requests.get(self.baseurl + basereq, params=parameter, headers=self.headers)

        if r.status_code != 200:
            funargs, _, _, values = inspect.getargvalues(inspect.currentframe())  # get list of all function parameters
            params = [(i, values[i]) for i in funargs[1:]]  # get value of parameters, expect the first one (self)
            erromsg = "Server returned {}. Parameters and values are: {}".format(r.status_code, params)
            raise ValueError(erromsg)

        return json.loads(r.text)

    def getupdate(self, timestationpackage, timelinepackage, timeunused="2011-11-11+11:11", regionid="1"):
        """Sends an update request, to see if any stations or lines have been updated.

        Parameters
        ----------
        timestationpackage : `struct_time`
            timepoint from last update of station package
        timelinepackage : `struct_time`
            timepoint from last update of line package
        timeunused : `str`
            this parameter is currently unused, but required. We are using the values from the documentations example.
        regionid : `str`
            Id of the requested region. Id = 1 seems to cover the whole RNV area.

        Returns
        -------
        json dict: `dict`
            Empty dict if no updates are available, otherwise a collection of updates:

            - ``updateElementID``: ElementId in response dict (``str``).
            - ``element``: Type of update. Contains either "LINE" for line package or "STATIONPACKAGE" for station package (``str``).
            - ``description``: Contains a description of the update. Mostly something like "contains new lines" (``str``).
            - ``critical``: Contains the urgency of the update element ("true" or "false")(``str``).
            - ``action``: Describes what kind of modification was received. Always set as "CHANGED" (``str``).
            - ``elementID``: ElementId in response dict (``str``).
        """

        if not isinstance(timestationpackage, time.struct_time):
            raise TypeError("timestationpackage has to be a time.struct_time object.")
        if not isinstance(timelinepackage, time.struct_time):
            raise TypeError("timelinepackage has to be a time.struct_time object.")
        if not isinstance(timeunused, str):
            raise TypeError("timeunused has to be a string.")
        if not isinstance(regionid, str):
            raise TypeError("regionid has to be a string.")

        timestationpackage = time.strftime("%Y-%m-%d+%H:%M", timestationpackage)
        timelinepackage = time.strftime("%Y-%m-%d+%H:%M", timelinepackage)

        params = "regionID=" + regionid + "&time=" +\
                 timestationpackage + "$" + timelinepackage + "$" + timeunused

        basereq = "/update"

        return self.sendrequest(basereq, params)

    def getstationpackage(self, regionid="1"):
        """Request the station package of the specified region
        
        Parameters
        ----------
        regionid : `str`
            Id of the requested region. Id = 1 seems to cover the whole RNV area.
            
        Returns
        -------
        json dict: `dict`
            Collection containing all stations of the specified region
            
            - ``regionID``: RegionID of the requested stations (``str``).
            - ``name``: Name of the station package (``str``).
            - ``elementID``: Id of the station package (``str``).
            - ``groupURIs``: Unused. Is there for backwards compatibility (``str``).
            - ``stations``: Collection of all station from requested region (``dict``):
                - ``shortName``: Short name of station (``str``).
                - ``longitude``: Longitude of station (``str``).
                - ``longName``: Full name of station (``str``).
                - ``latitude``: Latitude of station (``str``).
                - ``hafasID``: Unique station id (``str``).
                - ``elementID``: Id of station element (``str``).
        """

        # We are enforcing strictly the required type and wont do any type of casting here
        if not isinstance(regionid, str):
            raise TypeError("regionid has to be a string.")

        basereq = "/regions/rnv/modules/stations/packages/"
        basereq += regionid

        return self.sendrequest(basereq)

    def getlinepackage(self):
        """Request the line package
        
        Returns
        -------
        json dict: `dict`
            Collection of LineJourney-Objects:
            
            - ``lineID``: Id of the line (``str``).
            - ``stopListIds``: List of id where the line will stop (``list`` of ``str``).
            - ``validFromIndex``: Index of the next stop in "stopListIds" (``str``).
        """

        basereq = "/regions/rnv/modules/lines/allJourney"

        return self.sendrequest(basereq)

    def getalllines(self):
        """Request information of all lines
        
        Returns
        -------
        json dict: `dict`
            Collection of Lineinfo-Objects:
            
            - ``lineType``: Type of the line, can be "STRB", "BUS" or "WEBUKOM" (``str``).
            - ``lineId``: Id of the line (``str``).
            - ``icon``: Name of the logo for the line (present for backwards compatibility) (``str``).
            - ``iconName``: Name of the logo which should be displayed for the line (``str``).
            - ``hexcolor``: Color which should be displayed for the line (``str``).
            - ``elementID``: Id of the lineinfo element (``str``).
        """

        basereq = "/regions/rnv/modules/lines/all"

        return self.sendrequest(basereq)

    def getstationmonitor(self, hafas="", timepoint="null", mode="DEP", poles="", needplatformdetail="true"):
        r"""Request info about a station, eg. arrival or depature times
        :param hafas: station id
        :param time: from time package list information from timepoint
        :param mode: default is DEP for departures, ARR is for arrival
        :param poles: comma separated list of poles, to restrict information about the station
        :param needplatformdetail: true or false, on true prints the poles at the output
        :return: json response Journey
        :rtype: json dict"""
        """Request info about a station, eg. arrival or departure times
        
        Parameters
        ----------
        hafas : id of requested station `str`.
        timepoint : Timepoint of request `struct_time`.
        transportFilter: Linenumber filter for result `str`.
        mode : "DEP" for departures, "ARR" for arrival `str`.
        poles : Limit request only to specified poles `list` of `str`.
        needplatformdetail : "true" or "false", on "true" prints if station is a platform or a track `str`.
        
        Returns
        ------
        json dict: `dict`
            Collection of Journey-Objects with Departure-Objects:
            - ``time``: Timepoint of request `str`.
            - ``shortlabel``: `str`.
            - ``projectedtime``: `str`.
            - ``label``: `str`.
            - ``icon``: `str`.
            - ``color``: `str`.
            - ``otherProjectedTimes``: `str`.
            - ``pastRequestText``: `str`.
            - ``ticker``: `str`.
            - ``updateIterations``: `str`.
            - ``updateTime``: `str`.
            - ``listOfDepartures``: `str`.
            - ``stationInfos``: `str`.
        """

        if hafas == "" or mode == "" or needplatformdetail == "":
            raise ValueError("Not a valid hafas or mode or needplatfromdetail.")

        if timepoint != "null":
            timepoint = time.strftime("%Y-%m-%d+%H:%M", timepoint)

        params = "hafasID=" + str(hafas) + "&time=" + timepoint + \
                 "&mode=" + mode + \
                 "&needPlatformDetail=" + needplatformdetail

        if poles != "":
            params += "&poles=" + poles

        basereq = "/regions/rnv/modules/stationmonitor/element"

        return self.sendrequest(basereq, params)

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
            raise ValueError("Not a valid lineid or timepoint or tourtype or tourid or hafas or stopindex.")

        timepoint = time.strftime("%Y-%m-%d+%H:%M", timepoint)

        params = "hafasID=" + str(hafas) + "&time=" + timepoint + \
                 "&lineID=" + str(lineid) + "&stopIndex=" + str(stopindex) + \
                 "&tourType=" + tourtype + "&tourID=" + str(tourid)

        basereq = "/regions/rnv/modules/lines"

        return self.sendrequest(basereq, params)

    def getnews(self):
        r"""Get current news for affected lines
        :return: json response NewsEntry
        :rtype: json dict"""

        basereq = "/regions/rnv/modules/news"

        return self.sendrequest(basereq)

    def getticker(self, lines=""):
        r"""Get current ticker for affected lines
        :param lines: semicolon seperated list of lines
        :return: json response NewsEntry
        :rtype: json dict"""

        if lines == "":
            raise ValueError("No valid lines.")

        params = "lines=" + str(lines)

        basereq = "/regions/rnv/modules/ticker"

        return self.sendrequest(basereq, params)

    def getcanceledline(self, lineid, departuretime):
        r"""Get information about canceled line valid at timepoint time
        :param lineid: id for requested line info
        :param departuretime: epoch time in ms
        :return: json response CanceledLineTransfer
        :rtype: json dict"""

        if lineid == "" or departuretime == "":
            raise ValueError("Not a valid lineid or departuretime.")

        params = "line=" + str(lineid) + "&departureTime=" + departuretime

        basereq = "/regions/rnv/modules/canceled/line"

        return self.sendrequest(basereq, params)

    def getstationinfo(self, lines="", departuretime="", hafas=""):
        r"""Get current information for specific lines at station at timepoint time
        :param lines: semicolon seperated lines (if more than one)
        :param hafas: (optional) station id to get info for a specific station
        :param departuretime: epoch time in ms
        :return: json response StationInfoTransfer
        :rtype: json dict"""

        if lines == "" or departuretime == "":
            raise ValueError("Not a valid departuretime or lines.")

        params = ""
        if (lines != "") and (departuretime != ""):
            params += "lines=" + str(lines) + "&departureTime=" + str(departuretime)
            if hafas != "":
                params += "&hafasID=" + str(hafas)

        basereq = "/regions/rnv/modules/info/station"

        return self.sendrequest(basereq, params)

    def getstationdetail(self, stationid=""):
        r""""Get information about the specified station
        :param stationid: station id
        :return: json response StationDetail
        :rtype: json dict
        """

        if stationid == "":
            raise ValueError("Not a valid stationid.")

        params = ""

        basereq = "/regions/rnv/modules/stations/detail"
        params += "stationId=" + str(stationid)

        return self.sendrequest(basereq, params)

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

        return self.sendrequest(basereq, params)

    def getmap(self, thumbnailsize="128", format="png"):
        r"""Get all current available maps
        This means also detour maps
        :param thumnailsize: Size of the thumbnail. Default value is 128,
        possible values are 32, 64, 128, 256 and 512
        :param format: Format of returned map. Default is png, possible values are png or pdf
        :return: json response MapEntity
        :rtype: json dict"""

        if thumbnailsize == "" or format == "":
            raise ValueError("Not a valid thumbnailsize or format.")

        params = "thumbnailSize=" + thumbnailsize + "&format=" + format

        basereq = "/regions/rnv/modules/maps"

        return self.sendrequest(basereq, params)

    def __init__(self, apitoken=""):
        if apitoken == "":
            raise ValueError("APItoken not set!")

        self.API_TOKEN = apitoken
        self.headers = {"RNV_API_TOKEN": self.API_TOKEN,
                        "Accept": "application/json"}

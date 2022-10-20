# assetInventory
Building the IOOS asset inventory with Python. See the [wiki page](https://github.com/MathewBiddle/assetInventory/wiki) for information on how the IOOS Office compiles the asset inventory.

## Repository outline
* For each year, an inventory directory is created (eg. [2020](https://github.com/MathewBiddle/assetInventory/tree/master/2020)).
* Within each year there are the following files and directories:
  * **data/** - This directory contains the `raw` and `processed` inventory files as well as any additional directories needed for processing.
    * `raw` - The inventory files as received from the RA
    * `processed` - The inventory files after manual processing by IOOS staff.
  * **combined_raw_inventory.(csv | geoJSON | kml)** - These are the concatenation of all the raw inventory files, without cleaning.
  * **processed_inventory.(csv | geoJSON | kml)** - These are cleaned inventory files.
    * Each row is a station.
    * The columns are groupings of observations, with `X` in the cell denoting if the observation was made during the year. See [this mapping](https://github.com/MathewBiddle/assetInventory/blob/735da9f14dd02fdd395e49a86a3836bd6674bc7c/2020/create_master_inventory_from_processed.py#L206-L233) for how the columns are defined.
  * **create_master_inventory.py** - _(Used for testing)_ This script creates the inventory files from the raw spreadsheets. This is useful as a first check of the raw inventory files.
  * **create_master_inventory_from_processed.py** - This script creates the inventory files from the manually processed Excel spreadsheets. 
* **utils/** - This directory contains some useful utilities for evaluating the inventory.
  * **ra_erddaps.json** - a json file of the RA erddap servers.
  * **temp.py** - a place to test
* **environment.yml** - environment file.  

## Raw asset inventory fields
Field | Definition
------|------------
RA | Name of the Regional Association
Station ID | (Optional)  Any unique digital or alphanumeric identifier assigned by the RA or affiliate (e.g. CDIP) to distinguish the station. (e.g. 204; GAK Seward, SUN2, NH-10, etc).  Does NOT include the WMO ID or CMAN ID (see next column).  Leave blank if none.
WMO ID or NWS/CMAN ID | (Required) The World Meteorological Organization 5-digit station identifier (WMO ID) is assigned to ocean platforms (drifting buoys, moored buoys, ocean reference sites, and profiling floats).  e.g. 48088.  The National Weather Service 5-digit alphanumerical identifier (e.g. the National Data Buoy Center CMAN ID) is assigned to shore-based stations.  (e.g. HBYC1).  For special cases where an ID is not assigned, put N/A and briefly indicate why in the notes.
Station Long Name | (Required) Station name. e.g. Red Bank - Garden Banks, Fripps Inlet,  etc.
Station Description | (Optional) Anything descriptive about the station.  This is a freeform field.
Latitude (dec deg) | (Required) Coordinate Reference System WGS84 ([EPSG:4326](https://epsg.io/4326)).
Longitude (dec deg) | (Required) Coordinate Reference System WGS84 ([EPSG:4326](https://epsg.io/4326)).
Platform Type | (Required) A structure or vehicle designed to hold one or more sensors such that the intended oceanographic or atmospheric variable(s) can be monitored or measured in a manner designed for the ocean observing system or scientific hypotheses. Use terms listed in the IOOS Platform Vocabulary: http://mmisw.org/ont/ioos/platform (e.g. buoy, profiling buoy, moored buoy, wave buoy, fixed, offshore tower, profile)  
Station Deployment (mm/yyyy, yyyy, < 5 yr, > 5 yr) | (Required) The time when the station became operational.  This can be determined by the first data record or an installation date.  This indicates the first time the station was deployed - not the last or latest, but the first time - even if IOOS was not established yet. Accepted responses:  Please provide a month and year (mm/yyyy).  If the actual deployment date is not known then provide a year (yyyy), or "< 5 yr" (any date on/after 1/1/2013) or "> 5 yr" (any date on/before 12/31/2012) .  If not available, please indicate why in the notes column.
Currently Operational? (Y, N, O, U) | (Required) Is the asset deployed and collecting data?  Y = Yes (this includes seasonal buoys intended for redeployment).  N = No (it was uninstalled/removed, or is offline with no intent to repair).  O =  Offline (temporary outage, with intent to repair or redeploy).  U = Unknown (e.g. funding uncertainty for repair/redeployment, or operator's plans are unknown).  If O or U, please indicate why in the notes column.
Platform Funder/Sponsor | (Optional) A person, group, or organization’s full or partial support of the asset. (e.g. AOOS, USACE).  Does not include support for data management activities.  Multiple groups may be listed. 
RA Funding Involvement (Yf, Yp, N) | (Required) Does the RA currently fund the asset?  This excludes support for data management activities.  Yf = Fully funds.  Yp = Partially funds.  N = No funding.  
Platform Operator/Owner | (Required)  IOOS Vocabulary definition: "Platform operator used as classifier or contact type; will often be the platform owner as well..."   Akin to the Creator_name attribute in netCDF: "The person/organization that (primarily) collects the data."  In general, the person/group/institution principally responsible for operating the station.  Note that most of the time this is also the group that maintains the asset. 
Operator Sector | (Required) Use the IOOS Organization Societal Sector Vocabulary.  (Academic, industry, tribal, nonprofit, gov_state, gov_federal, etc). Underscores required. http://mmisw.org/ont/ioos/sector
Platform Maintainer | (Optional) The organization with the primary responsibility for providing the maintenance of the platorm/sensors today (e.g. University of Wisconsin-Milwaukee).  In most cases this will be the same as the platform operator.  This is the group that conducts maintenance activities - this does not include the group that funds the maintenance (that group should fall under Platform Funder/Sponsor).
Data Manager | (Optional) The organization that is responsible for the data management activities.  This does not mean the organization that funds the data management.  
Variable Names + water column depth of measurement in meters [CF_name (# m, # m) or CF_name (mult) or CF_name (# depths)]. |	(Required) A list of observed variables that are associated with each station, with the depth(s) of the each measured oceanographic variable in parentheses following the variable name. 'Depths' not required for meteorological variables.  If the variable is ONLY measured at the surface and no other dpeth, you do not need to include any parentheses/depth - just state the variable name.  Use CF names (http://cfconventions.org/Data/cf-standard-names/47/build/cf-standard-name-table.html), and if the variable is not available in CF then use the IOOS parameter vocabulary (http://mmisw.org/ont/ioos/parameter). Accepted responses: sea_water_temperature (1 m, 10 m, 40 m), or sea_water_temperature (sfc, 10 m, 40 m), or sea_water_temperature (sfc and 2 depths), or mass_concentration_of_chlorophyll_in_sea_water. The latter means chlorophyll is measured only at the surface.  Please provide all variables for the asset in a single cell in the spreadsheet (do not separate by row).  
Additional notes | (Optional) Any additional information that does not fit in the template that you think is relevant, or provides context. 

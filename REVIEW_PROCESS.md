# assetInventory Review Process

The Observing Asset Inventory requirements can be found on the bottom of page 4 of the [Cooperative Agreement Progress Report Guidance document](https://cdn.ioos.noaa.gov/media/2021/12/2021-Cooperative-Agreement-Progress-Report-Guidance.pdf). In this document, guidance is provided on what assets to include, what assets not to include, and what specific fields should be populated. The inventories cover the entire calendar year (CY), for the year they are reporting (eg. for 2020 the period of time is Jan 1 2020 -  Dec 31 2020).

## Process for IOOS initial Asset Inventory review:
When the inventories are received for the progress reports, they will be made available through Google Drive. Below is a step-by-step walkthrough of the initial review for an Asset Inventory.
1. Pick an RA to review. Typically this will be the first RA to submit their progress report.
1. Download the associated inventory spreadsheet. This is typically in MS Excel format as a workbook.
1. Open the spreadsheet and review the headers to ensure the appropriate columns exist and are populated. See the [README](https://github.com/MathewBiddle/assetInventory/blob/master/README.md) in this repository for a summary of the fields and their contents. 
   1. If any columns are missing or entirely empty, send a note to the RA about the missing information. See [Sending a request for more information](#sending-a-request-for-more-information).
1. Review changes from last year's inventory
   1. Review any comments provided in the *Additional notes* column.
   1. Review any notes, added as comments, for cells in the inventory.
   1. In some cases, changes from last year's inventory will be indicated with syntax formatting (strikethrough, bold, highlighted).  
1. Clean up the inventory.
   1. Create a copy of the source workbook and store it in `[year]/data/processed/[RA].xlsx` (eg. 2023/data/processed/AOOS.xlsx) 
   1. Run spot_check_stations.ipynb (https://github.com/ioos/ioos-asset-inventory/blob/main/spot_check_stations.ipynb). In Cell[2] Edit `ra = ` to identify the RA your reviewing and run the notebook. 
      1. This gives you a quick sense of if the data in the spreadsheet can be read and if those stations are available via an RA ERDDAP or the IOOS Catalog.
   1. What NOT to include:
   > Assets that are not publicly served/disseminated by the RA (e.g. assets used only for internal purposes).
   > 
   > ▪ Federal stations that are solely owned, operated, maintained, and funded by the federal group (i.e. the RA has no involvement in the operations).
   > 
   > ▪ Servers, vehicles used to deploy/conduct maintenance, a laboratory, etc.
   > 
   > ▪ HF Radar and Gliders, since these inventories are already captured separately.
   1. Create a new sheet in the Excel Workbook and name it **IOOS Removals**.
      1. This is where the stations that shouldn't be considered for the CY Inventory will be moved to.
   1. If a station is indicated to not have observations for the Calendar Year of reporting, move the row to the **IOOS Removals** sheet.
   1. Move any stations with `Platform Type` of `satellite`, `glider`, `HF-radar`, or `surface_current_radar` to the **IOOS Removals** sheet.
   1. Check the `Latitude` and `Longitude` columns to ensure there are valid values and those coordinates are expected (decimal point in correct place, missing negative for West, etc).
      1. This checking is done in `spot_check_stations.ipynb`.
      1. Any issues with coordinates should be relayed back to the RA. 
   1. Check the `Variable Names` for any out of the ordinary names. The goal is to be provided CF standard names, if possible. Otherwise, a descriptive term is sufficient. 
1. Spot check a couple of the stations to ensure data are available.
   1. Using the `RA`, `Station ID`, `WMO ID`, `Station Long Name`, or `Station Description` the station and associated data should be discoverable from the RA website and the [IOOS Catalog](https://data.ioos.us/).
   1. This checking is done in `spot_check_stations.ipynb`.
1. If no issues are found,
   1. Save the processed spreadsheet `[year]/data/processed/[RA].xlsx` (eg. 2023/data/processed/AOOS.xlsx) 
   1. Save the most recent run of `spot_check_stations.ipynb`.
   1. Run [`inventory_creation.ipynb`](https://github.com/ioos/ioos-asset-inventory/blob/main/inventory_creation.ipynb) to update inventory files.
   1. `git add`, `git commit`, and `git push` changes to the repository 
   1. Update the appropriate GitHub issue for the yearly inventory indicating which RA is complete.
   1. update the Trello card with the text `[RA]: Asset Inventory meets the requirements.` (replacing RA with the RA name)


## Sending a request for more information
In some cases, the IOOS Office needs more information from the Regional Association to complete the inventory. If this is the case, the IOOS reviewer will add a comment to the appropriate Trello card. Indicating the RA and including a concise description of what is missing. 

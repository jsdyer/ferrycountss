# Ferry Counts

[Open Ferry Counts](https://coolcode.ca/ferrycountss/) to compare historical passenger boardings on the Halifax–Alderney and Halifax–Woodside ferries in either direction.

<!-- coolcode:guide -->
Compare Halifax to Alderney against the return direction on weekdays. Expand the hourly figures to see how many dates contributed to each average, or download the comparison as CSV.
Switch to Vancouver Harbour to compare SeaBus volumes by direction, season and day type.
<!-- /coolcode:guide -->

## Reading the results

Pick two directions, a weekday or day group, and a month. The bars compare total reported boardings divided by the number of distinct observed dates for that particular route and clock hour. A date with several departures contributes their combined boardings. Missing hours are excluded and explicit zero counts are retained. Each direction’s highlighted peak shows its average and how many observed dates contributed to it. The table and export include the totals and denominators for every hour. The earliest hour wins ties for the peak. Figures describe historical boarding activity and give no direct measurement of vessel capacity.

## Source and coverage

Halifax Regional Municipality publishes boarding counts, route direction, a timestamp and a clock hour in its [Transit Ferry Passenger Counts table](https://services2.arcgis.com/11XBiaBYA9Ep0yNJ/arcgis/rest/services/Transit_Ferry_Passenger_Counts/FeatureServer/0). The source calls the Alderney terminal Dartmouth. Service dates use America/Halifax and hourly groups use Halifax Transit's reported route hour. Coverage spans the twelve calendar months preceding the month of the newest source record. The final partial month is omitted. Halifax Transit says additions can lag by two to four weeks.

The weekly GitHub Action downloads the full selection, checks record IDs and route coverage, and publishes the resulting profiles. An incomplete retrieval leaves the previous edition available. The app displays the source period and retrieval date. No personal information is collected. All filtering happens in the browser.

## Maintaining this tool

Run `python3 scripts/refresh.py` to update the two JSON files under `web/data/`. Run `node --test tests/*.test.mjs`, `python3 -m unittest discover -s tests`, and `python3 scripts/build.py` for an offline validation and build. CI checks the app at a project subpath on desktop and mobile before publishing. The URL follows the repository’s spelling, `ferrycountss`.

## Vancouver SeaBus

TransLink’s [seasonal performance review](https://www.translink.ca/plans-and-projects/strategies-plans-and-guidelines/managing-the-transit-network) supplies average daily passenger volume for each published hour and direction, shown in Pacific time. Use the harbour selector to see each agency’s own dates and units. No observed-date denominators are published in the SeaBus file. A missing figure is distinct from a reported zero. The monthly refresh checks for the latest edition. Run `python3 scripts/refresh_seabus.py` to update it. [SeaBus Clock](https://coolcode.ca/seabusclock/) adds the dated timetable.

<!-- schedule-reliability -->
## Schedule reliability

Public GitHub repositories can have scheduled workflows disabled after 60 days of inactivity. A separate weekly [schedule guard](.github/workflows/schedule-guard.yml) calls GitHub's enable-workflow API for an explicit list of refresh workflows and itself. It can restore workflows disabled for inactivity, preserves manually disabled workflows, and runs independently of collection failures.

The separate schedule guard remains a mitigation, not a scheduling guarantee. The independent [CoolCode refresh watchdog](https://github.com/jsdyer/jsdyer.github.io/blob/main/services/refresh-watchdog/README.md) is maintained in GitHub and uses the generated workflow and freshness registry; do not maintain another target list here. Using it requires installation on a Linux server and GitHub credentials with access to this repository. A generated target does not prove that a private server has adopted it; verify the installed service's report. The guard does not collect data, create dummy commits or change source/check timestamps. Successful collection and published data freshness still need monitoring.
<!-- /schedule-reliability -->

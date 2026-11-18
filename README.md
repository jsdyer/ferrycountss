# Ferry Counts

[Open Ferry Counts](https://coolcode.ca/ferrycountss/) to compare historical passenger boardings on the Halifax–Alderney and Halifax–Woodside ferries in either direction.

<!-- coolcode:guide -->
Compare Halifax to Alderney against the return direction on weekdays. Expand the hourly figures to see how many dates contributed to each average, or download the comparison as CSV.
<!-- /coolcode:guide -->

## Reading the results

Pick two directions, a weekday or day group, and a month. The bars compare total reported boardings divided by the number of distinct observed dates for that particular route and clock hour. A date with several departures contributes their combined boardings. Missing hours are excluded and explicit zero counts are retained. The table and export include the totals and denominators. The earliest hour wins ties for the peak. Figures describe historical boarding activity and give no direct measurement of vessel capacity.

## Source and coverage

Halifax Regional Municipality publishes boarding counts, route direction, a timestamp and a clock hour in its [Transit Ferry Passenger Counts table](https://services2.arcgis.com/11XBiaBYA9Ep0yNJ/arcgis/rest/services/Transit_Ferry_Passenger_Counts/FeatureServer/0). The source calls the Alderney terminal Dartmouth. Service dates use America/Halifax and hourly groups use Halifax Transit's reported route hour. Coverage spans the twelve calendar months preceding the month of the newest source record. The final partial month is omitted. Halifax Transit says additions can lag by two to four weeks.

The weekly GitHub Action downloads the full selection, checks record IDs and route coverage, and publishes the resulting profiles. An incomplete retrieval leaves the previous edition available. The app displays the source period and retrieval date. No personal information is collected. All filtering happens in the browser.

## Maintaining this tool

Run `python3 scripts/refresh.py` to update the two JSON files under `web/data/`. Run `node --test tests/*.test.mjs`, `python3 -m unittest discover -s tests`, and `python3 scripts/build.py` for an offline validation and build. CI checks the app at a project subpath on desktop and mobile before publishing. The URL follows the repository’s spelling, `ferrycountss`.

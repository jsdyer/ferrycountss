"""Build a validated edition of Halifax Transit ferry boarding records."""
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen, Request
from urllib.error import URLError
from zoneinfo import ZoneInfo
import json
import time

ROOT = Path(__file__).resolve().parents[1]
SERVICE = 'https://services2.arcgis.com/11XBiaBYA9Ep0yNJ/arcgis/rest/services/Transit_Ferry_Passenger_Counts/FeatureServer/0'
ATLANTIC = ZoneInfo('America/Halifax')
ROUTES = {'FerryDH':'Alderney → Halifax', 'FerryHD':'Halifax → Alderney',
          'FerryHW':'Halifax → Woodside', 'FerryWH':'Woodside → Halifax'}


def query(**params):
    url = SERVICE + '/query?' + urlencode(dict(f='json',returnGeometry='false',**params))
    for attempt in range(3):
        try:
            with urlopen(Request(url, headers={'User-Agent': 'CoolCode Ferry Counts/1.0'}), timeout=45) as response:
                payload = json.load(response)
            if 'error' in payload:
                raise ValueError(payload['error'])
            return payload
        except (OSError, URLError):
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)


def local(milliseconds):
    return datetime.fromtimestamp(milliseconds / 1000, tz=ATLANTIC)


def assemble(rows):
    hours = defaultdict(int)
    valid = missing = 0
    for row in rows:
        when = local(row['ROUTE_DATETIME'])
        route, hour, total = row['ROUTE_NUMBER'], row['ROUTE_HOUR'], row['RIDERSHIP_TOTAL']
        if route not in ROUTES or hour not in range(24):
            raise ValueError(f'Unexpected route or clock hour: {route} {hour}')
        if total is None:
            missing += 1
            continue
        if type(total) is not int or total < 0:
            raise ValueError('Invalid ridership value')
        hours[route, when.date(), hour] += total
        valid += 1
    groups = defaultdict(lambda: [0,0])
    for (route, day, hour), total in hours.items():
        group = groups[route,day.strftime('%Y-%m'),day.weekday(),hour]
        group[0] += total
        group[1] += 1
    return [list(key)+v for key,v in sorted(groups.items())], valid, missing


def refresh():
    most_recent = query(where='1=1',outFields='ROUTE_DATETIME',orderByFields='ROUTE_DATETIME DESC',resultRecordCount=1)
    last = local(most_recent['features'][0]['attributes']['ROUTE_DATETIME']).date()
    end = last.replace(day=1)
    start = end.replace(year=end.year-1)
    def cutoff(day):
        return datetime.combine(day,datetime.min.time(),ATLANTIC).astimezone(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    where = f"ROUTE_DATETIME >= TIMESTAMP '{cutoff(start)}' AND ROUTE_DATETIME < TIMESTAMP '{cutoff(end)}'"
    ids = sorted(query(where=where,returnIdsOnly='true')['objectIds'])
    if not ids or len(set(ids)) != len(ids):
        raise ValueError('Incomplete source ID list')
    def batch(group):
        doc=query(where=f"({where}) AND OBJECTID >= {group[0]} AND OBJECTID <= {group[-1]}",outFields='OBJECTID,ROUTE_NUMBER,ROUTE_DATETIME,ROUTE_HOUR,RIDERSHIP_TOTAL')
        rows=[f['attributes'] for f in doc['features']]
        if sorted(r['OBJECTID'] for r in rows) != group:
            raise ValueError('Records changed during retrieval')
        return rows
    with ThreadPoolExecutor(max_workers=4) as pool:
        rows=[r for chunk in pool.map(batch,[ids[i:i+1800] for i in range(0,len(ids),1800)]) for r in chunk]
    cells, count, missing = assemble(rows)
    if sorted(query(where=where,returnIdsOnly='true')['objectIds']) != ids:
        raise ValueError('Source changed during retrieval')
    if {c[0] for c in cells} != set(ROUTES):
        raise ValueError('Missing ferry direction')
    from datetime import timedelta
    document=dict(retrieved=datetime.now(timezone.utc).date().isoformat(),start=start.isoformat(),
                  end=(end-timedelta(days=1)).isoformat(),sourceLatest=last.isoformat(),records=count,
                  missing=missing,routes=ROUTES,boardings=sum(c[4] for c in cells))
    target=ROOT/'web/data'
    # Both files are published together by the offline build and Pages deployment.
    (target/'profile.json').write_text(json.dumps(cells,separators=(',',':'))+'\n')
    (target/'status.json').write_text(json.dumps(document,ensure_ascii=False,indent=2)+'\n')
    print(count, 'records;', len(cells), 'hourly groups;', start, 'to', end)

if __name__=='__main__':
    refresh()

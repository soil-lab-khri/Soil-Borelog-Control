import json
import os
import re
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

def coordinate(value, axis):
    limit, directions = (90, 'NS') if axis == 'latitude' else (180, 'EW')
    try:
        number = float(value)
    except ValueError:
        match = re.fullmatch(r"""(\d{1,3})\s*°\s*(\d{1,2})\s*['′]\s*(\d+(?:\.\d+)?)\s*["″]?\s*([NSEW])""", value.upper())
        if not match:
            raise ValueError(f'Invalid {axis}. Use decimal degrees or DMS with hemisphere.')
        deg, minute, second, direction = match.groups()
        if direction not in directions or int(minute) >= 60 or float(second) >= 60:
            raise ValueError(f'Invalid {axis} DMS')
        number = (int(deg) + int(minute)/60 + float(second)/3600) * (-1 if direction in 'SW' else 1)
    if not -limit <= number <= limit:
        raise ValueError(f'{axis} outside valid range')
    return number

def main():
    data = {k:v.strip() for k,v in json.loads(os.environ['ENTRY']).items()}
    for key in ('name','sample_id','district','bore_date','latitude','longitude','borelog'):
        if not data.get(key):
            raise ValueError(f'Missing {key}')
    date.fromisoformat(data['bore_date'])
    for key in ('sotr','borelog','soilreport'):
        if data.get(key):
            url = urlsplit(data[key])
            if url.scheme != 'https' or not url.hostname or any(c.isspace() for c in data[key]):
                raise ValueError(f'Enter a complete HTTPS link for {key}')
    data['point'] = [coordinate(data[key],key) for key in ('latitude','longitude')]
    path = Path('records.json')
    rows = json.loads(path.read_text())
    rows = [r for r in rows if r['sample_id'] != data['sample_id']]
    rows.append(data)
    path.write_text(json.dumps(sorted(rows,key=lambda r:r['sample_id']), ensure_ascii=False, indent=2)+'\n')

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Refresh public marketplace counters, preserving the separate dashboard figure.

Run after installing scripts/design-requirements.txt. No marketplace credentials
are required. The authenticated publisher dashboard's acquisition total is not
exposed by these public counters and is never inferred from their sum.
"""
import argparse,json,subprocess,sys
from datetime import datetime,date
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'assets/profile'
API={
    'vscode':'https://marketplace.visualstudio.com/_apis/public/gallery/extensionquery',
    'openvsx':'https://open-vsx.org/api/guptasachinn/heaplens',
    'jetbrains':'https://plugins.jetbrains.com/api/plugins/35004',
}
QUERY={'filters':[{'criteria':[{'filterType':7,'value':'guptasachinn.heaplens'}]}],'flags':256}


def count(value,label):
    if isinstance(value,bool) or not isinstance(value,(int,float)) or not 0<=value<=10**10 or int(value)!=value:
        raise ValueError(f'Invalid {label} counter.')
    return int(value)


def parse_vscode(payload):
    extensions=[e for r in payload.get('results',[]) for e in r.get('extensions',[])]
    matches=[e for e in extensions if e.get('extensionName')=='heaplens' and e.get('publisher',{}).get('publisherName')=='guptasachinn']
    if len(matches)!=1:
        raise ValueError('VS Code response did not identify exactly one guptasachinn.heaplens extension.')
    stats={s['statisticName']:s.get('value') for s in matches[0].get('statistics',[])}
    return count(stats.get('downloadCount'),'VS Code downloads'),count(stats.get('install'),'VS Code installs')


def parse_openvsx(payload):
    if payload.get('namespace')!='guptasachinn' or payload.get('name')!='heaplens':
        raise ValueError('Open VSX returned a different extension.')
    return count(payload.get('downloadCount'),'Open VSX downloads')


def parse_jetbrains(payload):
    if payload.get('id')!=35004 or payload.get('name')!='HeapLens':
        raise ValueError('JetBrains returned a different plugin.')
    return count(payload.get('downloads'),'JetBrains downloads')


def fetch_json(name):
    # curl uses the system's verified HTTPS trust store, including on macOS.
    command=['curl','--fail','--silent','--show-error','--location','--proto','=https','--max-time','30','--max-filesize','3000000','--retry','2','--retry-max-time','60','-H','Accept: application/json','-H','User-Agent: sachinkg12-profile-stats']
    if name=='vscode':
        command+=['-H','Content-Type: application/json','-H','Accept: application/json;api-version=7.2-preview.1','--data-binary',json.dumps(QUERY)]
    response=subprocess.run(command+[API[name]],capture_output=True,check=True,timeout=95)
    return json.loads(response.stdout)


def updated_data(previous,responses,checked_on):
    date.fromisoformat(checked_on)
    downloads,installs=parse_vscode(responses['vscode'])
    openvsx=parse_openvsx(responses['openvsx'])
    jetbrains=parse_jetbrains(responses['jetbrains'])
    result=dict(previous)
    result.pop('total_downloads',None)
    result.update({'as_of':checked_on,'vscode_downloads':downloads,'vscode_installs':installs,'openvsx_downloads':openvsx,'jetbrains_downloads':jetbrains})
    # Preserve both the value and date supplied from the publisher dashboard.
    count(result['vscode_acquisitions'],'VS Code dashboard acquisitions')
    date.fromisoformat(result['vscode_acquisitions_as_of'])
    result['api_sources']=API
    return result


def refresh(fetch=fetch_json,checked_on=None):
    previous=json.loads((OUT/'heaplens-distribution.json').read_text())
    checked_on=checked_on or datetime.now(ZoneInfo('America/Los_Angeles')).date().isoformat()
    responses={name:fetch(name) for name in API}
    data=updated_data(previous,responses,checked_on)
    from profile_metrics import render_assets,render_readme
    assets=render_assets(data)
    changes={OUT/'heaplens-distribution.json':json.dumps(data,indent=2,ensure_ascii=False)+'\n',
             ROOT/'README.md':render_readme(data,(ROOT/'README.md').read_text())}
    changes.update({OUT/name:value for name,value in assets.items()})
    # All requests, identities, counts, and rendering must succeed before writes.
    pending=[]
    try:
        for path,value in changes.items():
            temp=path.with_name(path.name+'.tmp')
            temp.write_text(value)
            pending.append((temp,path))
        for temp,path in pending:
            temp.replace(path)
    finally:
        for temp,_ in pending:
            temp.unlink(missing_ok=True)
    return data


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--date',help='Record the public counters with this date (YYYY-MM-DD). Defaults to today in America/Los_Angeles.')
    args=parser.parse_args()
    try:
        data=refresh(checked_on=args.date)
    except (ValueError,KeyError,TypeError,subprocess.SubprocessError,OSError) as error:
        print(f'Refresh failed; previous published counts were retained: {error}',file=sys.stderr)
        return 1
    print(f"Public counters: VS Code {data['vscode_downloads']:,} downloads / {data['vscode_installs']:,} installs; Open VSX {data['openvsx_downloads']:,}; IntelliJ {data['jetbrains_downloads']:,}. Dashboard acquisitions remain {data['vscode_acquisitions']:,} ({data['vscode_acquisitions_as_of']}).")
    return 0


if __name__=='__main__':
    raise SystemExit(main())

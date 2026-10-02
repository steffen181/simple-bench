"""Explicit CLI for campaign phases and local dashboard export."""
import argparse
import json
from pathlib import Path
import urllib.request
from .common import read_json


def main(argv):
    parser=argparse.ArgumentParser(prog='tracking-bench');commands=parser.add_subparsers(dest='command',required=True)
    d=commands.add_parser('dashboard');d.add_argument('--campaign',type=Path,required=True);d.add_argument('--out',type=Path,required=True)
    c=commands.add_parser('campaign');phases=c.add_subparsers(dest='phase',required=True)
    p=phases.add_parser('freeze');p.add_argument('--config',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    for phase in ['gate','smoke','bbh','confirm','audit']:
        p=phases.add_parser(phase);p.add_argument('directory',type=Path)
        if phase!='audit':p.add_argument('--key-file',type=Path)
    a=parser.parse_args(argv)
    try:
        from . import frontier_campaign as campaign
        if a.command=='dashboard':
            from .frontier_analysis import analyze_campaign
            from .dashboard import export
            result=export(analyze_campaign(a.campaign),a.out)
        elif a.phase=='freeze':
            def get(url):
                with urllib.request.urlopen(url,timeout=30) as response:return json.load(response)
            catalog=get('https://openrouter.ai/api/v1/models')
            endpoints={mid:get('https://openrouter.ai/api/v1/models/'+mid+'/endpoints') for mid in campaign.MODELS}
            result=campaign.freeze(read_json(a.config),catalog,endpoints,a.out)
        elif a.phase=='audit':result=campaign.audit_campaign(a.directory)
        else:result=campaign.execute_phase(a.directory,a.phase,a.key_file)
    except (ValueError,OSError,KeyError) as exc:parser.exit(2,f'Campaign failed: {type(exc).__name__}: {exc}\n')
    print(json.dumps(result,indent=2,ensure_ascii=False))
    return 2 if result.get('status')=='STOPPED' else 0

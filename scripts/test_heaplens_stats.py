import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import refresh_heaplens_stats as stats


def responses():
    return {
        'vscode':{'results':[{'extensions':[{'extensionName':'heaplens','publisher':{'publisherName':'guptasachinn'},'statistics':[{'statisticName':'downloadCount','value':13477.0},{'statisticName':'install','value':2319.0},{'statisticName':'updateCount','value':10081.0}]}]}]},
        'openvsx':{'name':'heaplens','namespace':'guptasachinn','downloadCount':13811},
        'jetbrains':{'id':35004,'name':'HeapLens','downloads':53},
    }


def previous():
    return {'as_of':'2026-11-20','vscode_downloads':13000,'vscode_installs':2300,'openvsx_downloads':13700,'jetbrains_downloads':52,'total_downloads':26752,
            'vscode_acquisitions':15832,'vscode_acquisitions_as_of':'2026-11-21','vscode_acquisitions_source':'Publisher dashboard',
            'sources':{'vscode':'https://marketplace.visualstudio.com/items?itemName=guptasachinn.heaplens','openvsx':'https://open-vsx.org/extension/guptasachinn/heaplens','jetbrains':'https://plugins.jetbrains.com/plugin/35004-heaplens'}}


class MarketplaceCounts(unittest.TestCase):
    def test_download_install_and_update_counts_are_not_conflated(self):
        self.assertEqual(stats.parse_vscode(responses()['vscode']),(13477,2319))

    def test_wrong_extensions_and_plugins_are_rejected(self):
        for name,parser,key,value in [('vscode',stats.parse_vscode,'extensionName','other'),('openvsx',stats.parse_openvsx,'namespace','other'),('jetbrains',stats.parse_jetbrains,'id',1)]:
            data=responses()[name]
            target=data['results'][0]['extensions'][0] if name=='vscode' else data
            target[key]=value
            with self.assertRaises(ValueError):
                parser(data)

    def test_invalid_and_missing_counts_never_become_zero(self):
        for value in [None,True,-1,1.5,'53',float('nan'),float('inf')]:
            with self.assertRaises(ValueError):
                stats.count(value,'test')
        self.assertEqual(stats.count(0,'test'),0)

    def test_refresh_preserves_dashboard_value_date_and_measure(self):
        updated=stats.updated_data(previous(),responses(),'2026-11-22')
        self.assertEqual(updated['vscode_acquisitions'],15832)
        self.assertEqual(updated['vscode_acquisitions_as_of'],'2026-11-21')
        self.assertEqual(updated['vscode_downloads'],13477)
        self.assertEqual(updated['as_of'],'2026-11-22')
        self.assertNotIn('total_downloads',updated)

    def test_failed_request_preserves_every_existing_file(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder); out=root/'assets/profile'; out.mkdir(parents=True)
            (out/'heaplens-distribution.json').write_text(json.dumps(previous()))
            (out/'heaplens-adoption.svg').write_text('existing desktop image')
            (out/'heaplens-adoption-mobile.svg').write_text('existing mobile image')
            (root/'README.md').write_text('existing profile')
            before={p:p.read_bytes() for p in root.rglob('*') if p.is_file()}
            def unavailable(name):
                if name=='openvsx':
                    raise OSError('marketplace temporarily unavailable')
                return responses()[name]
            with patch.object(stats,'ROOT',root),patch.object(stats,'OUT',out):
                with self.assertRaises(OSError):
                    stats.refresh(fetch=unavailable,checked_on='2026-11-22')
            self.assertEqual(before,{p:p.read_bytes() for p in root.rglob('*') if p.is_file()})

    def test_readme_refresh_only_replaces_the_designated_stats_block(self):
        from profile_metrics import render_readme
        original='Author introduction\n<!-- heaplens-stats:start -->old stats<!-- heaplens-stats:end -->\nResearch and keynote'
        updated=render_readme(stats.updated_data(previous(),responses(),'2026-11-22'),original)
        self.assertTrue(updated.startswith('Author introduction\n'))
        self.assertTrue(updated.endswith('\nResearch and keynote'))
        self.assertIn('15,832 acquisitions',updated)
        self.assertIn('heaplens-adoption-mobile.svg',updated)
        self.assertNotIn('VS Code dashboard:',updated)
        self.assertNotIn('VS Code public API:',updated)
        self.assertNotIn('not unique users',updated)
        self.assertNotIn('<sub>',updated)

    def test_first_refresh_keeps_the_heaplens_project_and_other_projects(self):
        from profile_metrics import render_readme
        projects='<p><a href="https://github.com/sachinkg12/heaplens"><picture><img src="./assets/profile/projects/project-01.svg" /></picture></a></p>\nOther projects and their links\n'
        old=projects+'<p><a href="https://github.com/sachinkg12/heaplens"><picture><img src="./assets/profile/heaplens-adoption.svg" /></picture></a></p>\n<sub>Snapshot: old counts</sub>\nReviewing'
        updated=render_readme(stats.updated_data(previous(),responses(),'2026-11-22'),old)
        self.assertTrue(updated.startswith(projects))
        self.assertTrue(updated.endswith('\nReviewing'))


if __name__=='__main__':
    unittest.main()

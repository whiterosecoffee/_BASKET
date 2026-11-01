import copy, importlib.util, json, tempfile, unittest
from pathlib import Path
from range_replay import detect, replay, append_records, first_passage, legs, contacts, CONFIG
START=1790861400000  # 2026-10-01 09:30 ET
def bars(n=180):
    out=[]
    for i in range(n):
        p=60+[0,.1,.2,.1][i%4]
        out.append(dict(t=START+i*60000,o=p,c=p,h=p+.02,l=p-.02,v=100.,vw=p,n=1.))
    return out
def daily():
    return [dict(t=1788235200000-i*86400000,o=60.,c=60.,h=61.,l=59.,v=10000.,vw=60.) for i in range(25)][::-1]
ZONE={"lower_band":[59.9,60.],"upper_band":[60.9,61.],"width":1.1}
class ReplayTests(unittest.TestCase):
    def test_detect_only_confirmed_pivots(self):
        p=bars(30);z=detect(p);self.assertIsNotNone(z)
        for k in ['formation_lower_pivots','formation_upper_pivots']:
            self.assertTrue(all(x['confirmed_at']<=__import__('range_replay').stamp(p[-1]['t']+60000) for x in z[k]))
    def test_no_range_on_gap(self):
        p=bars(31);p.pop(3);self.assertIsNone(detect(p))
    def test_walkforward_feature_stability(self):
        a=bars();r=replay(a,daily())
        self.assertTrue(r)
        cutoff=a[90]['t']
        revised=copy.deepcopy(a)
        for b in revised[91:]:
            for k in ['o','c','h','l','vw']:b[k]+=20
        newer={x['event_id']:x for x in replay(revised,daily())}
        for old in r:
            if __import__('datetime').datetime.fromisoformat(old['evaluated_through']).timestamp()*1000<=cutoff:
                self.assertEqual(old['features_at_freeze'],newer[old['event_id']]['features_at_freeze'])
                self.assertEqual(old['input_hash'],newer[old['event_id']]['input_hash'])
    def test_prefix_finalized_records(self):
        a=bars();full=replay(a,daily());prefix=replay(a[:100],daily())
        fm={x['event_id']:x for x in full}
        for p in prefix:
            if not p['quality']['right_censored']:
                self.assertEqual(p['revision_id'],fm[p['event_id']]['revision_id'])
    def test_target_failure_ambiguity(self):
        p=bars(1);p[0]['c']=59.95
        f=bars(2)[1:];f[0].update(h=61.2,l=59.7,c=60.5)
        self.assertEqual(first_passage(p,f,ZONE,False)['outcome'],'ambiguous_same_bar')
    def test_timeout_not_failure(self):
        p=bars(1);p[0]['c']=59.95
        f=bars(3)[1:]
        self.assertEqual(first_passage(p,f,ZONE,False)['outcome'],'timeout')
        self.assertEqual(first_passage(p,f,ZONE,True)['outcome'],'right_censored')
    def test_complete_close_traversal(self):
        a=bars(4)
        for b,p in zip(a,[59.95,60.4,60.95,59.95]):b['c']=p
        x=legs(a,ZONE);self.assertEqual([r['direction'] for r in x],['up','down'])
        self.assertEqual(sum(r['shares'] for r in x),300.)
    def test_no_ceiling_contacts(self):
        self.assertEqual(contacts(bars(20),[61.,61.1],'upper',1),[])
    def test_neighboring_contacts_not_independent(self):
        a=bars(4)
        for b in a:b.update(h=61.05,l=60.95,c=61.)
        e=contacts(a,[60.9,61.1],'upper',1.)
        self.assertEqual(len(e),1)
        self.assertEqual(e[0]['response'],'unresolved')
        self.assertEqual(e[0]['shares'],400.)
    def test_idempotent_history(self):
        r=replay(bars(),daily())
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'x.jsonl'
            self.assertEqual(append_records(p,r),len(r))
            self.assertEqual(append_records(p,r),0)
            self.assertEqual(len(p.read_text().splitlines()),len(r))
    def test_ticker_is_explicit(self):
        r=replay(bars(),daily(),ticker="OTHER")
        self.assertTrue(r);self.assertEqual({x['ticker'] for x in r},{"OTHER"})
    def test_current_session_not_daily_baseline(self):
        a=bars();d=daily();expected=replay(a,d)
        d.append(dict(t=START,o=60.,c=60.,h=61.,l=59.,v=1e12,vw=60.))
        actual=replay(a,d)
        self.assertEqual([r['input_hash'] for r in expected],[r['input_hash'] for r in actual])
if __name__=="__main__":unittest.main()


"""Generic walk-forward range-event research; Massive historical minute inputs.
This is not canonical ingestion or calibrated trading inference.
"""
import argparse, csv, hashlib, json, math, statistics, sys
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from battle_matrix import path_summary
ET=ZoneInfo("America/New_York")
VERSION="range-replay@1.0.0"
CONFIG={"formation_minutes":30,"forward_minutes":30,"retry_minutes":5,
        "min_cluster_pivots":2,"pivot_separation_minutes":3,
        "cluster_tolerance_median_bar_range":0.6,"tick":0.01,
        "break_confirm_closes":2,"score_half_life_minutes":5}
LIMITS=["OHLCV bars, not full trade/quote tape or signed order flow",
        "VWAP-assigned whole-bar volume is approximate, not volume-at-price",
        "Historical vendor revisions; not an archived point-in-time feed",
        "Confirmed pivots use one subsequent bar available by formation freeze",
        "Heuristic range detector and thresholds are uncalibrated",
        "Overlapping formation windows are not independent statistical samples",
        "No executable bid/ask, slippage or profitability inference"]

def stamp(t): return datetime.fromtimestamp(t/1000,ET).isoformat()
def session(t): return datetime.fromtimestamp(t/1000,ET).date().isoformat()
def minute(t):
    x=datetime.fromtimestamp(t/1000,ET);return x.hour*60+x.minute
def sha(x): return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":"),allow_nan=False).encode()).hexdigest()
def load_csv(path):
    rows=[]
    for row in csv.DictReader(Path(path).open()):
        b={k:float(v) for k,v in row.items()};b["t"]=int(b["t"])
        if any(not math.isfinite(v) for v in b.values()): raise ValueError("nonfinite")
        if b["v"]<0 or min(b[k] for k in ("o","c","h","l","vw"))<=0: raise ValueError("invalid")
        if not b["l"]<=min(b["o"],b["c"])<=max(b["o"],b["c"])<=b["h"]:raise ValueError("bad envelope")
        rows.append(b)
    if any(b["t"]<=a["t"] for a,b in zip(rows,rows[1:])):raise ValueError("unordered/duplicate")
    return rows
def contiguous(rows):
    return all(b["t"]-a["t"]==60000 for a,b in zip(rows,rows[1:]))
def cluster(points,tolerance):
    groups=[]
    for price,index in sorted(points):
        if not groups or price-groups[-1][0][0]>tolerance: groups.append([])
        groups[-1].append((price,index))
    candidates=[]
    for group in groups:
        separated=[]
        for p,i in sorted(group,key=lambda x:x[1]):
            if not separated or i-separated[-1][1]>=CONFIG["pivot_separation_minutes"]:
                separated.append((p,i))
        if len(separated)>=CONFIG["min_cluster_pivots"]: candidates.append(separated)
    if not candidates:return None
    return max(candidates,key=lambda g:(len(g),max(x[1] for x in g)))
def detect(past):
    if len(past)!=CONFIG["formation_minutes"] or not contiguous(past):return None
    tolerance=max(.03,statistics.median(b["h"]-b["l"] for b in past)*.6)
    lows=[];highs=[]
    for j in range(1,len(past)-1):
        a,b,c=past[j-1:j+2]
        if b["l"]<=a["l"] and b["l"]<c["l"]:lows.append((b["l"],j))
        if b["h"]>=a["h"] and b["h"]>c["h"]:highs.append((b["h"],j))
    lower=cluster(lows,tolerance);upper=cluster(highs,tolerance)
    if not lower or not upper:return None
    band=lambda g:[round(min(x[0] for x in g)-tolerance*.25,4),round(max(x[0] for x in g)+tolerance*.25,4)]
    lb,ub=band(lower),band(upper);width=ub[1]-lb[0]
    if lb[1]>=ub[0] or width<3*tolerance or not lb[0]<=past[-1]["c"]<=ub[1]:return None
    return {"lower_band":lb,"upper_band":ub,"width":width,"tolerance":tolerance,
            "formation_lower_pivots":[{"price":p,"at":stamp(past[i]["t"]),"confirmed_at":stamp(past[i+1]["t"]+60000)} for p,i in lower],
            "formation_upper_pivots":[{"price":p,"at":stamp(past[i]["t"]),"confirmed_at":stamp(past[i+1]["t"]+60000)} for p,i in upper]}
def flow(rows,zone,previous,addv):
    sides={k:{"weighted_travel":0.,"weighted_dollars":0.,"bars":0,"shares":0.,"dollars":0.,"sum_w":0.,"sum_w2":0.} for k in ("up","down")}
    lo,hi=zone["lower_band"][0],zone["upper_band"][1]
    clip=lambda p:min(hi,max(lo,p))
    if not rows:return {"score":None,"state":"empty","sides":sides}
    end=rows[-1]["t"]+60000
    for b in rows:
        change=(clip(b["c"])-clip(previous))/(hi-lo);previous=b["c"]
        if not lo<=b["vw"]<=hi or not change:continue
        s=sides["up" if change>0 else "down"];w=2**(-((end-b["t"]-60000)/60000)/5)
        s["weighted_travel"]+=w*abs(change);s["weighted_dollars"]+=w*b["v"]*b["vw"]
        s["bars"]+=1;s["shares"]+=b["v"];s["dollars"]+=b["v"]*b["vw"];s["sum_w"]+=w;s["sum_w2"]+=w*w
    for s in sides.values():
        s["effective_n"]=s["sum_w"]**2/s["sum_w2"] if s["sum_w2"] else 0.
        s["efficiency"]=s["weighted_travel"]/(s["weighted_dollars"]/addv) if addv and s["weighted_dollars"] else None
    valid=all(s["bars"]>=3 and s["effective_n"]>=2 and s["efficiency"] for s in sides.values())
    return {"score":sides["up"]["efficiency"]/sides["down"]["efficiency"] if valid else None,
            "state":"scored" if valid else "insufficient_evidence","sides":sides}
def activity(rows,band=None):
    selected=[b for b in rows if band is None or band[0]<=b["vw"]<=band[1]]
    v=sum(b["v"] for b in selected);d=sum(b["v"]*b["vw"] for b in selected)
    return {"shares":v,"dollar_turnover":d,"bars":len(selected),"vwap":d/v if v else None}
def contacts(rows,band,side,width):
    events=[];active=None;armed=True;away=0
    buffer=max(.02,width*.1)
    for b in rows:
        touch=b["l"]<=band[1] and b["h"]>=band[0]
        if armed and touch:
            active={"contact_at":stamp(b["t"]),"contact_bar_t":b["t"],"side":side,
                    "shares":0.,"dollar_turnover":0.,"observed_bars":0};armed=False
        if active:
            active['shares']+=b['v'];active['dollar_turnover']+=b['v']*b['vw'];active['observed_bars']+=1
            crossed=b["c"]<band[0]-.02 if side=="lower" else b["c"]>band[1]+.02
            rejected=b["c"]>band[1]+buffer if side=="lower" else b["c"]<band[0]-buffer
            if crossed or rejected:
                events.append(dict(active,response="closed_through" if crossed else "retreated_into_range",
                                   response_at=stamp(b["t"]+60000),
                                   response_same_bar=b["t"]==active["contact_bar_t"]))
                active=None
        far=b["l"]>band[1]+buffer if side=="lower" else b["h"]<band[0]-buffer
        away=away+1 if far else 0
        if active is None and away>=2:armed=True
    if active:events.append(dict(active,response="unresolved",response_at=None))
    return events
def legs(rows,zone):
    lb,ub=zone["lower_band"],zone["upper_band"];anchor=None;out=[]
    for i,b in enumerate(rows):
        side="lower" if b["c"]<=lb[1] else "upper" if b["c"]>=ub[0] else None
        if side is None:continue
        if anchor is None:anchor=(side,i)
        elif side!=anchor[0]:
            start=rows[anchor[1]];segment=rows[anchor[1]+1:i+1]
            out.append({"direction":"up" if side=="upper" else "down",
                        "start_at":stamp(start["t"]+60000),"end_at":stamp(b["t"]+60000),
                        "minutes":(b["t"]-start["t"])/60000,
                        "from_price":start["c"],"to_price":b["c"],**activity(segment)})
            anchor=(side,i)
    return out
def first_passage(past,future,zone,partial):
    lb,ub=zone["lower_band"],zone["upper_band"]
    anchors=[("lower" if b["c"]<=lb[1] else "upper" if b["c"]>=ub[0] else None,i,b) for i,b in enumerate(future)]
    p=past[-1]
    initial="lower" if p["c"]<=lb[1] else "upper" if p["c"]>=ub[0] else None
    if initial:side,start,b=initial,-1,p
    else:
        candidate=next((x for x in anchors if x[0]),None)
        if candidate is None:return {"outcome":"no_boundary_anchor","censored":partial}
        side,start,b=candidate
    for nxt in future[start+1:]:
        target=nxt["h"]>=ub[0] if side=="lower" else nxt["l"]<=lb[1]
        failure=nxt["l"]<lb[0]-.02 if side=="lower" else nxt["h"]>ub[1]+.02
        if target or failure:
            return {"anchor":side,"start_at":stamp(b["t"]+60000),
                    "outcome":"ambiguous_same_bar" if target and failure else "opposite_band_first" if target else "outside_failure_first",
                    "end_at":stamp(nxt["t"]+60000),"minutes":(nxt["t"]-b["t"])/60000,"censored":False}
    return {"anchor":side,"start_at":stamp(b["t"]+60000),"outcome":"right_censored" if partial else "timeout",
            "end_at":stamp(future[-1]["t"]+60000) if future else None,"censored":partial}
def replay(minute_rows,daily,ticker="CRWV"):
    by_day={}
    for b in minute_rows:
        if 570<=minute(b["t"])<960:by_day.setdefault(session(b["t"]),[]).append(b)
    records=[];prior_sessions=[]
    for day,rows in sorted(by_day.items()):
        full=len(rows)==390 and minute(rows[0]["t"])==570 and minute(rows[-1]["t"])==959 and contiguous(rows)
        prior_daily=[b for b in daily if session(b["t"])<day][-20:]
        adv=sum(b["v"] for b in prior_daily)/20 if len(prior_daily)==20 else None
        addv=sum(b["v"]*b["vw"] for b in prior_daily)/20 if len(prior_daily)==20 else None
        i=CONFIG["formation_minutes"]-1
        while i<len(rows)-1:
            past=rows[i-29:i+1];zone=detect(past)
            if not zone:i+=CONFIG["retry_minutes"];continue
            future=rows[i+1:i+1+CONFIG["forward_minutes"]]
            planned_end=past[-1]["t"]+60000+30*60000
            partial=len(future)<30 and not full
            # End range when two successive closes establish an outside break.
            streak=0;last_dir=None;breakout=None
            for j,b in enumerate(future):
                direction="up" if b["c"]>zone["upper_band"][1]+.02 else "down" if b["c"]<zone["lower_band"][0]-.02 else None
                streak=streak+1 if direction and direction==last_dir else 1 if direction else 0
                last_dir=direction
                if streak>=2:
                    future=future[:j+1];breakout={"direction":direction,"confirmed_at":stamp(b["t"]+60000)};partial=False;break
            if not future:break
            gaps=not contiguous(past+future)
            if gaps:partial=True
            act=activity(future);upper=contacts(future,zone["upper_band"],"upper",zone["width"]);lower=contacts(future,zone["lower_band"],"lower",zone["width"])
            profiles=[]
            offsets={minute(b["t"]) for b in future}
            for prior in prior_sessions[-20:]:
                prof=[b for b in prior if minute(b["t"]) in offsets]
                if len(prof)==len(offsets):profiles.append(sum(b["v"] for b in prof))
            expected=statistics.mean(profiles) if len(profiles)>=5 else None
            boundary_ambiguous=sum(b["h"]>=zone["upper_band"][0] and b["l"]<=zone["lower_band"][1] for b in future)
            features={"formation_flow":flow(past[-15:],zone,past[-16]["c"],addv),
                      "formation_path":path_summary(past,zone["width"]),
                      "start_position":(past[-1]["c"]-zone["lower_band"][0])/zone["width"],
                      "note":"formation-fit features, known by freeze; not independent support confirmation"}
            event_id=sha({"ticker":ticker,"session":day,"freeze":past[-1]["t"]+60000,"zone":zone,"config":CONFIG})
            record={"schema":"ticker.range-event@1","method":VERSION,"method_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                    "config":CONFIG,"ticker":ticker,"currency":"USD","session":day,
                    "event_id":event_id,"range_id":event_id,"formed_from":stamp(past[0]["t"]),
                    "frozen_at":stamp(past[-1]["t"]+60000),"evaluated_through":stamp(future[-1]["t"]+60000),
                    "planned_end":stamp(planned_end),"zone":zone,"features_at_freeze":features,
                    "freeze_price":past[-1]['c'],"end_price":future[-1]['c'],
                    "outcome":{"range_end":"confirmed_break" if breakout else "partial_tape" if partial else "session_end_timeout" if len(future)<30 else "horizon_timeout",
                               "breakout":breakout,"first_passage":first_passage(past,future,zone,partial),
                               "completed_close_traversals":legs([past[-1]]+future,zone),
                               "upper_encounters":upper,"lower_encounters":lower,
                               "no_ceiling_contact":len(upper)==0,
                               "net_displacement_ranges":(future[-1]["c"]-past[-1]["c"])/zone["width"],
                               "observed_path":path_summary([past[-1]]+future,zone["width"]),
                               "flow":flow(future,zone,past[-1]["c"],addv),
                               "activity":act,"lower_band_activity":activity(future,zone["lower_band"]),
                               "upper_band_activity":activity(future,zone["upper_band"]),
                               "volume_pct_adv20":act["shares"]/adv*100 if adv else None,
                               "same_time_rvol":act["shares"]/expected if expected else None,
                               "same_time_profile_sessions":len(profiles),
                               "ceiling_contact_bars":sum(b["h"]>=zone["upper_band"][0] and b["l"]<=zone["upper_band"][1] for b in future)},
                    "quality":{"complete_session":full,"right_censored":partial,"minute_gaps":gaps,
                               "ambiguous_both_boundary_bars":boundary_ambiguous,"volume_at_price":"whole-bar VWAP approximation",
                               "available_at":None,"retrieved_at":None,"retrieval_date":"2026-10-28",
                               "ingested_at":"2026-10-28T15:50:00Z","source":"Massive split-adjusted one-minute aggregates",
                               "limitations":LIMITS},
                    "input_hash":sha({"formation":past,"evaluation":future,"daily_baseline":prior_daily,
                                      "profile_rows":[[b for b in p if minute(b["t"]) in offsets] for p in prior_sessions[-20:]]})}
            record["revision_id"]=sha(record);records.append(record)
            i+=len(future)
        if full:prior_sessions.append(rows)
    return records
def append_records(path,records):
    path=Path(path);existing=[]
    if path.exists():existing=[json.loads(x) for x in path.read_text().splitlines() if x.strip()]
    seen={r["revision_id"] for r in existing};written=0
    with path.open("a") as f:
        for r in records:
            if r["revision_id"] in seen:continue
            old=next((x["revision_id"] for x in reversed(existing) if x["event_id"]==r["event_id"]),None)
            out=dict(r,supersedes_revision_id=old)
            f.write(json.dumps(out,sort_keys=True,allow_nan=False)+"\n");existing.append(out);seen.add(r["revision_id"]);written+=1
    return written
def main():
    p=argparse.ArgumentParser();p.add_argument("--minutes",required=True);p.add_argument("--daily",required=True)
    p.add_argument("--out",required=True);p.add_argument("--ticker",default="CRWV")
    a=p.parse_args();m=load_csv(a.minutes);d=load_csv(a.daily);records=replay(m,d,a.ticker)
    written=append_records(a.out,records)
    print(json.dumps({"events":len(records),"new_revisions":written,"sessions":len({r["session"] for r in records})}))
if __name__=="__main__":main()


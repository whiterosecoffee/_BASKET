"""Research prototype: generic, replayable battle-band matrix. No live worker.
Inputs use Massive bar fields t,o,h,l,c,v,vw. Dollar volume is bar approximation.
Run: python battle_matrix.py matrix-input-2026-10-28.json --out matrix-output.json
"""
import argparse, hashlib, json, math
from pathlib import Path
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

VERSION = "battle-matrix@1"
ET = ZoneInfo("America/New_York")

def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()

def minute_end(bar):
    return int(bar["t"]) + 60000

def regular(bar):
    dt = datetime.fromtimestamp(bar["t"]/1000, ET)
    return 570 <= dt.hour*60+dt.minute < 960

def validate_bars(bars):
    seen = set()
    previous = -1
    for b in bars:
        if b["t"] in seen or b["t"] <= previous:
            raise ValueError("bars must have unique increasing timestamps")
        seen.add(b["t"]); previous = b["t"]
        if any(not math.isfinite(float(b[k])) for k in ("t","o","h","l","c","v","vw")):
            raise ValueError("non-finite bar")
        if b["v"] < 0 or min(b[k] for k in ("o","h","l","c","vw")) <= 0:
            raise ValueError("invalid price/volume")
        if not b["l"] <= min(b["o"],b["c"]) <= max(b["o"],b["c"]) <= b["h"]:
            raise ValueError("OHLC envelope inconsistent")

def baseline(daily, session):
    eligible = [b for b in daily if datetime.fromtimestamp(b["t"]/1000, ET).date().isoformat() < session][-20:]
    if len(eligible) != 20:
        return {"adv20": None, "addv20": None, "sessions": len(eligible)}
    return {"adv20": sum(b["v"] for b in eligible)/20,
            "addv20": sum(b["v"]*b["vw"] for b in eligible)/20, "sessions":20}

def path_summary(window, width):
    """Kaufman-style signed progress/noise on observed close path, not OFI."""
    if not window:
        return {"state":"empty", "signed_efficiency":None, "gross_travel_ranges":None}
    if any(b['t']-a['t'] != 60000 for a,b in zip(window,window[1:])):
        return {"state":"gapped", "signed_efficiency":None, "gross_travel_ranges":None}
    points=[window[0]['o']]+[b['c'] for b in window]
    gross=sum(abs(b-a) for a,b in zip(points,points[1:]))
    net=points[-1]-points[0]
    return {"state":"observed_close_path", "signed_efficiency":net/gross if gross else None,
            "gross_travel_ranges":gross/width, "net_displacement_ranges":net/width,
            "flat_path":gross==0}

def boundary_summary(window, upper, width, as_of):
    """Bar contacts are not independent tests or proof of rejection."""
    contacts=[b for b in window if b['h']>=upper[0] and b['l']<=upper[1]]
    hysteresis=.05*width  # explicit uncalibrated engineering parameter
    armed=False; entries=0
    for b in window:
        if b['c']<upper[0]-hysteresis:
            armed=True
        elif b['c']>=upper[0] and armed:
            entries+=1; armed=False
    last=minute_end(contacts[-1]) if contacts else None
    return {'contact_bar_count':len(contacts), 'close_entry_episodes':entries,
            'entry_hysteresis_usd':hysteresis, 'last_contact_at':last,
            'minutes_since_last_window_contact':(as_of-last)/60000 if last else None,
            'close_fraction_above_ceiling':sum(b['c']>upper[1] for b in window)/len(window) if window else None,
            'no_ceiling_contact_in_window':not bool(contacts),
            'initial_inside_episode_left_censored':bool(window and window[0]['c']>=upper[0]),
            'method':'OHLC contact bars; debounced close entries; not independent rejection events'}

def zone_metrics(bars, zone, as_of, minutes, base, half_life=5, min_bars=3):
    lower, upper = zone["lower"], zone["upper"]
    lo, hi = float(lower[0]), float(upper[1])
    if not lo <= lower[1] < upper[0] <= hi:
        raise ValueError("ordered, nonoverlapping lower and upper bands required")
    frozen = int(zone["frozen_at"])
    start = as_of - minutes*60000
    # No pre-freeze flow in the score. Partial windows remain explicitly partial.
    window = [b for b in bars if start < minute_end(b) <= as_of and b["t"] >= frozen]
    previous = {b["t"]: b for b in bars if minute_end(b) <= as_of}
    sides = {k: {"weighted_travel":0., "weighted_notional":0., "weight":0.,
                 "weight_sq":0., "bars":0, "shares":0., "notional":0.} for k in ("up","down")}
    neutral_notional = 0.
    assigned = []
    clip = lambda p: min(hi,max(lo,p))
    for b in window:
        prev = previous.get(b["t"]-60000)
        if prev is None or not regular(prev):
            continue
        # Exclusive membership by bar VWAP. This is not actual volume-at-price.
        if not lo <= b["vw"] <= hi:
            continue
        assigned.append(b)
        move = (clip(b["c"])-clip(prev["c"]))/(hi-lo)
        notional = b["v"]*b["vw"]
        if not move:
            neutral_notional += notional
            continue
        side = sides["up" if move>0 else "down"]
        weight = 2**(-((as_of-minute_end(b))/60000)/half_life)
        side["weighted_travel"] += weight*abs(move)
        side["weighted_notional"] += weight*notional
        side["weight"] += weight; side["weight_sq"] += weight*weight
        side["bars"] += 1; side["shares"] += b["v"]; side["notional"] += notional
    for side in sides.values():
        side["effective_n"] = side["weight"]**2/side["weight_sq"] if side["weight_sq"] else 0.
        side["efficiency"] = (side["weighted_travel"]/(side["weighted_notional"]/base["addv20"])
                              if side["weighted_notional"] and base["addv20"] else None)
    enough = all(s["bars"] >= min_bars and s["effective_n"] >= 2 for s in sides.values())
    score = None
    if enough and all(s["efficiency"] and s["efficiency"]>0 for s in sides.values()):
        score = sides["up"]["efficiency"]/sides["down"]["efficiency"]
    state = ("scored" if score is not None else
             "missing_baseline" if not base["addv20"] else "insufficient_directional_sample")
    v = sum(b["v"] for b in assigned)
    d = sum(b["v"]*b["vw"] for b in assigned)
    last = next((b for b in reversed(bars) if minute_end(b)<=as_of), None)
    def band_activity(band):
        selected = [b for b in window if band[0] <= b['vw'] <= band[1]]
        return {'shares':sum(b['v'] for b in selected),
                'dollar_volume':sum(b['v']*b['vw'] for b in selected),
                'bars':len(selected), 'method':'whole-bar VWAP assignment, not exact volume-at-price'}
    completed = [b for b in bars if start < minute_end(b)<=as_of]
    expected_start = max(start, frozen)
    expected_minutes = max(0,int((as_of-expected_start)/60000))
    return {
        "minutes": minutes, "state":state, "score":score, "sides":sides,
        "assigned_shares":v, "assigned_dollar_volume":d, "neutral_notional":neutral_notional,
        "volume_pct_adv20":100*v/base["adv20"] if base["adv20"] else None,
        "dollar_pct_addv20":100*d/base["addv20"] if base["addv20"] else None,
        "same_time_rvol":None, "same_time_rvol_reason":"historical minute profile not supplied",
        "lower_band_activity":band_activity(lower), "upper_band_activity":band_activity(upper),
        "path":path_summary(window,hi-lo),
        "ceiling_observations":boundary_summary(window,upper,hi-lo,as_of),
        "eligible_window_minutes":expected_minutes, "observed_window_bars":len(window),
        "window_complete":expected_minutes==minutes and len(window)==minutes,
        "range_position": (last["c"]-lo)/(hi-lo) if last else None,
        "net_displacement_ranges": ((completed[-1]["c"]-completed[0]["o"])/(hi-lo)) if completed else None,
        "last_price":last["c"] if last else None,
        "volume_membership":"whole bars whose VWAP falls in corridor; approximate, not volume-at-price",
    }

def evaluate(data):
    as_of=int(data["as_of"])
    results=[]
    config=data.get("config",{})
    half=float(config.get("half_life_minutes",5))
    minimum=int(config.get("min_directional_bars",3))
    if half<=0 or minimum<1:
        raise ValueError("invalid config")
    for item in data["tickers"]:
        bars=item["bars"]; validate_bars(bars); validate_bars(item["daily"])
        # Trim future rows before any result or digest is constructed.
        past=[b for b in bars if minute_end(b)<=as_of and regular(b)
              and datetime.fromtimestamp(b["t"]/1000,ET).date().isoformat()==data["session"]]
        daily=[b for b in item["daily"] if datetime.fromtimestamp(b["t"]/1000,ET).date().isoformat()<data["session"]]
        base=baseline(daily,data["session"])
        for zone in item["zones"]:
            if zone["frozen_at"]>as_of:
                continue
            row={"ticker":item["ticker"],"zone_id":zone["id"],"zone":zone,
                 "as_of":as_of,"session":data["session"],"baseline":base}
            row["windows"]={}
            for n in (5,15):
                current=zone_metrics(past,zone,as_of,n,base,half,minimum)
                prior=zone_metrics(past,zone,as_of-n*60000,n,base,half,minimum)
                current["previous_score"]=prior["score"]
                current["score_change"]=(current["score"]-prior["score"]
                                        if current["score"] is not None and prior["score"] is not None else None)
                row["windows"][str(n)]=current
            row["input_hash"]=digest({"bars":past,"daily":daily,"zone":zone,"config":config})
            results.append(row)
    out={"schema":VERSION,"method_version":"1.1.0", "method_hash":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),"as_of":as_of,"session":data["session"],
         "currency":"USD","source":data.get("source"),"config":config,"rows":results,
         "limitations":["Descriptive efficiency, not signed buying/selling or a probability",
                        "Overlapping zones cannot be summed",
                        "5-minute score may be null when directional evidence is inadequate",
                        "Zones are supplied/frozen; automatic clustering and independent touch counts not implemented",
                        "No live ingestion or persistent scheduled worker",
                        "Score above 1 means upward travel more efficient, not necessarily rising net price"]}
    out["snapshot_id"]=digest(out)
    return out

def append_snapshot(path, out):
    path=Path(path)
    seen=[]
    if path.exists():
        seen=[json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    if any(x["snapshot_id"]==out["snapshot_id"] for x in seen):
        return False
    # Revised inputs create another immutable revision, not an overwrite.
    prior=[x["snapshot_id"] for x in seen if x["as_of"]==out["as_of"]]
    record=dict(out, supersedes_snapshot_id=prior[-1] if prior else None)
    with path.open("a") as f:
        f.write(json.dumps(record,sort_keys=True,allow_nan=False)+"\n")
    return True

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("input"); parser.add_argument("--out",required=True)
    parser.add_argument("--history")
    args=parser.parse_args()
    result=evaluate(json.loads(Path(args.input).read_text()))
    Path(args.out).write_text(json.dumps(result,indent=2,allow_nan=False)+"\n")
    if args.history: append_snapshot(args.history,result)
    print(json.dumps({"snapshot_id":result["snapshot_id"],"rows":len(result["rows"])},sort_keys=True))

if __name__=="__main__": main()


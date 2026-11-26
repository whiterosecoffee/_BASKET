"""Separate read-only component using only the verified access boundary."""
import argparse
import json
if __package__:
    from .flow import read_verified
else:
    from flow import read_verified


def summary(directory, **request):
    rows, receipt = read_verified(directory, **request)
    return {'format': 'basket.partition_summary@1', 'rows': len(rows),
            'ticker': receipt['ticker'], 'session': receipt['session'],
            'source_mode': receipt['source_mode'], 'source_sha256': receipt['source_sha256'],
            'partition_sha256': receipt['partition_sha256'],
            'first_t': rows[0]['t'], 'last_t': rows[-1]['t'],
            'fractional_volume_rows': sum(row['v'] != int(row['v']) for row in rows),
            'claim': 'historical observed bars; not live or complete-session certification'}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('directory')
    for field in ('ticker', 'session', 'as-of', 'expected-source-sha256'):
        p.add_argument('--' + field, required=True)
    p.add_argument('--allow-synthetic', action='store_true')
    args = vars(p.parse_args())
    print(json.dumps(summary(**args), sort_keys=True))

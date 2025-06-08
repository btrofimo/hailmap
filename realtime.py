#!/usr/bin/env python3
"""Simple real-time downloader for new MRMS MESH files."""
import argparse
import os
import time
import boto3

BUCKET = 'noaa-mrms-pds'
PREFIX = 'MESHMax/'


def watch(prefix: str, interval: int, out_dir: str) -> None:
    s3 = boto3.client('s3')
    seen = set()
    os.makedirs(out_dir, exist_ok=True)
    while True:
        resp = s3.list_objects_v2(Bucket=BUCKET, Prefix=prefix)
        for obj in resp.get('Contents', []):
            key = obj['Key']
            if not key.endswith('.gz'):
                continue
            if key in seen:
                continue
            seen.add(key)
            local = os.path.join(out_dir, os.path.basename(key))
            print(f'Downloading {key} to {local}')
            s3.download_file(BUCKET, key, local)
        time.sleep(interval)


def main() -> None:
    p = argparse.ArgumentParser(description="Watch MRMS bucket for new files")
    p.add_argument('--prefix', default=PREFIX)
    p.add_argument('--interval', type=int, default=300)
    p.add_argument('--out-dir', default='data')
    args = p.parse_args()
    watch(args.prefix, args.interval, args.out_dir)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Simple real-time downloader for new MRMS MESH files."""
import argparse
import os
import time
import boto3

from botocore import UNSIGNED
from botocore.client import Config

BUCKET = 'noaa-mrms-pds'
DEFAULT_PREFIX = 'MESH_Max_1440min_00.50/'


def watch(prefix: str, interval: int, out_dir: str) -> None:
    # Create an anonymous (unsigned) S3 client to allow public bucket access without credentials
    s3 = boto3.client('s3', config=Config(signature_version=UNSIGNED))
    seen = set()
    os.makedirs(out_dir, exist_ok=True)
    while True:
        try:
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
        except KeyboardInterrupt:
            print("Stopping watch loop.")
            break


def main() -> None:
    p = argparse.ArgumentParser(description="Watch MRMS bucket for new files")
    p.add_argument('--prefix', default=DEFAULT_PREFIX)
    p.add_argument('--interval', type=int, default=300)
    p.add_argument('--out-dir', default='data')
    args = p.parse_args()
    watch(args.prefix, args.interval, args.out_dir)


if __name__ == '__main__':
    main()

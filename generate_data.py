#!/usr/bin/env python3
"""
Master entrypoint to execute the synthetic data pipeline and verify reproducibility.

Usage:
  python generate_data.py --scale full
  python generate_data.py --scale starter
  python generate_data.py --verify
"""
import sys
import os

# Add backend directory to PYTHONPATH
backend_dir = os.path.join(os.path.dirname(__file__), "backend")
sys.path.insert(0, backend_dir)

from data.generators.pipeline import run_pipeline
from data.generators.config import FIXED_SEED

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate synthetic supply chain datasets")
    parser.add_argument("--scale", choices=["starter", "medium", "full"], default="starter", help="Volume scale")
    parser.add_argument("--seed", type=int, default=FIXED_SEED, help="Fixed random seed")
    parser.add_argument("--verify", action="store_true", help="Run dual execution and verify identical MD5 checksums")
    args = parser.parse_args()

    if args.verify:
        print("[*] Running Dual-Seed Reproducibility Verification...")
        print(f"[*] Execution 1 (Seed: {args.seed})...")
        _, md5_1 = run_pipeline(scale_name=args.scale, seed=args.seed, export=False)
        print(f"[*] Execution 2 (Seed: {args.seed})...")
        _, md5_2 = run_pipeline(scale_name=args.scale, seed=args.seed, export=False)

        print("\n" + "=" * 60)
        print(f"Run 1 Checksum: {md5_1}")
        print(f"Run 2 Checksum: {md5_2}")
        if md5_1 == md5_2:
            print("REPRODUCIBILITY VERIFICATION: PASSED (100% Deterministic Match)")
        else:
            print("REPRODUCIBILITY VERIFICATION: FAILED")
            sys.exit(1)
        print("=" * 60)
    else:
        run_pipeline(scale_name=args.scale, seed=args.seed, export=True)

if __name__ == "__main__":
    main()


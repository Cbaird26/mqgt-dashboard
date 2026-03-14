#!/usr/bin/env python3
"""CLI for mqgt-dashboard."""

import argparse
from pathlib import Path
from mqgtdashboard.fusion import load_all_channel_bounds, compute_joint_exclusion, generate_dashboard_json
from mqgtapischema.validate_csv import save_joint_bounds_csv


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description='Generate joint scalar constraints')
    parser.add_argument('--output-dir', default='results/scalar_constraints', help='Output directory')
    
    args = parser.parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Define channel files (would come from config in production)
    channel_files = {
        'fifth_force': str(output_dir / 'fifth_force_bounds.csv'),
        'collider': str(output_dir / 'collider_higgs_bounds.csv'),
    }
    
    print("Loading channel bounds...")
    all_bounds = load_all_channel_bounds(channel_files)
    available = {k: v for k, v in all_bounds.items() if v}
    print(f"Available channels: {list(available.keys())}")
    
    if not available:
        print("Error: No channel bounds found")
        return
    
    print("Computing joint exclusion...")
    joint_bounds = compute_joint_exclusion(available, method='union')
    
    # Save CSV
    csv_path = output_dir / 'joint_bounds.csv'
    with open(csv_path, 'w') as f:
        from mqgtapischema.validate_csv import BOUNDS_CSV_SCHEMA
        writer = csv.DictWriter(f, fieldnames=BOUNDS_CSV_SCHEMA["required_columns"])
        writer.writeheader()
        for bound in joint_bounds:
            writer.writerow(bound)
    print(f"Saved joint bounds: {csv_path}")
    
    # Generate dashboard
    dashboard_path = output_dir / 'joint_dashboard.json'
    generate_dashboard_json(joint_bounds, available, str(dashboard_path))
    print(f"Generated dashboard: {dashboard_path}")


if __name__ == '__main__':
    import csv
    main()

"""Joint Constraint Fusion Module
Combines constraints from multiple channels to produce joint exclusion plots
"""

import csv
import json
import math
from pathlib import Path
from typing import Dict, List, Tuple, Optional


def load_channel_bounds(csv_path: str) -> List[Dict]:
    """Load bounds from a channel CSV file."""
    bounds = []
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            bounds.append({
                'm_c_GeV': float(row['m_c_GeV']),
                'lambda_m': float(row.get('lambda_m', 0)),
                'theta_max': float(row['theta_max']),
                'kappa_vc_max_GeV': float(row['kappa_vc_max_GeV']),
                'domain_min': float(row.get('domain_min', 0)),
                'domain_max': float(row.get('domain_max', float('inf'))),
                'channel_name': row.get('channel_name', 'unknown')
            })
    return bounds


def load_all_channel_bounds(channel_files: Dict[str, str]) -> Dict[str, List[Dict]]:
    """Load bounds from all channel CSV files."""
    all_bounds = {}
    for channel_name, file_path in channel_files.items():
        if Path(file_path).exists():
            all_bounds[channel_name] = load_channel_bounds(file_path)
        else:
            print(f"Warning: Channel file not found: {file_path}")
            all_bounds[channel_name] = []
    return all_bounds


def compute_joint_exclusion(
    all_bounds: Dict[str, List[Dict]],
    method: str = 'union'
) -> List[Dict]:
    """Combine constraints from multiple channels."""
    m_c_values = set()
    for channel_bounds in all_bounds.values():
        for bound in channel_bounds:
            m_c_values.add(bound['m_c_GeV'])
    
    m_c_values = sorted(m_c_values)
    joint_bounds = []
    
    for m_c in m_c_values:
        channel_limits = {}
        for channel_name, bounds in all_bounds.items():
            closest = None
            min_diff = float('inf')
            for bound in bounds:
                diff = abs(bound['m_c_GeV'] - m_c)
                if diff < min_diff:
                    min_diff = diff
                    closest = bound
            
            if closest and abs(closest['m_c_GeV'] - m_c) < 1e-15:
                channel_limits[channel_name] = {
                    'theta_max': closest['theta_max'],
                    'kappa_vc_max': closest['kappa_vc_max_GeV']
                }
        
        if not channel_limits:
            continue
        
        if method == 'union':
            theta_max = min([lim['theta_max'] for lim in channel_limits.values()])
            kappa_vc_max = min([lim['kappa_vc_max'] for lim in channel_limits.values()])
        else:
            theta_max = max([lim['theta_max'] for lim in channel_limits.values()])
            kappa_vc_max = max([lim['kappa_vc_max'] for lim in channel_limits.values()])
        
        hbar_c_gev_m = 1.973e-13
        lambda_m = hbar_c_gev_m / m_c if m_c > 0 else 0
        
        joint_bounds.append({
            'm_c_GeV': m_c,
            'lambda_m': lambda_m,
            'theta_max': theta_max,
            'kappa_vc_max_GeV': kappa_vc_max,
            'domain_min': 0,
            'domain_max': float('inf'),
            'channel_name': 'joint'
        })
    
    return joint_bounds


def generate_dashboard_json(
    joint_bounds: List[Dict],
    channel_bounds: Dict[str, List[Dict]],
    output_path: str
) -> None:
    """Generate dashboard JSON with allowed region and metrics."""
    m_c_values = [b['m_c_GeV'] for b in joint_bounds]
    kappa_vc_values = [b['kappa_vc_max_GeV'] for b in joint_bounds]
    
    dashboard = {
        'version': '1.0',
        'allowed_region': {
            'num_points': len(joint_bounds),
            'min_m_c': min(m_c_values) if m_c_values else None,
            'max_m_c': max(m_c_values) if m_c_values else None,
            'min_kappa_vc': min(kappa_vc_values) if kappa_vc_values else None,
            'max_kappa_vc': max(kappa_vc_values) if kappa_vc_values else None,
        },
        'channel_coverage': {
            name: len(bounds) for name, bounds in channel_bounds.items()
        },
        'joint_bounds_summary': {
            'num_points': len(joint_bounds),
            'm_c_range': [min(m_c_values), max(m_c_values)] if m_c_values else [0, 0],
            'kappa_vc_range': [min(kappa_vc_values), max(kappa_vc_values)] if kappa_vc_values else [0, 0]
        }
    }
    
    with open(output_path, 'w') as f:
        json.dump(dashboard, f, indent=2)

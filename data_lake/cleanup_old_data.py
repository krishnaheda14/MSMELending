"""
Clean up existing datasets, keeping only CUST_MSM_00001.
Removes customer-specific files from raw/, clean/, analytics/, and logs/ directories.
"""

import os
import glob
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Define directories to clean
DIRS_TO_CLEAN = {
    'raw': os.path.join(BASE_DIR, 'raw'),
    'clean': os.path.join(BASE_DIR, 'clean'),
    'analytics': os.path.join(BASE_DIR, 'analytics'),
    'logs': os.path.join(BASE_DIR, 'logs')
}

# Customer to keep
KEEP_CUSTOMER = 'CUST_MSM_00001'

def clean_directory(dir_path, dir_name):
    """Remove all customer-specific files except CUST_MSM_00001."""
    if not os.path.exists(dir_path):
        print(f"  ⚠️  Directory not found: {dir_path}")
        return
    
    print(f"\n📂 Cleaning {dir_name}/ directory...")
    removed_count = 0
    kept_count = 0
    
    # Get all files in directory
    for filename in os.listdir(dir_path):
        filepath = os.path.join(dir_path, filename)
        
        # Skip directories
        if os.path.isdir(filepath):
            continue
        
        # Check if file is customer-specific
        # Pattern: contains CUST_MSM_XXXXX
        if 'CUST_MSM_' in filename:
            if KEEP_CUSTOMER in filename:
                print(f"  ✓ Keeping: {filename}")
                kept_count += 1
            else:
                print(f"  ✗ Removing: {filename}")
                os.remove(filepath)
                removed_count += 1
    
    print(f"  Summary: {removed_count} removed, {kept_count} kept")
    return removed_count, kept_count


def main():
    """Main cleanup function."""
    print("="*80)
    print("CLEANUP: Remove all customer datasets except CUST_MSM_00001")
    print("="*80)
    
    total_removed = 0
    total_kept = 0
    
    for dir_name, dir_path in DIRS_TO_CLEAN.items():
        removed, kept = clean_directory(dir_path, dir_name)
        total_removed += removed
        total_kept += kept
    
    print("\n" + "="*80)
    print("CLEANUP SUMMARY")
    print("="*80)
    print(f"✗ Total files removed: {total_removed}")
    print(f"✓ Total files kept: {total_kept}")
    print(f"\nOnly {KEEP_CUSTOMER} data remains.")
    print("="*80)


if __name__ == '__main__':
    main()

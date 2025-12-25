#!/usr/bin/env python3
"""
Data Migration Script - Move alfred_data to C:/Drive/data

This script safely migrates ALFRED data from the project directory
to the centralized PathManager location.

BEFORE:
  C:\Alfred_UBX\alfred_data\
    └── alfred_brain.db
    └── chroma_db/
    └── cache/
    └── ...

AFTER:
  C:\Drive\data\
    └── alfred_brain.db
    └── chroma_db/
    └── cache/
    └── ...

The old alfred_data directory is renamed to alfred_data.backup after migration.
"""

import os
import shutil
from pathlib import Path
from datetime import datetime


def migrate_data():
    """
    Migrate data from project directory to C:/Drive/data
    """
    # Source and destination
    source_dir = Path("alfred_data")
    from core.path_manager import PathManager
    dest_dir = PathManager.DATA_DIR

    print("="*60)
    print("ALFRED Data Migration Script")
    print("="*60)
    print(f"\nSource:      {source_dir.absolute()}")
    print(f"Destination: {dest_dir}")

    # Check if source exists
    if not source_dir.exists():
        print("\n✅ No migration needed - alfred_data directory doesn't exist")
        print(f"✅ Data will be stored in: {dest_dir}")
        return

    # Check if source is empty
    source_files = list(source_dir.rglob('*'))
    if not source_files:
        print("\n✅ alfred_data is empty - removing directory")
        source_dir.rmdir()
        print(f"✅ Data will be stored in: {dest_dir}")
        return

    print(f"\nFound {len(source_files)} files/directories to migrate")

    # Confirm migration
    print("\n⚠️  This will:")
    print(f"   1. Copy all data from {source_dir} to {dest_dir}")
    print(f"   2. Rename {source_dir} to alfred_data.backup")
    print("\nProceed? (yes/no): ", end='')

    response = input().strip().lower()
    if response not in ['yes', 'y']:
        print("\n❌ Migration cancelled")
        return

    # Ensure destination exists
    dest_dir.mkdir(parents=True, exist_ok=True)

    # Copy all files and directories
    print(f"\n📦 Copying data to {dest_dir}...")
    copied_count = 0
    error_count = 0

    for item in source_dir.iterdir():
        try:
            dest_item = dest_dir / item.name

            if item.is_file():
                # Copy file
                shutil.copy2(item, dest_item)
                print(f"   ✓ {item.name}")
                copied_count += 1
            elif item.is_dir():
                # Copy directory
                if dest_item.exists():
                    # Merge directories
                    shutil.copytree(item, dest_item, dirs_exist_ok=True)
                else:
                    shutil.copytree(item, dest_item)
                print(f"   ✓ {item.name}/")
                copied_count += 1
        except Exception as e:
            print(f"   ✗ Failed to copy {item.name}: {e}")
            error_count += 1

    # Rename source directory
    backup_name = f"alfred_data.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    backup_path = Path(backup_name)

    print(f"\n📁 Renaming {source_dir} to {backup_name}...")
    try:
        source_dir.rename(backup_path)
        print(f"   ✓ Backup created at {backup_path}")
    except Exception as e:
        print(f"   ✗ Failed to rename: {e}")
        print(f"   ⚠️  Please manually rename {source_dir}")
        error_count += 1

    # Summary
    print("\n" + "="*60)
    print("Migration Complete!")
    print("="*60)
    print(f"✓ Copied:  {copied_count} items")
    if error_count > 0:
        print(f"✗ Errors:  {error_count} items")
    print(f"\n✅ ALFRED will now use: {dest_dir}")
    print(f"📦 Backup location:     {backup_path}")
    print("\nYou can safely delete the backup directory after verifying")
    print("that everything works correctly.")
    print("="*60)


def verify_migration():
    """
    Verify that data was migrated correctly
    """
    from core.path_manager import PathManager
    dest_dir = PathManager.DATA_DIR

    print("\n" + "="*60)
    print("Verifying Migration")
    print("="*60)

    # Check for brain database
    brain_db = PathManager.BRAIN_DB
    if brain_db.exists():
        size_mb = brain_db.stat().st_size / (1024**2)
        print(f"✓ Brain database found: {brain_db}")
        print(f"  Size: {size_mb:.2f} MB")
    else:
        print(f"⚠️  Brain database not found at {brain_db}")

    # Check for ChromaDB
    chroma_db = dest_dir / "chroma_db"
    if chroma_db.exists():
        print(f"✓ ChromaDB found: {chroma_db}")
    else:
        print(f"ℹ️  ChromaDB not found (may not have been created yet)")

    # Check for other directories
    for subdir in ['cache', 'vector_store', 'conversations', 'knowledge']:
        path = dest_dir / subdir
        if path.exists():
            file_count = len(list(path.rglob('*')))
            print(f"✓ {subdir}: {file_count} files")

    print("="*60)


if __name__ == "__main__":
    try:
        migrate_data()
        verify_migration()
    except KeyboardInterrupt:
        print("\n\n❌ Migration cancelled by user")
    except Exception as e:
        print(f"\n\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()

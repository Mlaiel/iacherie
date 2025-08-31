#!/usr/bin/env python3
"""Batch Python syntax fixer for industrial-scale repositories

This script efficiently fixes common syntax errors across thousands of Python files
using optimized patterns and parallel processing.
"""

import ast
import sys
import re
import multiprocessing as mp
from pathlib import Path
from typing import List, Tuple, Dict
import logging
from concurrent.futures import ProcessPoolExecutor, as_completed
import time

class BatchSyntaxFixer:
    """Industrial-scale syntax fixer for Python repositories"""
    
    def __init__(self, max_workers: int = None):
        self.max_workers = max_workers or min(32, mp.cpu_count())
        self.logger = self._setup_logging()
        self.stats = {
            'total_files': 0,
            'processed_files': 0,
            'fixed_files': 0,
            'failed_files': 0,
            'skipped_files': 0
        }
    
    def _setup_logging(self):
        """Setup logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)
    
    def fix_single_file(self, file_path: Path) -> Tuple[str, bool, str]:
        """Fix syntax errors in a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Apply fixes in order of likelihood and safety
            
            # Fix 1: Replace problematic unicode characters
            content = content.replace('©', '(c)')
            content = content.replace('®', '(R)') 
            content = content.replace('™', '(TM)')
            
            # Fix 2: The most common issue - missing newline after docstring before import/code
            # Pattern: """docstring"""
import -> """docstring"""\nimport
            content = re.sub(r'("""[^"]*?""")([a-zA-Z_])', r'\1\n\2', content)
            content = re.sub(r"('''[^']*?''')([a-zA-Z_])", r"\1\n\2", content)
            
            # Fix 3: Missing newline after class/function docstrings
            # Pattern: """docstring"""
    VARIABLE = -> """docstring"""\n    VARIABLE =
            content = re.sub(r'("""[^"]*?""")(\s+)([A-Z_][A-Z0-9_]*\s*=)', r'\1\n\2\3', content)
            content = re.sub(r"('''[^']*?''')(\s+)([A-Z_][A-Z0-9_]*\s*=)", r"\1\n\2\3", content)
            
            # Fix 4: Ensure proper spacing around imports
            content = re.sub(r'"""\nimport', '"""\n\nimport', content)
            content = re.sub(r'"""\nfrom', '"""\n\nfrom', content)
            
            # Only proceed if we made changes
            if content != original_content:
                # Verify the fix doesn't break syntax
                try:
                    ast.parse(content)
                    
                    # Create backup
                    backup_path = file_path.with_suffix('.py.backup')
                    with open(backup_path, 'w', encoding='utf-8') as f:
                        f.write(original_content)
                    
                    # Write fixed content
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    return str(file_path), True, "Fixed successfully"
                    
                except SyntaxError as e:
                    return str(file_path), False, f"Fix introduced new syntax error: {e}"
            else:
                # Check if original content has syntax errors
                try:
                    ast.parse(content)
                    return str(file_path), True, "Already valid"
                except SyntaxError as e:
                    return str(file_path), False, f"Unfixable syntax error: {e}"
                    
        except Exception as e:
            return str(file_path), False, f"Processing error: {e}"

def process_file_batch(file_paths: List[Path]) -> List[Tuple[str, bool, str]]:
    """Process a batch of files"""
    fixer = BatchSyntaxFixer()
    results = []
    
    for file_path in file_paths:
        result = fixer.fix_single_file(file_path)
        results.append(result)
    
    return results

class IndustrialSyntaxFixer:
    """Industrial-scale syntax fixer with parallel processing"""
    
    def __init__(self, root_path: str = ".", max_workers: int = None):
        self.root_path = Path(root_path)
        self.max_workers = max_workers or min(32, mp.cpu_count())
        self.logger = self._setup_logging()
        self.results = []
    
    def _setup_logging(self):
        """Setup logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)
    
    def find_python_files(self) -> List[Path]:
        """Find all Python files in the repository"""
        self.logger.info("🔍 Scanning for Python files...")
        
        exclude_dirs = {
            '.git', '__pycache__', '.pytest_cache', 'node_modules',
            'venv', '.venv', 'env', '.env', 'dist', 'build',
            '.tox', '.coverage', 'htmlcov'
        }
        
        python_files = []
        for py_file in self.root_path.rglob("*.py"):
            if any(excluded in py_file.parts for excluded in exclude_dirs):
                continue
            
            # Skip very large files (>1MB)
            try:
                if py_file.stat().st_size > 1024 * 1024:
                    continue
            except OSError:
                continue
                
            python_files.append(py_file)
        
        self.logger.info(f"📊 Found {len(python_files)} Python files")
        return python_files
    
    def process_files_parallel(self, python_files: List[Path], batch_size: int = 100) -> Dict[str, int]:
        """Process files in parallel batches"""
        self.logger.info(f"🚀 Processing {len(python_files)} files with {self.max_workers} workers...")
        
        # Split files into batches
        batches = [python_files[i:i + batch_size] for i in range(0, len(python_files), batch_size)]
        
        stats = {
            'total_files': len(python_files),
            'processed_files': 0,
            'fixed_files': 0,
            'failed_files': 0,
            'already_valid_files': 0
        }
        
        start_time = time.time()
        
        # Process batches in parallel
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_batch = {executor.submit(process_file_batch, batch): batch for batch in batches}
            
            for i, future in enumerate(as_completed(future_to_batch)):
                try:
                    batch_results = future.result()
                    self.results.extend(batch_results)
                    
                    # Update stats
                    for file_path, success, message in batch_results:
                        stats['processed_files'] += 1
                        if success:
                            if "Fixed successfully" in message:
                                stats['fixed_files'] += 1
                            else:
                                stats['already_valid_files'] += 1
                        else:
                            stats['failed_files'] += 1
                    
                    # Progress update
                    if (i + 1) % 10 == 0 or (i + 1) == len(batches):
                        elapsed = time.time() - start_time
                        progress = (i + 1) / len(batches) * 100
                        self.logger.info(f"📊 Progress: {progress:.1f}% ({i + 1}/{len(batches)} batches, "
                                       f"{stats['processed_files']}/{stats['total_files']} files, "
                                       f"{elapsed:.1f}s elapsed)")
                        
                except Exception as e:
                    self.logger.error(f"❌ Batch processing error: {e}")
        
        elapsed = time.time() - start_time
        self.logger.info(f"⏱️  Processing completed in {elapsed:.2f} seconds")
        
        return stats
    
    def print_summary(self, stats: Dict[str, int]):
        """Print summary of the batch fixing operation"""
        print("\n" + "=" * 80)
        print("🏭 INDUSTRIAL BATCH SYNTAX FIXING RESULTS")
        print("=" * 80)
        print(f"📊 Files Statistics:")
        print(f"   • Total files found: {stats['total_files']:,}")
        print(f"   • Files processed: {stats['processed_files']:,}")
        print(f"   • Files fixed: {stats['fixed_files']:,}")
        print(f"   • Files already valid: {stats['already_valid_files']:,}")
        print(f"   • Files that failed to fix: {stats['failed_files']:,}")
        
        # Calculate rates
        if stats['total_files'] > 0:
            success_rate = ((stats['fixed_files'] + stats['already_valid_files']) / stats['total_files']) * 100
            fix_rate = (stats['fixed_files'] / stats['total_files']) * 100
            print(f"\n📈 Success Metrics:")
            print(f"   • Overall success rate: {success_rate:.2f}%")
            print(f"   • Fix application rate: {fix_rate:.2f}%")
        
        # Show sample of fixes and failures
        fixed_files = [r for r in self.results if r[1] and "Fixed successfully" in r[2]]
        failed_files = [r for r in self.results if not r[1]]
        
        if fixed_files:
            print(f"\n✅ Sample of fixed files:")
            for file_path, _, _ in fixed_files[:5]:
                print(f"   • {file_path}")
            if len(fixed_files) > 5:
                print(f"   ... and {len(fixed_files) - 5} more")
        
        if failed_files:
            print(f"\n❌ Sample of failed files:")
            for file_path, _, message in failed_files[:5]:
                print(f"   • {file_path}: {message}")
            if len(failed_files) > 5:
                print(f"   ... and {len(failed_files) - 5} more")
        
        print("=" * 80)
    
    def run_industrial_fix(self) -> Dict[str, int]:
        """Run the industrial-scale syntax fixing operation"""
        python_files = self.find_python_files()
        
        if not python_files:
            self.logger.warning("No Python files found to process")
            return {'total_files': 0, 'processed_files': 0, 'fixed_files': 0, 'failed_files': 0, 'already_valid_files': 0}
        
        stats = self.process_files_parallel(python_files)
        return stats


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Industrial-scale Python syntax fixer")
    parser.add_argument("--root", default=".", help="Root directory to process")
    parser.add_argument("--workers", type=int, help="Number of parallel workers")
    parser.add_argument("--batch-size", type=int, default=100, help="Batch size for processing")
    
    args = parser.parse_args()
    
    try:
        fixer = IndustrialSyntaxFixer(args.root, args.workers)
        stats = fixer.run_industrial_fix()
        fixer.print_summary(stats)
        
        # Return appropriate exit code
        if stats['failed_files'] == 0:
            print("\n🎉 All files processed successfully!")
            return 0
        elif stats['fixed_files'] > 0:
            print(f"\n⚠️  {stats['fixed_files']} files fixed, {stats['failed_files']} still have issues")
            return 0
        else:
            print("\n❌ No files were successfully fixed")
            return 1
            
    except KeyboardInterrupt:
        print("\n⏹️  Operation interrupted by user")
        return 130
    except Exception as e:
        print(f"\n❌ Operation failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
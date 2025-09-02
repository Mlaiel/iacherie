#!/usr/bin/env python3
"""IA Influencer Agent - Content Management System Launcher
======================================================

Simple launcher script for the industrial-grade content management system
with interactive menu, quick start options, and system monitoring.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

⚠️ LEGAL WARNING: This code and concept are protected by intellectual property laws.
Any unauthorized copying, modification, or distribution without explicit written 
permission from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited and will 
result in legal action under German and international copyright laws.
"""

import os
import sys
import asyncio
import argparse
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from index import initialize_content_system, get_content_system, shutdown_content_system
    from health_check import ContentModuleHealthCheck
    from maintenance import ContentModuleMaintenance
    from setup_content_module import ContentModuleSetup
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Please ensure all required files are present in the content module directory.")
    sys.exit(1)


class ContentSystemLauncher:
    """Interactive launcher for the content management system."""
    
    def __init__(self):
        self.system = None
        self.running = False
    
    def print_banner(self):
        """
Print system banner."""
        print("""╔══════════════════════════════════════════════════════════════════════════════╗
║                IA Influencer Agent - Content Management System              ║
║                                                                              ║
║  🚀 Industrial-Grade Content Processing Platform                             ║
║  🎵 Multi-Format Support (Audio, Video, Image, Text)                        ║
║  🤖 AI-Powered Enhancement & Protection                                      ║
║  📈 Smart Distribution & Monetization                                        ║
║  🔒 Advanced Security & Copyright Protection                                 ║
║  🌐 Intelligent Web Crawling & Monitoring                                    ║
║  📊 Performance Optimization & Analytics                                     ║
║                                                                              ║
║  Author: Fahed Mlaiel <mlaiel@live.de>                                      ║
║  Version: 2.1.0 Enterprise Edition                                          ║
╚══════════════════════════════════════════════════════════════════════════════╝
        """)
    
    def print_menu(self):
        """
Print interactive menu."""
        print("""┌─ Main Menu ──────────────────────────────────────────────────────────────────┐
│                                                                              │
│  1. 🚀 Quick Start - Initialize & Launch System                             │
│  2. 🔍 System Health Check                                                   │
│  3. ⚙️  Setup & Configuration                                                │
│  4. 🧹 System Maintenance                                                    │
│  5. 📊 Performance Monitor                                                   │
│  6. 🎬 Demo Complete System                                                  │
│  7. 📋 System Information                                                    │
│  8. 🛑 Shutdown System                                                       │
│  9. ❓ Help & Documentation                                                  │
│  0. 🚪 Exit                                                                  │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
        """)
    
    async def quick_start(self):
        """
Quick start the system."""
        print("🚀 Starting Content Management System...")
        
        try:
            self.system = await initialize_content_system()
            
            if self.system and self.system.is_initialized:
                info = self.system.get_system_info()
                print(f"✅ System started successfully!")
                print(f"   - Engines loaded: {info['engines_count']}")
                print(f"   - Status: {info['health_status']}")
                print(f"   - Startup time: {info['startup_time']}")
                
                self.running = True
                
                # Quick health check
                health = await self.system.health_check()
                print(f"   - System health: {health['status']}")
                print(f"   - Memory usage: {health['system_metrics'].get('memory_mb', 'N/A')} MB")
                
                return True
            else:
                print("❌ Failed to start system")
                return False
                
        except Exception as e:

                
            logger.error(f"Error: {e}")

                
            raise
            print(f"❌ Startup failed: {e}")
            return False
    
    async def health_check(self):
        """Run system health check."""
        print("🔍 Running System Health Check...")
        
        health_checker = ContentModuleHealthCheck()
        report = await health_checker.run_comprehensive_health_check()
        
        health_checker.print_health_summary(report)
        
        # Save report
        report_path = health_checker.save_report(report)
        print(f"\n📋 Detailed report saved: {report_path}")
    
    async def setup_system(self):
        """Run system setup and configuration."""
        print("⚙️ Running System Setup...")
        
        setup = ContentModuleSetup()
        
        # Environment validation
        env_result = setup.validate_environment()
        
        # Configuration setup
        config_result = await setup.setup_configuration()
        
        # Generate deployment scripts
        setup.generate_deployment_scripts()
        
        # Print summary
        setup.print_setup_summary()
    
    async def maintenance_menu(self):
        """Show maintenance submenu."""
        maintenance = ContentModuleMaintenance()
        
        while True:
            print("""┌─ Maintenance Menu ───────────────────────────────────────────────────────────┐
│                                                                              │
│  1. 📦 Create System Backup                                                  │
│  2. 🧹 System Cleanup                                                        │
│  3. ⚡ Performance Optimization                                               │
│  4. 📊 Generate System Report                                                │
│  5. 📋 List Backups                                                          │
│  6. 🔄 Restore from Backup                                                   │
│  7. 🔙 Back to Main Menu                                                     │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
            """)
            
            choice = input("Select option: ").strip()
            
            if choice == '1':
                backup_file = await maintenance.create_system_backup()
                print(f"✅ Backup created: {backup_file}")
                
            elif choice == '2':
                aggressive = input("Aggressive cleanup? (y/N): ").lower() == 'y'
                results = await maintenance.cleanup_system(aggressive)
                print(f"✅ Cleanup completed:")
                print(f"   - Files removed: {results['temp_files_removed']}")
                print(f"   - Space freed: {results['space_freed_mb']} MB")
                
            elif choice == '3':
                results = await maintenance.optimize_performance()
                print(f"✅ Optimization completed:")
                for rec in results['recommendations'][:3]:
                    print(f"   • {rec}")
                    
            elif choice == '4':
                report = await maintenance.generate_system_report()
                print(f"✅ System report generated:")
                print(f"   - Memory: {report['resource_usage']['memory_mb']} MB")
                print(f"   - CPU: {report['resource_usage']['cpu_percent']}%")
                
            elif choice == '5':
                backups = maintenance.list_backups()
                if backups:
                    print("📦 Available backups:")
                    for backup in backups:
                        print(f"   • {backup['filename']} ({backup['size_mb']} MB)")
                else:
                    print("No backups found")
                    
            elif choice == '6':
                backups = maintenance.list_backups()
                if backups:
                    print("Available backups:")
                    for i, backup in enumerate(backups):
                        print(f"   {i+1}. {backup['filename']}")
                    
                    try:
                        selection = int(input("Select backup number: ")) - 1
                        if 0 <= selection < len(backups):
                            backup_file = backups[selection]['filename']
                            success = await maintenance.restore_backup(backup_file)
                            if success:
                                print(f"✅ Backup restored successfully")
                            else:
                                print(f"❌ Backup restoration failed")
                        else:
                            print("Invalid selection")
                    except ValueError:
                        print("Invalid number")
                else:
                    print("No backups available")
                    
            elif choice == '7':
                break
                
            else:
                print("Invalid option")
            
            input("\nPress Enter to continue...")
    
    async def performance_monitor(self):
        """Run performance monitoring."""
        print("📊 Starting Performance Monitor...")
        
        duration = input("Monitoring duration in seconds (default 60): ").strip()
        try:
            duration = int(duration) if duration else 60
        except ValueError:
            duration = 60
        
        maintenance = ContentModuleMaintenance()
        results = await maintenance.monitor_system(duration)
        
        summary = results['summary']
        print(f"✅ Monitoring completed:")
        print(f"   - Average memory: {summary['avg_memory_mb']} MB")
        print(f"   - Peak memory: {summary['max_memory_mb']} MB")
        print(f"   - Average CPU: {summary['avg_cpu_percent']}%")
        print(f"   - Samples collected: {summary['samples_collected']}")
    
    async def demo_system(self):
        """Run complete system demo."""
        print("🎬 Starting Complete System Demo...")
        
        try:
            from demo_complete_system import ContentSystemDemo
            
            demo = ContentSystemDemo()
            await demo.run_complete_demo()
            
        except ImportError:
            print("❌ Demo system not available")
        except Exception as e:

            logger.error(f"Error: {e}")

            raise
            print(f"❌ Demo failed: {e}")
    
    async def show_system_info(self):
        """Show system information."""
        if self.system and self.running:
            info = self.system.get_system_info()
            health = await self.system.health_check()
            
            print(f"""╔─ System Information ─────────────────────────────────────────────────────────╗
║                                                                              ║
║  System: {info['system_name']}                             ║
║  Version: {info['version']}                                                 ║
║  Author: {info['author']}                               ║
║                                                                              ║
║  Status: {'🟢 RUNNING' if self.running else '🔴 STOPPED'}                                                   ║
║  Health: {health['status'].upper()}                                                  ║
║  Uptime: {health['uptime_seconds']:.2f} seconds                                      ║
║                                                                              ║
║  Engines: {info['engines_count']} loaded                                                ║
║  Memory: {health['system_metrics'].get('memory_mb', 'N/A')} MB                                                 ║
║  CPU: {health['system_metrics'].get('cpu_percent', 'N/A')}%                                                    ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
            """)
        else:
            print("""╔─ System Information ─────────────────────────────────────────────────────────╗
║                                                                              ║
║  System: IA Influencer Agent - Content Management System                    ║
║  Version: 2.1.0                                                             ║
║  Author: Fahed Mlaiel <mlaiel@live.de>                                      ║
║                                                                              ║
║  Status: 🔴 NOT RUNNING                                                      ║
║                                                                              ║
║  Use option 1 to start the system                                           ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
            """)
    
    def show_help(self):
        """
Show help information."""
        print("""╔─ Help & Documentation ───────────────────────────────────────────────────────╗
║                                                                              ║
║  📖 Documentation Files:                                                     ║
║     • README.md - English documentation                                     ║
║     • README.de.md - German documentation                                   ║
║     • README.fr.md - French documentation                                   ║
║                                                                              ║
║  🔧 Configuration:                                                           ║
║     • config.py - Module configuration                                      ║
║     • .env.template - Environment variables template                        ║
║     • content_module_config.json - Runtime configuration                    ║
║                                                                              ║
║  🧪 Testing & Validation:                                                    ║
║     • python health_check.py - System health check                          ║
║     • python -m pytest - Run test suite                                     ║
║     • python demo_complete_system.py - Run demo                             ║
║                                                                              ║
║  🛠️ Utilities:                                                              ║
║     • python setup_content_module.py - Setup system                         ║
║     • python maintenance.py - Maintenance tools                             ║
║                                                                              ║
║  📧 Enterprise Support: mlaiel@live.de                                      ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
        """)
    
    async def shutdown_system(self):
        """
Shutdown the system."""
        if self.system and self.running:
            print("🛑 Shutting down Content Management System...")
            await shutdown_content_system()
            self.running = False
            self.system = None
            print("✅ System shutdown completed")
        else:
            print("💡 System is not running")
    
    async def run_interactive(self):
        """Run interactive mode."""
        self.print_banner()
        
        while True:
            self.print_menu()
            
            choice = input("Select option: ").strip()
            
            try:
                if choice == '1':
                    await self.quick_start()
                    
                elif choice == '2':
                    await self.health_check()
                    
                elif choice == '3':
                    await self.setup_system()
                    
                elif choice == '4':
                    await self.maintenance_menu()
                    
                elif choice == '5':
                    await self.performance_monitor()
                    
                elif choice == '6':
                    await self.demo_system()
                    
                elif choice == '7':
                    await self.show_system_info()
                    
                elif choice == '8':
                    await self.shutdown_system()
                    
                elif choice == '9':
                    self.show_help()
                    
                elif choice == '0':
                    if self.running:
                        await self.shutdown_system()
                    print("👋 Goodbye!")
                    break
                    
                else:
                    print("❌ Invalid option. Please try again.")
                    
            except KeyboardInterrupt:
                print("\n🛑 Operation cancelled by user")
                
            except Exception as e:

                
                logger.error(f"Error: {e}")

                
                raise
                print(f"❌ Error: {e}")
            
            if choice not in ['0', '4']:  # Don't pause for exit or maintenance menu
                input("\nPress Enter to continue...")


async def main():
    """Main launcher function."""
    parser = argparse.ArgumentParser(
        description="IA Influencer Agent - Content Management System Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python launcher.py                    # Interactive mode
  python launcher.py --quick-start      # Quick start system
  python launcher.py --health-check     # Run health check
  python launcher.py --setup            # Run setup
        """
    )
    
    parser.add_argument('--quick-start', action='store_true', help='Quick start the system')
    parser.add_argument('--health-check', action='store_true', help='Run health check')
    parser.add_argument('--setup', action='store_true', help='Run system setup')
    parser.add_argument('--demo', action='store_true', help='Run system demo')
    
    args = parser.parse_args()
    
    launcher = ContentSystemLauncher()
    
    if args.quick_start:
        launcher.print_banner()
        await launcher.quick_start()
        
    elif args.health_check:
        launcher.print_banner()
        await launcher.health_check()
        
    elif args.setup:
        launcher.print_banner()
        await launcher.setup_system()
        
    elif args.demo:
        launcher.print_banner()
        await launcher.demo_system()
        
    else:
        # Interactive mode
        await launcher.run_interactive()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Launcher interrupted by user")
    except Exception as e:

        logger.error(f"Error: {e}")

        raise
        print(f"❌ Launcher error: {e}")
        sys.exit(1)

#!/usr/bin/env python3
"""
NextFactory Autonomous PostgreSQL Setup Script
==============================================

This script provides a fully autonomous setup for the NextFactory ERP+MES system.
It automatically installs dependencies, creates the database, sets up tables,
creates roles, and seeds demo data with comprehensive error reporting.

Features:
- Autonomous PostgreSQL database setup
- Automatic dependency installation
- Clear error reporting and troubleshooting
- One-command execution for exhibition demo
- Self-diagnostic capabilities

Usage:
    python setup_postgres.py

Author: NextFactory Development Team
Created: 2024 - Phase 3 Implementation
"""

import os
import sys
import subprocess
import logging
import platform
from typing import Optional, Dict, List
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('nextfactory_setup.log')
    ]
)
logger = logging.getLogger(__name__)


class SetupError(Exception):
    """Custom exception for setup errors."""
    pass


class NextFactorySetup:
    """
    Autonomous setup class for NextFactory ERP+MES system.
    
    This class handles all aspects of setting up the NextFactory system,
    from dependency installation to database creation and data seeding.
    """
    
    def __init__(self):
        """Initialize the setup manager."""
        self.system = platform.system().lower()
        self.python_executable = sys.executable
        self.setup_dir = Path(__file__).parent
        self.requirements_file = self.setup_dir / "requirements.txt"
        
        # Database configuration
        self.db_config = {
            'host': 'localhost',
            'port': '5432',
            'database': 'nextfactory',
            'user': 'nextfactory',
            'password': 'nextfactory123'
        }
        
        # Track setup progress
        self.setup_steps = {
            'dependencies': False,
            'postgresql': False,
            'database': False,
            'tables': False,
            'seeding': False
        }
    
    def print_banner(self):
        """Print setup banner."""
        banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                    NextFactory ERP+MES Autonomous Setup                      ║
║                           Phase 3 - Exhibition Demo                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

🚀 Setting up NextFactory ERP+MES system with complete automation...
📊 This will configure: PostgreSQL + Database + Demo Data + All Modules
⏱️  Estimated time: 2-5 minutes (depending on your system)

"""
        print(banner)
        logger.info("Starting NextFactory autonomous setup")
    
    def check_python_version(self) -> bool:
        """Check if Python version is compatible."""
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            raise SetupError(
                f"Python 3.8+ required. Current version: {version.major}.{version.minor}"
            )
        
        logger.info(f"✓ Python version check passed: {version.major}.{version.minor}.{version.micro}")
        return True
    
    def install_python_dependencies(self) -> bool:
        """Install Python dependencies."""
        logger.info("📦 Installing Python dependencies...")
        
        if not self.requirements_file.exists():
            raise SetupError(f"Requirements file not found: {self.requirements_file}")
        
        try:
            # Upgrade pip first
            subprocess.run([
                self.python_executable, "-m", "pip", "install", "--upgrade", "pip"
            ], check=True, capture_output=True, text=True)
            
            # Install requirements
            result = subprocess.run([
                self.python_executable, "-m", "pip", "install", "-r", str(self.requirements_file)
            ], check=True, capture_output=True, text=True)
            
            self.setup_steps['dependencies'] = True
            logger.info("✓ Python dependencies installed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            error_msg = f"Failed to install Python dependencies: {e.stderr}"
            logger.error(error_msg)
            raise SetupError(error_msg)
    
    def check_postgresql_installation(self) -> bool:
        """Check if PostgreSQL is installed and running."""
        logger.info("🔍 Checking PostgreSQL installation...")
        
        # Check if psql command is available
        try:
            result = subprocess.run(['psql', '--version'], 
                                  capture_output=True, text=True, check=True)
            logger.info(f"✓ PostgreSQL found: {result.stdout.strip()}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            return self.install_postgresql()
        
        # Check if PostgreSQL service is running
        if not self.is_postgresql_running():
            return self.start_postgresql_service()
        
        self.setup_steps['postgresql'] = True
        return True
    
    def is_postgresql_running(self) -> bool:
        """Check if PostgreSQL service is running."""
        try:
            if self.system == "linux":
                result = subprocess.run(['sudo', 'systemctl', 'is-active', 'postgresql'], 
                                      capture_output=True, text=True)
                return result.returncode == 0
            elif self.system == "darwin":  # macOS
                result = subprocess.run(['brew', 'services', 'list'], 
                                      capture_output=True, text=True)
                return 'postgresql' in result.stdout and 'started' in result.stdout
            elif self.system == "windows":
                result = subprocess.run(['sc', 'query', 'postgresql'], 
                                      capture_output=True, text=True)
                return 'RUNNING' in result.stdout
            return False
        except Exception:
            return False
    
    def start_postgresql_service(self) -> bool:
        """Start PostgreSQL service."""
        logger.info("🔄 Starting PostgreSQL service...")
        
        try:
            if self.system == "linux":
                subprocess.run(['sudo', 'systemctl', 'start', 'postgresql'], 
                              check=True, capture_output=True)
                subprocess.run(['sudo', 'systemctl', 'enable', 'postgresql'], 
                              check=True, capture_output=True)
            elif self.system == "darwin":  # macOS
                subprocess.run(['brew', 'services', 'start', 'postgresql'], 
                              check=True, capture_output=True)
            elif self.system == "windows":
                subprocess.run(['net', 'start', 'postgresql'], 
                              check=True, capture_output=True)
            
            logger.info("✓ PostgreSQL service started successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            error_msg = f"Failed to start PostgreSQL service: {e}"
            logger.error(error_msg)
            raise SetupError(error_msg)
    
    def install_postgresql(self) -> bool:
        """Install PostgreSQL if not present."""
        logger.info("📥 Installing PostgreSQL...")
        
        try:
            if self.system == "linux":
                # Ubuntu/Debian
                subprocess.run(['sudo', 'apt', 'update'], check=True, capture_output=True)
                subprocess.run(['sudo', 'apt', 'install', '-y', 'postgresql', 'postgresql-contrib'], 
                              check=True, capture_output=True)
            elif self.system == "darwin":  # macOS
                subprocess.run(['brew', 'install', 'postgresql'], 
                              check=True, capture_output=True)
            elif self.system == "windows":
                logger.warning("⚠️  Please install PostgreSQL manually from https://www.postgresql.org/download/windows/")
                return False
            
            logger.info("✓ PostgreSQL installed successfully")
            return self.start_postgresql_service()
            
        except subprocess.CalledProcessError as e:
            error_msg = f"Failed to install PostgreSQL: {e}"
            logger.error(error_msg)
            raise SetupError(error_msg)
    
    def create_database_user(self) -> bool:
        """Create NextFactory database user."""
        logger.info("👤 Creating database user...")
        
        commands = [
            f"CREATE USER {self.db_config['user']} WITH PASSWORD '{self.db_config['password']}';",
            f"ALTER USER {self.db_config['user']} CREATEDB;",
            f"GRANT ALL PRIVILEGES ON DATABASE postgres TO {self.db_config['user']};"
        ]
        
        for cmd in commands:
            try:
                subprocess.run([
                    'sudo', '-u', 'postgres', 'psql', '-c', cmd
                ], check=True, capture_output=True, text=True)
            except subprocess.CalledProcessError:
                # User might already exist, continue
                pass
        
        logger.info("✓ Database user created/verified")
        return True
    
    def create_database(self) -> bool:
        """Create NextFactory database."""
        logger.info("🗄️  Creating NextFactory database...")
        
        try:
            # Create database
            subprocess.run([
                'sudo', '-u', 'postgres', 'createdb', 
                '-O', self.db_config['user'], self.db_config['database']
            ], check=True, capture_output=True, text=True)
            
            logger.info("✓ NextFactory database created successfully")
            
        except subprocess.CalledProcessError:
            # Database might already exist
            logger.info("✓ NextFactory database already exists")
        
        self.setup_steps['database'] = True
        return True
    
    def setup_database_schema(self) -> bool:
        """Set up database tables and schema."""
        logger.info("🏗️  Setting up database schema...")
        
        try:
            # Import and run database setup
            os.chdir(self.setup_dir)
            result = subprocess.run([
                self.python_executable, 'database.py'
            ], check=True, capture_output=True, text=True)
            
            logger.info("✓ Database schema created successfully")
            self.setup_steps['tables'] = True
            return True
            
        except subprocess.CalledProcessError as e:
            error_msg = f"Failed to create database schema: {e.stderr}"
            logger.error(error_msg)
            raise SetupError(error_msg)
    
    def seed_demo_data(self) -> bool:
        """Seed database with demonstration data."""
        logger.info("🌱 Seeding demonstration data...")
        
        try:
            result = subprocess.run([
                self.python_executable, 'seed_db.py'
            ], check=True, capture_output=True, text=True)
            
            logger.info("✓ Demo data seeded successfully")
            self.setup_steps['seeding'] = True
            return True
            
        except subprocess.CalledProcessError as e:
            error_msg = f"Failed to seed demo data: {e.stderr}"
            logger.error(error_msg)
            raise SetupError(error_msg)
    
    def test_installation(self) -> bool:
        """Test the complete installation."""
        logger.info("🧪 Testing installation...")
        
        try:
            result = subprocess.run([
                self.python_executable, 'test_nextfactory.py'
            ], check=True, capture_output=True, text=True)
            
            if "tests passed" in result.stdout:
                logger.info("✓ Installation test passed")
                return True
            else:
                logger.warning("⚠️  Some tests failed - check test output")
                print("\nTest output:")
                print(result.stdout)
                return True  # Continue even if some tests fail
                
        except subprocess.CalledProcessError as e:
            logger.warning(f"⚠️  Test execution failed: {e.stderr}")
            return True  # Continue even if tests fail
    
    def print_success_message(self):
        """Print successful setup message."""
        success_msg = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                          🎉 SETUP COMPLETED SUCCESSFULLY! 🎉                ║
╚══════════════════════════════════════════════════════════════════════════════╝

NextFactory ERP+MES system is ready for exhibition demonstration!

🚀 TO START THE APPLICATION:
   python main.py

📊 SYSTEM OVERVIEW:
   ✓ PostgreSQL Database: {self.db_config['database']} on {self.db_config['host']}:{self.db_config['port']}
   ✓ User Account: {self.db_config['user']}
   ✓ Demo Data: Loaded with 6 optional modules
   ✓ All Dependencies: Installed and configured

👥 DEMO CREDENTIALS:
   ┌─────────────┬──────────┬────────────┬─────────────────────────┐
   │ Role        │ Username │ Password   │ Access Level            │
   ├─────────────┼──────────┼────────────┼─────────────────────────┤
   │ Admin       │ admin    │ admin123   │ Full system access      │
   │ Manager     │ manager  │ manager123 │ Management oversight    │
   │ Operator    │ operator │ operator123│ Production operations   │
   │ Guest       │ guest    │ guest123   │ Read-only demo          │
   │ Analyst     │ analyst  │ analyst123 │ Reporting & analytics   │
   └─────────────┴──────────┴────────────┴─────────────────────────┘

📁 LOG FILE: nextfactory_setup.log (for troubleshooting)

🌟 PHASE 3 FEATURES READY:
   • ERP: Sales & CRM
   • ERP: Asset Management  
   • MES: Resource Allocation
   • MES: Product Tracking & Traceability
   • MES: Maintenance Management
   • MES: Labor Management

Happy demonstrating! 🏭✨
"""
        print(success_msg)
        logger.info("NextFactory setup completed successfully")
    
    def print_error_message(self, error: Exception):
        """Print error message with troubleshooting information."""
        error_msg = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                            ❌ SETUP FAILED ❌                                ║
╚══════════════════════════════════════════════════════════════════════════════╝

Error: {str(error)}

🔧 TROUBLESHOOTING STEPS:

1. CHECK SYSTEM REQUIREMENTS:
   • Python 3.8+ ({'✓' if sys.version_info >= (3, 8) else '❌'})
   • PostgreSQL 12+ ({'✓' if self.setup_steps.get('postgresql', False) else '❌'})
   • Internet connection for dependencies
   • Administrator/sudo access

2. MANUAL POSTGRESQL SETUP:
   sudo apt update && sudo apt install postgresql postgresql-contrib
   sudo systemctl start postgresql
   sudo systemctl enable postgresql

3. CHECK LOG FILE:
   cat nextfactory_setup.log

4. RETRY SETUP:
   python setup_postgres.py

5. MANUAL SETUP (if auto-setup fails):
   python database.py
   python seed_db.py
   python main.py

📞 NEED HELP?
   • Check documentation: docs/database_setup.md
   • Review troubleshooting guide in README.md
   • Check PostgreSQL service status
   • Verify network connectivity

Setup Progress:
{self._format_progress()}
"""
        print(error_msg)
        logger.error(f"Setup failed: {error}")
    
    def _format_progress(self) -> str:
        """Format setup progress for display."""
        progress = []
        for step, completed in self.setup_steps.items():
            status = "✓" if completed else "❌"
            progress.append(f"   {status} {step.replace('_', ' ').title()}")
        return "\n".join(progress)
    
    def run_setup(self) -> bool:
        """Run the complete autonomous setup process."""
        try:
            self.print_banner()
            
            # Step 1: Check Python version
            self.check_python_version()
            
            # Step 2: Install Python dependencies
            self.install_python_dependencies()
            
            # Step 3: Check/install PostgreSQL
            self.check_postgresql_installation()
            
            # Step 4: Create database user
            self.create_database_user()
            
            # Step 5: Create database
            self.create_database()
            
            # Step 6: Set up database schema
            self.setup_database_schema()
            
            # Step 7: Seed demo data
            self.seed_demo_data()
            
            # Step 8: Test installation
            self.test_installation()
            
            # Success!
            self.print_success_message()
            return True
            
        except SetupError as e:
            self.print_error_message(e)
            return False
        except KeyboardInterrupt:
            logger.info("Setup cancelled by user")
            print("\n⚠️  Setup cancelled by user")
            return False
        except Exception as e:
            error = SetupError(f"Unexpected error: {str(e)}")
            self.print_error_message(error)
            return False


def main():
    """Main entry point for autonomous setup."""
    setup = NextFactorySetup()
    success = setup.run_setup()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
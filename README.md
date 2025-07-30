# NextFactory ERP+MES Exhibition Demo

A comprehensive, modular ERP and MES integrated software solution designed for modern manufacturing environments. This exhibition demo showcases the complete capabilities of NextFactory with role-based access control, professional UI, and **all Phase 3 optional modules** ready for demonstration.

![NextFactory Demo](https://img.shields.io/badge/Status-Phase%203%20Complete-brightgreen)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![PyQt6](https://img.shields.io/badge/GUI-PyQt6-orange)
![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-blue)

## 🚀 Quick Start (Autonomous Setup)

**One-command setup for exhibition demos:**

```bash
git clone <repository-url>
cd NextFactory
python setup_postgres.py
```

This autonomous setup script will:
- ✅ Install all Python dependencies
- ✅ Configure PostgreSQL database automatically  
- ✅ Create all database tables and relationships
- ✅ Seed comprehensive demo data
- ✅ Test the complete installation
- ✅ Provide ready-to-run exhibition demo

**Then start the application:**
```bash
python main.py
```

**That's it! 🎉 Complete NextFactory system ready in under 5 minutes.**

## 📋 Manual Installation (Alternative)

If you prefer manual setup:

### Prerequisites
- **Python 3.8+** (recommended: 3.10+)
- **PostgreSQL 12+** (recommended: 14+)
- **4GB RAM minimum** (8GB recommended)
- **2GB free disk space**

### Installation Steps

1. **Clone Repository**:
   ```bash
   git clone <repository-url>
   cd NextFactory
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup Database**:
   ```bash
   python database.py
   ```

4. **Seed Demo Data**:
   ```bash
   python seed_db.py
   ```

5. **Launch Application**:
   ```bash
   python main.py
   ```

## 🎯 Exhibition Demo Workflow

### 10-Minute Demo Script (Phase 3 Complete)

#### **1. Login & Role Overview (1 minute)**
- Start with Guest login (`guest` / `guest123`)
- Show read-only dashboard access
- Switch to Manager role (`manager` / `manager123`)
- Highlight dynamic UI changes based on permissions

#### **2. Dashboard & System Overview (1 minute)**
- Navigate the professional dashboard
- Show real-time metrics and system status
- Demonstrate inventory summary with low-stock alerts
- Explain modular tab structure with **13 total modules**

#### **3. ERP Modules Demo (3 minutes)**
- **Enhanced Inventory Management**: Advanced filtering, alerts, export
- **Supply Chain Management**: Supplier management, auto-order analysis
- **Sales & CRM** ⭐: Customer management, order tracking, analytics
- **Asset Management** ⭐: Equipment tracking, condition monitoring, maintenance links
- **Reporting & Analytics**: Interactive charts, KPI dashboard, data export

#### **4. MES Modules Demo (4 minutes)**
- **Production Scheduling**: Calendar-based task management
- **Real-Time Data Collection**: Live sensor monitoring, anomaly detection
- **Quality Management**: Inspection forms, quality metrics
- **Performance Analysis**: OEE calculations, efficiency metrics
- **Resource Allocation** ⭐: Resource optimization, auto-allocation
- **Product Tracking & Traceability** ⭐: Genealogy tracking, audit trails
- **Maintenance Management** ⭐: Work orders, preventive maintenance
- **Labor Management** ⭐: Employee scheduling, performance tracking

#### **5. Role-Based Access Control (1 minute)**
- Switch to different roles showing access restrictions
- Demonstrate security model across all 13 modules
- Show UI adaptation based on permissions

#### **6. Integration & Phase 3 Features (0.5 minutes)**
- Highlight cross-module data integration
- Show Phase 3 autonomous setup capabilities
- Demonstrate comprehensive traceability and analytics

## 👥 User Roles & Credentials

| Role | Username | Password | Access Level |
|------|----------|----------|--------------|
| **Administrator** | `admin` | `admin123` | Full system access |
| **Manager** | `manager` | `manager123` | Management oversight |
| **Operator** | `operator` | `operator123` | Production operations |
| **Guest** | `guest` | `guest123` | Read-only demonstration |
| **Analyst** | `analyst` | `analyst123` | Reporting & analytics |

> 📋 For detailed role permissions, see [docs/access_roles.md](docs/access_roles.md)

## 🏗️ Architecture Overview

### Core Components

```
NextFactory/
├── main.py              # Main PyQt6 application with module integration
├── models.py            # Complete SQLAlchemy database models (ERP+MES)
├── database.py          # Database configuration & utilities
├── seed_db.py           # Comprehensive demo data seeding script
├── erp_modules.py       # ERP module implementations
├── mes_modules.py       # MES module implementations
├── requirements.txt     # Python dependencies
├── docs/                # Documentation
│   ├── access_roles.md  # Role-based access guide
│   └── database_setup.md# Database setup instructions
└── README.md           # This file
```

### Technology Stack

- **Frontend**: PyQt6 for professional desktop GUI
- **Backend**: Python with SQLAlchemy ORM
- **Database**: PostgreSQL for robust data management
- **Authentication**: bcrypt password hashing
- **Architecture**: Modular design for easy expansion

### Database Schema

```sql
-- Core Tables
users                 # User authentication & profiles
roles                 # Role-based permissions
inventory_items       # Enhanced inventory management

-- ERP Module Tables
suppliers             # Supplier management
purchase_orders       # Purchase order tracking
purchase_order_items  # Purchase order line items

-- MES Module Tables
production_tasks      # Production scheduling and task management
sensor_data          # Real-time data collection and monitoring
quality_checks       # Quality management and inspections
```

## 🎨 User Interface Features

### Professional Design
- **Modern Styling**: Clean, professional interface suitable for industrial environments
- **Responsive Layout**: Tabbed interface with dynamic content sizing
- **Role-Based UI**: Interface elements show/hide based on user permissions
- **Real-Time Updates**: Dashboard refreshes automatically with live data

### User Experience
- **Quick Login**: Demo user selector for easy role switching
- **Intuitive Navigation**: Clear tab structure and logical menu organization
- **Status Indicators**: Visual feedback for system status and data conditions
- **Help Integration**: Built-in help system and role-specific guidance

## 📊 Current Features (Phase 3 Complete)

### ✅ Core System
- **User Authentication**: Secure login with role-based access
- **Dashboard**: Real-time system overview and metrics
- **Role-Based Security**: Dynamic UI and permission enforcement
- **Database Foundation**: Complete schema with all ERP/MES models
- **Professional UI**: Exhibition-ready interface design
- **Autonomous Setup**: One-command installation and configuration

### ✅ ERP Modules (Enterprise Resource Planning)

#### **Enhanced Inventory Management**
- Advanced filtering and search capabilities
- Low-stock alerts with real-time monitoring
- Category-based inventory organization
- Export functionality (CSV format)
- Professional table display with sorting
- Role-based add/update permissions

#### **Supply Chain Management**
- Comprehensive supplier management with rating system
- Purchase order creation and tracking
- Auto-order analysis based on inventory thresholds
- Delivery simulation and status tracking
- Supplier performance analytics

#### **Sales & CRM** ⭐ *Phase 3 New*
- Customer relationship management with contact information
- Sales order creation and tracking with status workflow
- Order history and customer analytics
- Customer performance metrics and revenue tracking
- Credit limit management and relationship tracking

#### **Asset Management** ⭐ *Phase 3 New*
- Comprehensive asset registry (machines, tools, equipment)
- Asset condition tracking and status monitoring
- Purchase cost tracking and depreciation analysis
- Location-based asset management
- Maintenance history integration and alerts

#### **Reporting & Analytics**
- Interactive Matplotlib charts and visualizations
- Real-time KPI dashboard (inventory value, stock levels)
- Inventory distribution by category
- Low stock trending analysis
- Chart export capabilities (PNG format)

### ✅ MES Modules (Manufacturing Execution System)

#### **Production Scheduling & Dispatching**
- Interactive calendar-based task scheduling
- Task creation, assignment, and priority management
- Status tracking with color-coded visualization
- Task filtering by status, priority, and assignment
- Resource allocation and capacity planning

#### **Real-Time Data Collection**
- Multi-threaded sensor simulation (5 sensor types)
- Live sensor dashboard with real-time updates
- Anomaly detection and automated alerting
- Historical data feed with scrolling display
- Configurable monitoring start/stop controls

#### **Quality Management**
- Quality inspection forms with customizable check types
- Pass/Fail/Review result tracking system
- Defect categorization and logging
- Corrective action management
- Quality metrics and pass rate analytics

#### **Performance Analysis**
- OEE (Overall Equipment Effectiveness) calculations
- Availability, Performance, and Quality metrics
- Real-time performance indicators
- Throughput and efficiency analysis
- Color-coded performance status

#### **Resource Allocation** ⭐ *Phase 3 New*
- Resource management (equipment, personnel, materials)
- Auto-allocation algorithms for optimal resource usage
- Resource utilization monitoring and capacity planning
- Real-time availability tracking and status indicators
- Cost analysis and efficiency optimization

#### **Product Tracking & Traceability** ⭐ *Phase 3 New*
- Complete product genealogy and batch tracking
- Traceability records with operation history
- Search capabilities and tree view navigation
- Audit trail export and compliance reporting
- Quality integration with production batches

#### **Maintenance Management** ⭐ *Phase 3 New*
- Preventive and corrective maintenance scheduling
- Work order management with priority escalation
- Maintenance cost tracking and analysis
- Equipment downtime monitoring and alerts
- MTTR/MTBF analytics and reporting

#### **Labor Management** ⭐ *Phase 3 New*
- Employee management and skill tracking
- Shift templates and scheduling optimization
- Performance monitoring and productivity analysis
- Attendance tracking and labor cost analysis
- Department-based organization and reporting

### 🔄 Real-Time Features
- **Live Dashboard**: Updates every 30 seconds with current data
- **Sensor Monitoring**: Real-time data collection with anomaly detection
- **Inventory Alerts**: Automatic low-stock notifications
- **Session Management**: Automatic logout and security features
- **Performance Metrics**: Live OEE and efficiency calculations

## 🛣️ Development Roadmap

### ✅ Phase 1: Foundation (Completed)
- **User Authentication**: Secure login with role-based access
- **Dashboard**: Real-time system overview and metrics
- **Basic Inventory**: Stock tracking and management foundation
- **Database Schema**: Complete foundation for all modules
- **Professional UI**: Exhibition-ready interface design

### ✅ Phase 2: Core ERP & MES Modules (Completed)
- **Enhanced Inventory Management**: Advanced features, filtering, alerts
- **Supply Chain Management**: Supplier management, order processing, auto-order
- **Reporting & Analytics**: Interactive charts, KPI dashboards, data export
- **Production Scheduling**: Resource allocation, task management, calendar view
- **Real-Time Data Collection**: Sensor integration, live monitoring, anomaly detection
- **Quality Management**: Inspection workflows, defect tracking, compliance
- **Performance Analysis**: OEE calculations, efficiency metrics, trending

### 🔄 Phase 3: Advanced Features (Future)
- **Integration APIs**: Third-party system integration
- **Mobile Interface**: Responsive web interface
- **Advanced Analytics**: Machine learning insights
- **IoT Integration**: Real-time sensor data processing
- **Workflow Automation**: Automated business processes
- **Advanced Reporting**: Custom report builder

## 🔧 Configuration

### Environment Variables
Create `.env` file for custom configuration:

```bash
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=nextfactory
DB_USER=nextfactory
DB_PASSWORD=nextfactory123
DB_ECHO=false
```

### Database Setup
Detailed database setup instructions available in [docs/database_setup.md](docs/database_setup.md)

### Customization
- **Styling**: Modify CSS-like StyleSheets in `main.py`
- **Permissions**: Adjust role permissions in `seed_db.py`
- **Demo Data**: Customize inventory items in `seed_db.py`

## 🧪 Testing & Quality

### Manual Testing Checklist
- [ ] All user roles can login successfully
- [ ] Dashboard displays correctly for each role
- [ ] Inventory data loads and displays properly
- [ ] Role-based UI elements show/hide correctly
- [ ] Database operations complete without errors
- [ ] Application handles logout and role switching

### Error Handling
- **Database Connectivity**: Graceful handling of connection failures
- **Authentication**: Clear error messages for login failures
- **Data Loading**: Robust error handling for database operations
- **UI Responsiveness**: Non-blocking operations with progress feedback

## 📱 Exhibition Setup

### Hardware Requirements
- **Display**: Minimum 1920x1080 resolution
- **RAM**: 8GB recommended for smooth operation
- **Storage**: SSD recommended for database performance
- **Network**: Optional (application works offline)

### Pre-Demo Setup
1. **Database Reset**:
   ```bash
   python seed_db.py --force
   ```

2. **Application Test**:
   ```bash
   python main.py
   ```

3. **Quick Login Test**: Verify all demo user accounts work

4. **Backup Creation**: Save clean database state for reset

### Demo Best Practices
- **Start with Guest role** to show visitor experience
- **Progress through roles** to demonstrate access levels
- **Highlight real-time features** with dashboard updates
- **Emphasize modular design** for future expansion
- **Show inventory alerts** for practical demonstration

## 🔒 Security Features

### Authentication
- **Password Hashing**: bcrypt for secure password storage
- **Session Management**: Automatic timeout and logout
- **Role Validation**: Server-side permission checking
- **SQL Injection Protection**: SQLAlchemy ORM security

### Access Control
- **Role-Based Permissions**: Granular access control
- **UI Security**: Dynamic interface based on permissions
- **Data Protection**: Role-based data access restrictions
- **Audit Trails**: User action logging (foundation)

## 🐛 Troubleshooting

### Common Issues

#### Database Connection Failed
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Restart if needed
sudo systemctl restart postgresql

# Test connection
python -c "from database import test_database_connection; print(test_database_connection())"
```

#### Missing Dependencies
```bash
# Reinstall requirements
pip install -r requirements.txt --force-reinstall
```

#### Application Won't Start
```bash
# Check Python version
python --version

# Check PyQt6 installation
python -c "import PyQt6.QtWidgets; print('PyQt6 OK')"

# Run database setup
python database.py
```

### Getting Help
- **Check Logs**: Application logs errors to console
- **Database Diagnostics**: Run `python database.py` for connection testing
- **Reset Demo Data**: Use `python seed_db.py --force` to reset
- **Documentation**: Refer to `docs/` directory for detailed guides

## 📞 Support & Contact

### Exhibition Support
- **Technical Issues**: Check troubleshooting section above
- **Demo Questions**: Refer to role documentation in `docs/access_roles.md`
- **Database Issues**: See database setup guide in `docs/database_setup.md`

### Development Team
NextFactory Development Team - 2024

### Resources
- **PostgreSQL**: https://www.postgresql.org/docs/
- **PyQt6**: https://doc.qt.io/qtforpython/
- **SQLAlchemy**: https://docs.sqlalchemy.org/

---

## 📈 Success Metrics

This Phase 3 implementation successfully delivers:

✅ **Complete ERP Suite**: Enhanced inventory, supply chain, sales & CRM, asset management, and reporting modules  
✅ **Full MES Integration**: Production scheduling, real-time monitoring, quality management, resource allocation, product tracking, maintenance management, and labor management  
✅ **Professional UI**: Exhibition-ready interface with role-based access control across **13 integrated modules**  
✅ **Real-Time Features**: Live data collection, monitoring, and automated alerts  
✅ **Modular Architecture**: Extensible design supporting 13+ integrated modules with seamless data flow  
✅ **Database Integration**: Complete schema with comprehensive data models for all Phase 3 features  
✅ **Security Model**: Comprehensive role-based access control and UI adaptation  
✅ **Export Capabilities**: Data export functionality for reports and analytics  
✅ **Demo Data**: Complete sample dataset for immediate exhibition use including all Phase 3 modules  
✅ **Autonomous Setup**: One-command installation and configuration for exhibitions  
✅ **Documentation**: Comprehensive guides for setup, operation, and expansion  

### 🌟 Phase 3 Optional Modules Delivered:
1. **ERP: Sales & CRM** – Customer orders, relationships, order history
2. **ERP: Asset Management** – Track machines, tools, asset status  
3. **MES: Resource Allocation** – Assign/monitor resources, auto-allocation
4. **MES: Product Tracking & Traceability** – Log genealogy, audit/export
5. **MES: Maintenance Management** – Schedule/track maintenance, alerts
6. **MES: Labor Management** – Worker schedules, shift templates, performance

**Phase 3 Complete - Comprehensive ERP+MES solution with all optional modules ready for exhibition demonstration.**

### 🚀 Exhibition Ready Features:
- **13 Integrated Modules** across ERP and MES domains
- **Autonomous Setup Script** for rapid deployment
- **Comprehensive Demo Data** covering all business scenarios
- **Professional UI** with role-based access control
- **Real-Time Monitoring** and analytics across all modules
- **Complete Traceability** from raw materials to finished products
- **Advanced Resource Management** with optimization algorithms
- **Maintenance Scheduling** with predictive analytics
- **Labor Management** with performance tracking

---

*NextFactory ERP+MES Exhibition Demo - Showcasing the complete future of integrated manufacturing software.*
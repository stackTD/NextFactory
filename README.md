# NextFactory ERP+MES Exhibition Demo

A comprehensive, modular ERP and MES integrated software solution designed for modern manufacturing environments. This exhibition demo showcases the core capabilities of NextFactory with role-based access control, professional UI, and foundational modules ready for expansion.

![NextFactory Demo](https://img.shields.io/badge/Status-Phase%201%20Complete-green)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![PyQt6](https://img.shields.io/badge/GUI-PyQt6-orange)
![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-blue)

## 🚀 Quick Start

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

### 5-Minute Demo Script

#### **1. Login & Role Overview (1 minute)**
- Start with Guest login (`guest` / `guest123`)
- Show read-only dashboard access
- Switch to Manager role (`manager` / `manager123`)
- Highlight dynamic UI changes based on permissions

#### **2. Dashboard & System Overview (1 minute)**
- Navigate the professional dashboard
- Show real-time metrics and system status
- Demonstrate inventory summary with low-stock alerts
- Explain modular tab structure

#### **3. Inventory Management (1.5 minutes)**
- Access Inventory tab (Manager permissions)
- Browse sample inventory items
- Show categorization and status indicators
- Point out low-stock items (red highlighting)
- Demonstrate sorting and filtering capabilities

#### **4. Role-Based Access Control (1 minute)**
- Switch to Operator role (`operator` / `operator123`)
- Show limited access to MES modules only
- Switch to Admin role (`admin` / `admin123`)
- Demonstrate full system access
- Explain security model and permission structure

#### **5. Future Modules Preview (0.5 minutes)**
- Click through ERP and MES placeholder tabs
- Explain Phase 2 implementation roadmap
- Highlight modular architecture benefits

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
├── main.py              # Main PyQt6 application
├── models.py            # SQLAlchemy database models
├── database.py          # Database configuration & utilities
├── seed_db.py           # Demo data seeding script
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
inventory_items       # Basic inventory management

-- Future Expansions (Phase 2+)
orders               # ERP order management
production_tasks     # MES production scheduling
quality_logs         # Quality management
assets              # Asset management
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

## 📊 Current Features (Phase 1)

### ✅ Implemented
- **User Authentication**: Secure login with role-based access
- **Dashboard**: Real-time system overview and metrics
- **Inventory Management**: Basic stock tracking and management
- **Role-Based Security**: Dynamic UI and permission enforcement
- **Database Foundation**: Complete schema for expansion
- **Professional UI**: Exhibition-ready interface design

### 🔄 Real-Time Features
- **Live Dashboard**: Updates every 30 seconds
- **Inventory Monitoring**: Low-stock alerts and status tracking
- **Session Management**: Automatic logout and security features
- **Performance Metrics**: System status and health indicators

## 🛣️ Development Roadmap

### Phase 2: Core ERP Modules (Planned)
- **Inventory Management**: Advanced features, procurement, tracking
- **Supply Chain Management**: Supplier management, order processing
- **Reporting & Analytics**: Advanced charts, KPI dashboards, data export

### Phase 3: Core MES Modules (Planned)
- **Production Scheduling**: Resource allocation, task management
- **Real-Time Data Collection**: Sensor integration, live monitoring
- **Quality Management**: Inspection workflows, compliance tracking
- **Performance Analysis**: OEE calculations, efficiency metrics

### Phase 4: Advanced Features (Future)
- **Integration APIs**: Third-party system integration
- **Mobile Interface**: Responsive web interface
- **Advanced Analytics**: Machine learning insights
- **IoT Integration**: Real-time sensor data processing

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

This Phase 1 implementation successfully delivers:

✅ **Professional UI**: Exhibition-ready interface with role-based access  
✅ **Solid Foundation**: Modular architecture supporting 13+ planned modules  
✅ **Security Model**: Comprehensive role-based access control  
✅ **Real-Time Features**: Live dashboard updates and data monitoring  
✅ **Database Foundation**: Complete schema ready for expansion  
✅ **Documentation**: Comprehensive guides for setup and operation  

**Ready for Phase 2 implementation of core ERP and MES modules.**

---

*NextFactory ERP+MES Exhibition Demo - Showcasing the future of integrated manufacturing software.*
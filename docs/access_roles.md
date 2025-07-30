# NextFactory Access Roles and Credentials

This document provides detailed information about user roles, access levels, and demonstration credentials for the NextFactory ERP+MES Exhibition Demo.

## Overview

NextFactory implements a comprehensive role-based access control (RBAC) system that ensures users have appropriate permissions for their responsibilities. The system supports five distinct roles, each designed for specific operational requirements.

## User Roles and Permissions

### 1. Administrator (admin)

**Purpose**: Complete system control and configuration
**Target Users**: IT administrators, system integrators, super users

#### Permissions:
- ✅ Edit Users and Roles
- ✅ View All Reports
- ✅ Manage Inventory
- ✅ Access MES Modules
- ✅ Access ERP Modules
- ✅ Create Orders
- ✅ Modify Schedules

#### Capabilities:
- Full access to all system modules
- User account management and role assignment
- System configuration and settings
- Database administration tools
- Security and audit management
- Module configuration and customization

#### Demonstration Credentials:
- **Username**: `admin`
- **Password**: `admin123`

---

### 2. Manager (manager)

**Purpose**: Management oversight and strategic operations
**Target Users**: Plant managers, production managers, department heads

#### Permissions:
- ❌ Edit Users and Roles
- ✅ View All Reports
- ✅ Manage Inventory
- ✅ Access MES Modules
- ✅ Access ERP Modules
- ✅ Create Orders
- ✅ Modify Schedules

#### Capabilities:
- Comprehensive reporting and analytics access
- Inventory management and procurement oversight
- Production scheduling and resource allocation
- Order creation and management
- Performance monitoring and KPI tracking
- Strategic planning tools

#### Demonstration Credentials:
- **Username**: `manager`
- **Password**: `manager123`

---

### 3. Operator (operator)

**Purpose**: Production floor operations and data entry
**Target Users**: Machine operators, production workers, floor supervisors

#### Permissions:
- ❌ Edit Users and Roles
- ✅ View Reports (Limited)
- ❌ Manage Inventory
- ✅ Access MES Modules
- ❌ Access ERP Modules
- ❌ Create Orders
- ❌ Modify Schedules

#### Capabilities:
- MES data entry and status updates
- Real-time production monitoring
- Quality control data logging
- Work order tracking and completion
- Equipment status reporting
- Basic performance metrics viewing

#### Demonstration Credentials:
- **Username**: `operator`
- **Password**: `operator123`

---

### 4. Guest (guest)

**Purpose**: Read-only demonstration and visitor access
**Target Users**: Visitors, potential customers, demonstration purposes

#### Permissions:
- ❌ Edit Users and Roles
- ✅ View Reports (Read-only)
- ❌ Manage Inventory
- ❌ Access MES Modules
- ❌ Access ERP Modules
- ❌ Create Orders
- ❌ Modify Schedules

#### Capabilities:
- View-only access to dashboards
- Limited reporting access
- System overview and navigation
- Demonstration-specific content
- Educational materials and tutorials

#### Demonstration Credentials:
- **Username**: `guest`
- **Password**: `guest123`

---

### 5. Analyst (analyst)

**Purpose**: Data analysis and reporting focus
**Target Users**: Business analysts, quality analysts, data scientists

#### Permissions:
- ❌ Edit Users and Roles
- ✅ View All Reports
- ❌ Manage Inventory
- ✅ Access MES Modules
- ✅ Access ERP Modules
- ❌ Create Orders
- ❌ Modify Schedules

#### Capabilities:
- Advanced reporting and analytics tools
- Data export and analysis capabilities
- KPI monitoring and trend analysis
- Cross-module data integration
- Custom report generation
- Statistical analysis tools

#### Demonstration Credentials:
- **Username**: `analyst`
- **Password**: `analyst123`

---

## Role Advantages and Use Cases

### Administrative Efficiency
- **Admin Role**: Complete control for system setup and maintenance
- **Manager Role**: Strategic oversight without technical system management
- **Clear Separation**: Prevents operational users from accessing system configuration

### Operational Security
- **Operator Role**: Limited access prevents accidental system changes
- **Guest Role**: Safe demonstration environment without data modification risk
- **Controlled Access**: Each role has minimum necessary permissions

### Business Intelligence
- **Analyst Role**: Specialized access for data-driven decision making
- **Manager Role**: Executive-level reporting and strategic metrics
- **Graduated Access**: Different reporting levels for different business needs

### Scalability
- **Modular Permissions**: Easy to add new roles or modify existing ones
- **Role-Based UI**: Interface adapts automatically to user permissions
- **Future-Proof**: Design supports expansion to additional modules

## Exhibition Demonstration Scenarios

### Scenario 1: Executive Overview (Manager Role)
1. Login as `manager`
2. Review dashboard metrics and KPIs
3. Access inventory management features
4. View production schedules and create orders
5. Generate management reports

### Scenario 2: Production Floor Operations (Operator Role)
1. Login as `operator`
2. Access MES modules for production tracking
3. Update work order status
4. Log quality control data
5. View real-time production metrics

### Scenario 3: System Administration (Admin Role)
1. Login as `admin`
2. Demonstrate user management capabilities
3. Show system configuration options
4. Access all modules and features
5. Explain security and audit features

### Scenario 4: Business Analysis (Analyst Role)
1. Login as `analyst`
2. Access advanced reporting tools
3. Demonstrate cross-module data analysis
4. Show custom report generation
5. Explain data export capabilities

### Scenario 5: Visitor Experience (Guest Role)
1. Login as `guest`
2. Navigate through system overview
3. View read-only dashboards
4. Understand system capabilities
5. Safe exploration without data modification

## Security Considerations

### Password Security
- **Demo Passwords**: Simple passwords for exhibition ease
- **Production Recommendation**: Use strong, unique passwords in production
- **Password Policy**: Implement corporate password policies for real deployment

### Access Control
- **Principle of Least Privilege**: Users have minimum necessary access
- **Regular Reviews**: Periodically review and update role permissions
- **Audit Trails**: System logs all user actions and access attempts

### Data Protection
- **Role-Based Data Access**: Sensitive data visible only to authorized roles
- **Session Management**: Automatic logout after inactivity
- **Secure Authentication**: Password hashing with bcrypt

## Technical Implementation

### Database Structure
- **Roles Table**: Stores role definitions and permissions
- **Users Table**: Links users to roles with additional metadata
- **Permission Flags**: Boolean flags for granular access control

### UI Integration
- **Dynamic Interface**: UI elements shown/hidden based on permissions
- **Real-Time Validation**: Permissions checked on every action
- **Graceful Degradation**: System works even with limited permissions

### Future Enhancements
- **Multi-Factor Authentication**: Enhanced security for production use
- **LDAP Integration**: Corporate directory integration
- **Advanced Permissions**: More granular, resource-specific permissions
- **Role Hierarchies**: Parent-child role relationships

---

## Quick Reference

| Role | Username | Password | Primary Use Case |
|------|----------|----------|------------------|
| Admin | admin | admin123 | System administration |
| Manager | manager | manager123 | Management oversight |
| Operator | operator | operator123 | Production operations |
| Guest | guest | guest123 | Demonstrations/tours |
| Analyst | analyst | analyst123 | Data analysis |

**Note**: These credentials are for demonstration purposes only. In production environments, implement proper password policies and security measures.
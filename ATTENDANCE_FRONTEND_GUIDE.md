# Frontend Implementation Guide - Attendance Integration

## Overview
This document provides detailed instructions for completing Phase 3 (Frontend UI) of the Attendance Integration.

**Backend Status**: ✅ Complete (Database, Models, Service, API Routes)  
**Frontend Status**: ⏳ Pending Implementation

---

## Phase 3: Frontend Components

### 1. Add "Sync to Attendance" Button in EmployesList

**File**: `frontend/src/pages/Employes/EmployesList.jsx`

**Location**: Add button in the actions column of the table.

**Implementation**:
```jsx
import { SyncOutlined } from '@ant-design/icons';
import axios from 'axios';

// Add sync function
const handleSyncToAttendance = async (employeeId) => {
  try {
    const response = await axios.post('/api/attendance-integration/sync-employee', {
      employee_id: employeeId
    });
    
    if (response.data.success) {
      message.success(response.data.message);
    } else {
      message.warning(response.data.message);
    }
  } catch (error) {
    message.error('Erreur lors de la synchronisation');
    console.error(error);
  }
};

// Add to actions column
{
  title: 'Actions',
  key: 'actions',
  render: (_, record) => (
    <Space>
      <Tooltip title="Modifier">
        <Button icon={<EditOutlined />} onClick={() => navigate(`/employes/${record.id}`)} />
      </Tooltip>
      <Tooltip title="Sync vers Attendance">
        <Button 
          icon={<SyncOutlined />} 
          onClick={() => handleSyncToAttendance(record.id)}
        />
      </Tooltip>
      <Tooltip title="Supprimer">
        <Button icon={<DeleteOutlined />} danger onClick={() => handleDeleteClick(record)} />
      </Tooltip>
    </Space>
  )
}
```

---

### 2. Create Import Attendance Page

**File**: `frontend/src/pages/Pointages/ImportAttendance.jsx` (NEW)

**Purpose**: Allow admin to import attendance logs for a date range.

**Implementation**:
```jsx
import { useState } from 'react';
import { Card, DatePicker, Button, Select, message, Table, Tag, Statistic, Row, Col } from 'antd';
import { DownloadOutlined, SyncOutlined } from '@ant-design/icons';
import axios from 'axios';
import dayjs from 'dayjs';

const { RangePicker } = DatePicker;
const { Option } = Select;

function ImportAttendance() {
  const [loading, setLoading] = useState(false);
  const [dateRange, setDateRange] = useState([dayjs().startOf('month'), dayjs().endOf('month')]);
  const [employeeId, setEmployeeId] = useState(null);
  const [summary, setSummary] = useState(null);

  const handleImport = async () => {
    if (!dateRange || dateRange.length !== 2) {
      message.error('Veuillez sélectionner une plage de dates');
      return;
    }

    try {
      setLoading(true);
      const response = await axios.post('/api/attendance-integration/import-logs', {
        start_date: dateRange[0].format('YYYY-MM-DD'),
        end_date: dateRange[1].format('YYYY-MM-DD'),
        employee_id: employeeId
      });

      setSummary(response.data);
      
      if (response.data.imported > 0) {
        message.success(`${response.data.imported} logs importés avec succès`);
      }
      
      if (response.data.conflicts > 0) {
        message.warning(`${response.data.conflicts} conflits détectés. Consultez la page Conflits.`);
      }
    } catch (error) {
      message.error('Erreur lors de l\'importation');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <Card title="Importer Pointages depuis Attendance">
        <Row gutter={16} style={{ marginBottom: 24 }}>
          <Col span={12}>
            <label>Plage de dates</label>
            <RangePicker 
              value={dateRange}
              onChange={setDateRange}
              style={{ width: '100%' }}
            />
          </Col>
          <Col span={12}>
            <label>Employé (optionnel)</label>
            <Select 
              placeholder="Tous les employés"
              allowClear
              onChange={setEmployeeId}
              style={{ width: '100%' }}
            >
              {/* Load employees from API */}
            </Select>
          </Col>
        </Row>

        <Button 
          type="primary" 
          icon={<DownloadOutlined />}
          onClick={handleImport}
          loading={loading}
        >
          Importer
        </Button>

        {summary && (
          <Row gutter={16} style={{ marginTop: 24 }}>
            <Col span={4}>
              <Statistic title="Total Logs" value={summary.total_logs} />
            </Col>
            <Col span={4}>
              <Statistic title="Importés" value={summary.imported} valueStyle={{ color: '#3f8600' }} />
            </Col>
            <Col span={4}>
              <Statistic title="Doublons" value={summary.skipped_duplicate} />
            </Col>
            <Col span={4}>
              <Statistic title="Sans Mapping" value={summary.skipped_no_mapping} valueStyle={{ color: '#cf1322' }} />
            </Col>
            <Col span={4}>
              <Statistic title="Conflits" value={summary.conflicts} valueStyle={{ color: '#faad14' }} />
            </Col>
            <Col span={4}>
              <Statistic title="Erreurs" value={summary.errors} valueStyle={{ color: '#cf1322' }} />
            </Col>
          </Row>
        )}
      </Card>
    </div>
  );
}

export default ImportAttendance;
```

---

### 3. Create Conflicts Resolution Page

**File**: `frontend/src/pages/Pointages/AttendanceConflicts.jsx` (NEW)

**Purpose**: Display and resolve import conflicts.

**Implementation**:
```jsx
import { useState, useEffect } from 'react';
import { Table, Button, Tag, message, Modal, Space } from 'antd';
import { CheckOutlined, CloseOutlined } from '@ant-design/icons';
import axios from 'axios';
import dayjs from 'dayjs';

function AttendanceConflicts() {
  const [loading, setLoading] = useState(false);
  const [conflicts, setConflicts] = useState([]);

  useEffect(() => {
    loadConflicts();
  }, []);

  const loadConflicts = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/attendance-integration/conflicts?status=pending');
      setConflicts(response.data);
    } catch (error) {
      message.error('Erreur lors du chargement des conflits');
    } finally {
      setLoading(false);
    }
  };

  const handleResolve = async (conflictId, resolution) => {
    try {
      await axios.post(`/api/attendance-integration/conflicts/${conflictId}/resolve`, {
        resolution: resolution,
        resolved_by: 'Admin' // Replace with actual user
      });
      
      message.success('Conflit résolu');
      loadConflicts();
    } catch (error) {
      message.error('Erreur lors de la résolution');
    }
  };

  const columns = [
    {
      title: 'Date',
      dataIndex: 'conflict_date',
      render: (date) => dayjs(date).format('DD/MM/YYYY')
    },
    {
      title: 'Employé',
      dataIndex: 'hr_employee_id',
      render: (id) => `Employé #${id}` // Fetch employee name from API
    },
    {
      title: 'Valeur HR',
      dataIndex: 'hr_existing_value',
      render: (val) => val === 1 ? <Tag color="green">Travaillé</Tag> : <Tag>Absent</Tag>
    },
    {
      title: 'Minutes Attendance',
      dataIndex: 'attendance_worked_minutes',
      render: (min) => `${min} min (${(min / 60).toFixed(1)}h)`
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Button 
            type="primary"
            icon={<CheckOutlined />}
            onClick={() => handleResolve(record.id, 'use_attendance')}
          >
            Utiliser Attendance
          </Button>
          <Button 
            icon={<CloseOutlined />}
            onClick={() => handleResolve(record.id, 'keep_hr')}
          >
            Garder HR
          </Button>
        </Space>
      )
    }
  ];

  return (
    <div>
      <Table 
        columns={columns}
        dataSource={conflicts}
        loading={loading}
        rowKey="id"
      />
    </div>
  );
}

export default AttendanceConflicts;
```

---

### 4. Add Routes

**File**: `frontend/src/App.jsx`

Add routes for new pages:
```jsx
import ImportAttendance from './pages/Pointages/ImportAttendance';
import AttendanceConflicts from './pages/Pointages/AttendanceConflicts';

// Inside Routes
<Route path="/pointages/import-attendance" element={<ImportAttendance />} />
<Route path="/pointages/conflicts" element={<AttendanceConflicts />} />
```

---

### 5. Update Sidebar

**File**: `frontend/src/components/Sidebar.jsx`

Add links to new pages (optional, or add as sub-menu under Pointages):
```jsx
{ to: '/pointages/import-attendance', label: 'Importer Pointages', icon: DownloadOutlined },
{ to: '/pointages/conflicts', label: 'Conflits Import', icon: ExclamationCircleOutlined },
```

---

## Testing Checklist

### Backend API Testing
- [ ] Test `/api/attendance-integration/sync-employee` with Postman
- [ ] Test `/api/attendance-integration/import-logs` with sample data
- [ ] Verify conflicts are created when day already set
- [ ] Test conflict resolution endpoints

### Frontend Testing
- [ ] Sync button appears in EmployesList
- [ ] Clicking sync shows success/error message
- [ ] Import page loads and accepts date range
- [ ] Import displays summary statistics
- [ ] Conflicts page shows pending conflicts
- [ ] Resolving conflict updates database

### Integration Testing
- [ ] Create employee in HR
- [ ] Sync to Attendance (verify in Attendance UI)
- [ ] Add attendance log in Attendance system
- [ ] Import logs to HR
- [ ] Verify pointage grid updated
- [ ] Verify overtime calculated correctly

---

## Deployment Steps

1. **Run Database Migration**:
   ```bash
   mysql -u root -p ay_hr < database/migrations/001_attendance_integration.sql
   ```

2. **Restart Backend**:
   ```bash
   systemctl restart ayhr-backend
   ```

3. **Rebuild Frontend**:
   ```bash
   cd frontend
   npm run build
   systemctl restart ayhr-frontend
   ```

4. **Verify API**:
   - Visit `http://192.168.20.53:8000/docs`
   - Check new endpoints under "Attendance Integration"

---

## Configuration

Add to `backend/.env`:
```env
ATTENDANCE_API_URL=http://192.168.20.56:8000/api
ATTENDANCE_API_TIMEOUT=30
```

---

## Notes

- **Photos**: Not managed in HR System. Admin must upload photos manually in Attendance UI after sync.
- **Mapping**: First sync creates mapping. Subsequent syncs update employee info only.
- **Conflicts**: Always flagged for manual review. Never auto-overwrite HR data.
- **Overtime**: Calculated as `(worked_minutes - 480) / 60` hours.

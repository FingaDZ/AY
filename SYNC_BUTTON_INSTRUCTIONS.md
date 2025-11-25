# Sync Button - Manual Instructions

Due to file editing conflicts, please add the sync button manually to `EmployesList.jsx`:

## Step 1: Add Imports (Lines 3-5)

**Line 3** - Add `CloudSyncOutlined` to imports:
```javascript
import { PlusOutlined, EditOutlined, DeleteOutlined, SearchOutlined, FilePdfOutlined, ExclamationCircleOutlined, CheckCircleOutlined, FileTextOutlined, SafetyCertificateOutlined, FileProtectOutlined, UserOutlined, CloudSyncOutlined } from '@ant-design/icons';
```

**Line 5** - Add `attendanceService`:
```javascript
import { employeService, attendanceService } from '../../services';
```

## Step 2: Add State (After line 17)

Add this line after `const [employes, setEmployes] = useState([]);`:
```javascript
const [syncingAll, setSyncingAll] = useState(false);
```

## Step 3: Add Sync Button (Line 521, BEFORE the PDF button)

Insert this button BEFORE the `<Button icon={<FilePdfOutlined />}` button:

```javascript
<Button
  icon={<CloudSyncOutlined />}
  onClick={async () => {
    try {
      setSyncingAll(true);
      const response = await attendanceService.syncAllEmployees();
      message.success(`${response.data.synced} employés synchronisés`);
      if (response.data.not_found > 0) {
        message.info(`${response.data.not_found} non trouvés dans Attendance`);
      }
    } catch (error) {
      message.error('Erreur lors de la synchronisation');
    } finally {
      setSyncingAll(false);
    }
  }}
  loading={syncingAll}
  block={isMobile}
>
  Sync Attendance
</Button>
```

That's it! The button will appear between the header and the PDF button.

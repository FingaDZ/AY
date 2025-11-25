import { useState, useEffect } from 'react';
import { Table, Button, Tag, message, Space, Card } from 'antd';
import { CheckOutlined, CloseOutlined, ReloadOutlined } from '@ant-design/icons';
import { attendanceService } from '../../services';
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
            const response = await attendanceService.getConflicts('pending');
            setConflicts(response.data);
        } catch (error) {
            message.error('Erreur lors du chargement des conflits');
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    const handleResolve = async (conflictId, resolution) => {
        try {
            await attendanceService.resolveConflict(
                conflictId,
                resolution,
                'Admin' // TODO: Replace with actual logged-in user
            );

            message.success('Conflit résolu avec succès');
            loadConflicts();
        } catch (error) {
            message.error('Erreur lors de la résolution du conflit');
            console.error(error);
        }
    };

    const columns = [
        {
            title: 'Date',
            dataIndex: 'conflict_date',
            key: 'conflict_date',
            render: (date) => dayjs(date).format('DD/MM/YYYY'),
            sorter: (a, b) => dayjs(a.conflict_date).unix() - dayjs(b.conflict_date).unix(),
        },
        {
            title: 'Employé ID',
            dataIndex: 'hr_employee_id',
            key: 'hr_employee_id',
        },
        {
            title: 'Valeur HR',
            dataIndex: 'hr_existing_value',
            key: 'hr_existing_value',
            render: (val) => (
                val === 1 ?
                    <Tag color="green">Travaillé</Tag> :
                    <Tag color="default">Absent</Tag>
            ),
        },
        {
            title: 'Minutes Attendance',
            dataIndex: 'attendance_worked_minutes',
            key: 'attendance_worked_minutes',
            render: (min) => {
                const hours = (min / 60).toFixed(1);
                return `${min} min (${hours}h)`;
            },
        },
        {
            title: 'Statut',
            dataIndex: 'status',
            key: 'status',
            render: (status) => {
                const colors = {
                    pending: 'orange',
                    resolved_keep_hr: 'blue',
                    resolved_use_attendance: 'green'
                };
                const labels = {
                    pending: 'En attente',
                    resolved_keep_hr: 'HR conservé',
                    resolved_use_attendance: 'Attendance utilisé'
                };
                return <Tag color={colors[status]}>{labels[status]}</Tag>;
            },
        },
        {
            title: 'Actions',
            key: 'actions',
            render: (_, record) => (
                record.status === 'pending' ? (
                    <Space>
                        <Button
                            type="primary"
                            size="small"
                            icon={<CheckOutlined />}
                            onClick={() => handleResolve(record.id, 'use_attendance')}
                        >
                            Utiliser Attendance
                        </Button>
                        <Button
                            size="small"
                            icon={<CloseOutlined />}
                            onClick={() => handleResolve(record.id, 'keep_hr')}
                        >
                            Garder HR
                        </Button>
                    </Space>
                ) : (
                    <Tag color="green">Résolu</Tag>
                )
            ),
        },
    ];

    return (
        <div style={{ padding: '24px' }}>
            <Card
                title="Conflits d'Importation Attendance"
                extra={
                    <Button
                        icon={<ReloadOutlined />}
                        onClick={loadConflicts}
                        loading={loading}
                    >
                        Actualiser
                    </Button>
                }
            >
                <Table
                    columns={columns}
                    dataSource={conflicts}
                    loading={loading}
                    rowKey="id"
                    pagination={{ pageSize: 10 }}
                />
            </Card>
        </div>
    );
}

export default AttendanceConflicts;

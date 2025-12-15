import React, { useState, useEffect } from 'react';
import { Table, Card, Select, DatePicker, Button, Space, Tag, Modal, Descriptions, Alert, Input } from 'antd';
import { ReloadOutlined, EyeOutlined, FilterOutlined, ClearOutlined } from '@ant-design/icons';
import logsService from '../../services/logs';
import dayjs from 'dayjs';

const { RangePicker } = DatePicker;
const { Option } = Select;

const LogsPage = () => {
    const [logs, setLogs] = useState([]);
    const [loading, setLoading] = useState(false);
    const [pagination, setPagination] = useState({ current: 1, pageSize: 100, total: 0 });
    const [modules, setModules] = useState([]);
    const [users, setUsers] = useState([]);
    const [detailModalVisible, setDetailModalVisible] = useState(false);
    const [selectedLog, setSelectedLog] = useState(null);
    
    // Filtres
    const [filters, setFilters] = useState({
        module_name: null,
        action_type: null,
        user_id: null,
        date_debut: null,
        date_fin: null,
        search: null,
    });

    useEffect(() => {
        fetchModules();
        fetchUsers();
        fetchLogs();
    }, []);

    const fetchLogs = async (page = 1) => {
        setLoading(true);
        try {
            const params = {
                page,
                limit: pagination.pageSize,
                ...filters,
            };
            
            const response = await logsService.getLogs(params);
            setLogs(response.data.logs);
            setPagination({
                ...pagination,
                current: page,
                total: response.data.total,
            });
        } catch (error) {
            console.error('Erreur lors de la récupération des logs:', error);
        } finally {
            setLoading(false);
        }
    };

    const fetchModules = async () => {
        try {
            const response = await logsService.getModules();
            setModules(response.data);
        } catch (error) {
            console.error('Erreur lors de la récupération des modules:', error);
        }
    };

    const fetchUsers = async () => {
        try {
            const response = await logsService.getUsers();
            setUsers(response.data);
        } catch (error) {
            console.error('Erreur lors de la récupération des utilisateurs:', error);
        }
    };

    const handleTableChange = (newPagination) => {
        fetchLogs(newPagination.current);
    };

    const handleFilterChange = (key, value) => {
        setFilters({
            ...filters,
            [key]: value,
        });
    };

    const handleDateRangeChange = (dates) => {
        if (dates) {
            setFilters({
                ...filters,
                date_debut: dates[0].toISOString(),
                date_fin: dates[1].toISOString(),
            });
        } else {
            setFilters({
                ...filters,
                date_debut: null,
                date_fin: null,
            });
        }
    };

    const applyFilters = () => {
        fetchLogs(1);
    };

    const clearFilters = () => {
        setFilters({
            module_name: null,
            action_type: null,
            user_id: null,
            date_debut: null,
            date_fin: null,
            search: null,
        });
        setTimeout(() => fetchLogs(1), 100);
    };

    const showLogDetail = async (log) => {
        try {
            const response = await logsService.getLogDetail(log.id);
            setSelectedLog(response.data);
            setDetailModalVisible(true);
        } catch (error) {
            console.error('Erreur lors de la récupération du détail:', error);
        }
    };

    const getActionColor = (action) => {
        switch (action) {
            case 'CREATE': return 'green';
            case 'UPDATE': return 'blue';
            case 'DELETE': return 'red';
            case 'LOGIN': return 'cyan';  // ⭐ v3.6.0 Phase 4
            default: return 'default';
        }
    };

    const getActionLabel = (action) => {
        switch (action) {
            case 'CREATE': return 'Création';
            case 'UPDATE': return 'Modification';
            case 'DELETE': return 'Suppression';
            case 'LOGIN': return '🔐 Connexion';  // ⭐ v3.6.0 Phase 4
            default: return action;
        }
    };

    const columns = [
        {
            title: 'Date/Heure',
            dataIndex: 'timestamp',
            key: 'timestamp',
            width: 180,
            render: (text) => dayjs(text).format('DD/MM/YYYY HH:mm:ss'),
        },
        {
            title: 'Module',
            dataIndex: 'module_name',
            key: 'module_name',
            width: 120,
            render: (text) => <Tag color="purple">{text}</Tag>,
        },
        {
            title: 'Action',
            dataIndex: 'action_type',
            key: 'action_type',
            width: 120,
            render: (text) => <Tag color={getActionColor(text)}>{getActionLabel(text)}</Tag>,
        },
        {
            title: 'Utilisateur',
            dataIndex: 'user_email',
            key: 'user_email',
            width: 200,
        },
        {
            title: 'ID Enregistrement',
            dataIndex: 'record_id',
            key: 'record_id',
            width: 120,
        },
        {
            title: 'Description',
            dataIndex: 'description',
            key: 'description',
            ellipsis: true,
        },
        {
            title: 'Actions',
            key: 'actions',
            width: 100,
            render: (_, record) => (
                <Button
                    type="link"
                    icon={<EyeOutlined />}
                    onClick={() => showLogDetail(record)}
                >
                    Détail
                </Button>
            ),
        },
    ];

    return (
        <div style={{ padding: '24px' }}>
            <Card
                title="Journaux d'Activité"
                extra={
                    <Button
                        icon={<ReloadOutlined />}
                        onClick={() => fetchLogs(pagination.current)}
                    >
                        Actualiser
                    </Button>
                }
            >
                <Alert
                    message="Information"
                    description="Les logs sont en lecture seule et ne peuvent être modifiés ou supprimés que par intervention directe dans la base de données."
                    type="info"
                    showIcon
                    style={{ marginBottom: 16 }}
                />

                <Space direction="vertical" style={{ width: '100%', marginBottom: 16 }}>
                    <Space wrap>
                        <Select
                            style={{ width: 200 }}
                            placeholder="Module"
                            allowClear
                            value={filters.module_name}
                            onChange={(value) => handleFilterChange('module_name', value)}
                        >
                            {modules.map(module => (
                                <Option key={module} value={module}>{module}</Option>
                            ))}
                        </Select>

                        <Select
                            style={{ width: 150 }}
                            placeholder="Action"
                            allowClear
                            value={filters.action_type}
                            onChange={(value) => handleFilterChange('action_type', value)}
                        >
                            <Option value="CREATE">Création</Option>
                            <Option value="UPDATE">Modification</Option>
                            <Option value="DELETE">Suppression</Option>
                            <Option value="LOGIN">🔐 Connexion</Option>
                        </Select>

                        <Select
                            style={{ width: 200 }}
                            placeholder="Utilisateur"
                            allowClear
                            value={filters.user_id}
                            onChange={(value) => handleFilterChange('user_id', value)}
                        >
                            {users.map(user => (
                                <Option key={user.id} value={user.id}>{user.email}</Option>
                            ))}
                        </Select>

                        <RangePicker
                            style={{ width: 300 }}
                            placeholder={['Date début', 'Date fin']}
                            onChange={handleDateRangeChange}
                            format="DD/MM/YYYY"
                        />

                        <Input
                            style={{ width: 200 }}
                            placeholder="Rechercher..."
                            allowClear
                            value={filters.search}
                            onChange={(e) => handleFilterChange('search', e.target.value)}
                        />
                    </Space>

                    <Space>
                        <Button
                            type="primary"
                            icon={<FilterOutlined />}
                            onClick={applyFilters}
                        >
                            Appliquer les filtres
                        </Button>
                        <Button
                            icon={<ClearOutlined />}
                            onClick={clearFilters}
                        >
                            Effacer les filtres
                        </Button>
                    </Space>
                </Space>

                <Table
                    columns={columns}
                    dataSource={logs}
                    rowKey="id"
                    loading={loading}
                    pagination={pagination}
                    onChange={handleTableChange}
                    scroll={{ x: 1200 }}
                />
            </Card>

            <Modal
                title="Détail du Log"
                open={detailModalVisible}
                onCancel={() => setDetailModalVisible(false)}
                footer={[
                    <Button key="close" onClick={() => setDetailModalVisible(false)}>
                        Fermer
                    </Button>
                ]}
                width={800}
            >
                {selectedLog && (
                    <Descriptions bordered column={1}>
                        <Descriptions.Item label="ID">{selectedLog.id}</Descriptions.Item>
                        <Descriptions.Item label="Date/Heure">
                            {dayjs(selectedLog.timestamp).format('DD/MM/YYYY HH:mm:ss')}
                        </Descriptions.Item>
                        <Descriptions.Item label="Module">
                            <Tag color="purple">{selectedLog.module_name}</Tag>
                        </Descriptions.Item>
                        <Descriptions.Item label="Action">
                            <Tag color={getActionColor(selectedLog.action_type)}>
                                {getActionLabel(selectedLog.action_type)}
                            </Tag>
                        </Descriptions.Item>
                        <Descriptions.Item label="Utilisateur">
                            {selectedLog.user_email || 'N/A'}
                        </Descriptions.Item>
                        <Descriptions.Item label="ID Utilisateur">
                            {selectedLog.user_id || 'N/A'}
                        </Descriptions.Item>
                        <Descriptions.Item label="ID Enregistrement">
                            {selectedLog.record_id || 'N/A'}
                        </Descriptions.Item>
                        <Descriptions.Item label="Adresse IP">
                            {selectedLog.ip_address || 'N/A'}
                        </Descriptions.Item>
                        <Descriptions.Item label="Description">
                            {selectedLog.description || 'N/A'}
                        </Descriptions.Item>
                        {selectedLog.old_data && (
                            <Descriptions.Item label="Anciennes données">
                                <pre style={{ maxHeight: 200, overflow: 'auto' }}>
                                    {JSON.stringify(selectedLog.old_data, null, 2)}
                                </pre>
                            </Descriptions.Item>
                        )}
                        {selectedLog.new_data && (
                            <Descriptions.Item label="Nouvelles données">
                                <pre style={{ maxHeight: 200, overflow: 'auto' }}>
                                    {JSON.stringify(selectedLog.new_data, null, 2)}
                                </pre>
                            </Descriptions.Item>
                        )}
                    </Descriptions>
                )}
            </Modal>
        </div>
    );
};

export default LogsPage;

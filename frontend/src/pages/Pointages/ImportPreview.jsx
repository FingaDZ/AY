import { useState, useEffect } from 'react';
import { Table, Button, Tag, message, Space, Card, Upload, Select, Statistic, Row, Col, Modal } from 'antd';
import {
    UploadOutlined,
    CheckCircleOutlined,
    WarningOutlined,
    CloseCircleOutlined,
    ReloadOutlined,
    CheckOutlined
} from '@ant-design/icons';
import { attendanceService } from '../../services';
import dayjs from 'dayjs';

function ImportPreview() {
    const [loading, setLoading] = useState(false);
    const [previewData, setPreviewData] = useState(null);
    const [selectedRowKeys, setSelectedRowKeys] = useState([]);
    const [filterStatus, setFilterStatus] = useState('all');
    const [manualMappings, setManualMappings] = useState({});

    const handleFileUpload = async (file) => {
        try {
            setLoading(true);
            const response = await attendanceService.previewImport(file);
            setPreviewData(response.data);

            // Auto-select all OK and WARNING items
            const autoSelect = response.data.items
                .filter(item => item.status !== 'error')
                .map(item => item.log_id);
            setSelectedRowKeys(autoSelect);

            message.success(`Preview généré: ${response.data.stats.total_logs} logs`);
        } catch (error) {
            message.error('Erreur lors de la prévisualisation');
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    const handleConfirmImport = async () => {
        if (selectedRowKeys.length === 0) {
            message.warning('Veuillez sélectionner au moins un log à importer');
            return;
        }

        Modal.confirm({
            title: 'Confirmer l\'importation',
            content: `Êtes-vous sûr de vouloir importer ${selectedRowKeys.length} logs ?`,
            onOk: async () => {
                try {
                    setLoading(true);
                    const response = await attendanceService.confirmImport({
                        session_id: previewData.session_id,
                        selected_log_ids: selectedRowKeys,
                        employee_mappings: manualMappings
                    });

                    message.success(`Import réussi: ${response.data.imported} logs importés`);
                    setPreviewData(null);
                    setSelectedRowKeys([]);
                    setManualMappings({});
                } catch (error) {
                    message.error('Erreur lors de l\'importation');
                    console.error(error);
                } finally {
                    setLoading(false);
                }
            }
        });
    };

    const getStatusIcon = (status) => {
        switch (status) {
            case 'ok':
                return <CheckCircleOutlined style={{ color: '#52c41a' }} />;
            case 'warning':
                return <WarningOutlined style={{ color: '#faad14' }} />;
            case 'error':
                return <CloseCircleOutlined style={{ color: '#ff4d4f' }} />;
            default:
                return null;
        }
    };

    const columns = [
        {
            title: 'Date',
            dataIndex: 'timestamp',
            key: 'timestamp',
            render: (timestamp) => dayjs(timestamp).format('DD/MM/YYYY HH:mm'),
            sorter: (a, b) => dayjs(a.timestamp).unix() - dayjs(b.timestamp).unix(),
            width: 150,
        },
        {
            title: 'Employé',
            dataIndex: 'employee_name',
            key: 'employee_name',
            render: (name, record) => (
                <div>
                    <div style={{ fontWeight: 500 }}>{name}</div>
                    {record.matched_employee_name && (
                        <div style={{ fontSize: '12px', color: '#1890ff' }}>
                            → {record.matched_employee_name}
                            {record.match_confidence < 100 && ` (${record.match_confidence}%)`}
                        </div>
                    )}
                    {record.matched_employee_poste && (
                        <div style={{ fontSize: '11px', color: '#888' }}>
                            {record.matched_employee_poste}
                        </div>
                    )}
                </div>
            ),
            width: 250,
        },
        {
            title: 'Type',
            dataIndex: 'log_type',
            key: 'log_type',
            render: (type) => (
                <Tag color={type === 'ENTRY' ? 'green' : 'orange'}>
                    {type === 'ENTRY' ? 'Entrée' : 'Sortie'}
                </Tag>
            ),
            width: 100,
        },
        {
            title: 'Durée',
            dataIndex: 'worked_minutes',
            key: 'worked_minutes',
            render: (minutes) => minutes ? `${minutes} min (${(minutes / 60).toFixed(1)}h)` : '-',
            width: 120,
        },
        {
            title: 'Statut',
            dataIndex: 'status',
            key: 'status',
            render: (status, record) => (
                <Space direction="vertical" size="small">
                    <Space>
                        {getStatusIcon(status)}
                        <Tag color={
                            status === 'ok' ? 'success' :
                                status === 'warning' ? 'warning' : 'error'
                        }>
                            {status.toUpperCase()}
                        </Tag>
                    </Space>
                    {record.warnings.map((warning, idx) => (
                        <div key={idx} style={{ fontSize: '11px', color: '#faad14' }}>
                            ⚠️ {warning}
                        </div>
                    ))}
                    {record.errors.map((error, idx) => (
                        <div key={idx} style={{ fontSize: '11px', color: '#ff4d4f' }}>
                            ❌ {error}
                        </div>
                    ))}
                </Space>
            ),
            width: 300,
        },
    ];

    const filteredData = previewData?.items.filter(item => {
        if (filterStatus === 'all') return true;
        return item.status === filterStatus;
    }) || [];

    const rowSelection = {
        selectedRowKeys,
        onChange: setSelectedRowKeys,
        getCheckboxProps: (record) => ({
            disabled: record.status === 'error',
        }),
    };

    return (
        <div style={{ padding: '24px' }}>
            <Card
                title="Prévisualisation Import Attendance"
                extra={
                    !previewData && (
                        <Upload
                            beforeUpload={(file) => {
                                handleFileUpload(file);
                                return false;
                            }}
                            showUploadList={false}
                            accept=".xlsx,.xls,.csv"
                        >
                            <Button
                                icon={<UploadOutlined />}
                                type="primary"
                                loading={loading}
                                size="large"
                            >
                                Charger Fichier Excel
                            </Button>
                        </Upload>
                    )
                }
            >
                {!previewData ? (
                    <div style={{ textAlign: 'center', padding: '60px 0' }}>
                        <UploadOutlined style={{ fontSize: '64px', color: '#d9d9d9' }} />
                        <p style={{ marginTop: '16px', color: '#999' }}>
                            Uploadez un fichier Excel pour prévisualiser l'import
                        </p>
                    </div>
                ) : (
                    <>
                        {/* Statistics */}
                        <Row gutter={16} style={{ marginBottom: '24px' }}>
                            <Col span={4}>
                                <Statistic
                                    title="Total Logs"
                                    value={previewData.stats.total_logs}
                                    prefix={<ReloadOutlined />}
                                />
                            </Col>
                            <Col span={4}>
                                <Statistic
                                    title="OK"
                                    value={previewData.stats.ok_count}
                                    valueStyle={{ color: '#52c41a' }}
                                    prefix={<CheckCircleOutlined />}
                                />
                            </Col>
                            <Col span={4}>
                                <Statistic
                                    title="Warnings"
                                    value={previewData.stats.warning_count}
                                    valueStyle={{ color: '#faad14' }}
                                    prefix={<WarningOutlined />}
                                />
                            </Col>
                            <Col span={4}>
                                <Statistic
                                    title="Errors"
                                    value={previewData.stats.error_count}
                                    valueStyle={{ color: '#ff4d4f' }}
                                    prefix={<CloseCircleOutlined />}
                                />
                            </Col>
                            <Col span={4}>
                                <Statistic
                                    title="Matchés"
                                    value={previewData.stats.matched_employees}
                                    valueStyle={{ color: '#1890ff' }}
                                />
                            </Col>
                            <Col span={4}>
                                <Statistic
                                    title="Conflits"
                                    value={previewData.stats.conflicts_detected}
                                    valueStyle={{ color: '#ff4d4f' }}
                                />
                            </Col>
                        </Row>

                        {/* Filters */}
                        <Space style={{ marginBottom: '16px' }}>
                            <span>Filtrer par statut:</span>
                            <Select
                                value={filterStatus}
                                onChange={setFilterStatus}
                                style={{ width: 150 }}
                            >
                                <Select.Option value="all">Tous</Select.Option>
                                <Select.Option value="ok">OK</Select.Option>
                                <Select.Option value="warning">Warning</Select.Option>
                                <Select.Option value="error">Error</Select.Option>
                            </Select>
                            <span style={{ marginLeft: '16px' }}>
                                {selectedRowKeys.length} logs sélectionnés
                            </span>
                        </Space>

                        {/* Table */}
                        <Table
                            rowSelection={rowSelection}
                            columns={columns}
                            dataSource={filteredData}
                            rowKey="log_id"
                            loading={loading}
                            pagination={{ pageSize: 20 }}
                            scroll={{ x: 1200 }}
                        />

                        {/* Actions */}
                        <div style={{ marginTop: '16px', textAlign: 'right' }}>
                            <Space>
                                <Button onClick={() => setPreviewData(null)}>
                                    Annuler
                                </Button>
                                <Button
                                    type="primary"
                                    icon={<CheckOutlined />}
                                    onClick={handleConfirmImport}
                                    disabled={selectedRowKeys.length === 0}
                                    loading={loading}
                                >
                                    Confirmer Import ({selectedRowKeys.length} logs)
                                </Button>
                            </Space>
                        </div>
                    </>
                )}
            </Card>
        </div>
    );
}

export default ImportPreview;

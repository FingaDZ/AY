import { useState, useEffect } from 'react';
import { Table, Button, Tag, message, Space, Card, Upload, Select, Statistic, Row, Col, Modal, DatePicker } from 'antd';
import {
    UploadOutlined,
    CheckCircleOutlined,
    WarningOutlined,
    CloseCircleOutlined,
    ReloadOutlined,
    CheckOutlined,
    ThunderboltOutlined
} from '@ant-design/icons';
import { attendanceService } from '../../services';
import dayjs from 'dayjs';
import 'dayjs/locale/fr';

const { RangePicker } = DatePicker;

dayjs.locale('fr');

function ImportPreview() {
    const [loading, setLoading] = useState(false);
    const [previewData, setPreviewData] = useState(null);
    const [selectedRowKeys, setSelectedRowKeys] = useState([]);
    const [filterStatus, setFilterStatus] = useState('all');
    const [filterEmployee, setFilterEmployee] = useState('all');
    const [dateRange, setDateRange] = useState(null);
    const [authorizedPhotos, setAuthorizedPhotos] = useState(new Set());

    const handleFileUpload = async (file) => {
        const hide = message.loading('Traitement du fichier en cours...', 0);
        try {
            setLoading(true);
            const response = await attendanceService.previewImport(file);
            setPreviewData(response.data);

            // Auto-select all OK and WARNING items
            const autoSelect = response.data.items
                .filter(item => item.status !== 'error')
                .map(item => item.log_id);
            setSelectedRowKeys(autoSelect);

            hide();

            // Show warning if there are unmatched employees
            if (response.data.stats.unmatched_employee_names && response.data.stats.unmatched_employee_names.length > 0) {
                const names = response.data.stats.unmatched_employee_names.join(', ');
                message.warning({
                    content: `Employés non trouvés dans le système: ${names}`,
                    duration: 8,
                    style: { marginTop: '20vh' }
                });
            }

            message.success(`Preview généré: ${response.data.stats.total_logs} jours`);
        } catch (error) {
            hide();
            message.error('Erreur lors de la prévisualisation');
            console.error('Preview error:', error);
            console.error('Response:', error.response?.data);
        } finally {
            setLoading(false);
        }
    };

    const handleConfirmImport = async () => {
        if (selectedRowKeys.length === 0) {
            message.warning('Veuillez sélectionner au moins un jour à importer');
            return;
        }

        Modal.confirm({
            title: 'Confirmer l\'importation',
            content: `Êtes-vous sûr de vouloir importer ${selectedRowKeys.length} jours de pointage ?`,
            onOk: async () => {
                try {
                    setLoading(true);
                    const response = await attendanceService.confirmImport({
                        session_id: previewData.session_id,
                        selected_log_ids: selectedRowKeys,
                        employee_mappings: {}
                    });

                    message.success(`Import réussi: ${response.data.imported} jours importés`);
                    setPreviewData(null);
                    setSelectedRowKeys([]);
                } catch (error) {
                    message.error('Erreur lors de l\'importation');
                    console.error(error);
                } finally {
                    setLoading(false);
                }
            }
        });
    };

    const handleDirectImport = async (file) => {
        Modal.confirm({
            title: 'Import Direct',
            content: 'Importer directement sans prévisualisation ? (Non recommandé)',
            onOk: async () => {
                try {
                    setLoading(true);
                    const previewResponse = await attendanceService.previewImport(file);

                    // Auto-import all valid items
                    const validIds = previewResponse.data.items
                        .filter(item => item.status !== 'error')
                        .map(item => item.log_id);

                    const importResponse = await attendanceService.confirmImport({
                        session_id: previewResponse.data.session_id,
                        selected_log_ids: validIds,
                        employee_mappings: {}
                    });

                    message.success(`Import direct réussi: ${importResponse.data.imported} jours`);
                } catch (error) {
                    message.error('Erreur lors de l\'import direct');
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
            dataIndex: 'work_date',
            key: 'work_date',
            render: (date) => dayjs(date).format('DD/MM/YYYY'),
            sorter: (a, b) => dayjs(a.work_date).unix() - dayjs(b.work_date).unix(),
            width: 120,
        },
        {
            title: 'Jour',
            dataIndex: 'work_date',
            key: 'day',
            render: (date) => {
                const day = dayjs(date).format('dddd');
                const isFriday = dayjs(date).day() === 5;
                return (
                    <span style={{ color: isFriday ? '#faad14' : 'inherit' }}>
                        {day}
                    </span>
                );
            },
            width: 100,
        },
        {
            title: 'Employé',
            dataIndex: 'matched_employee_name',
            key: 'employee',
            render: (name, record) => (
                <div>
                    <div style={{ fontWeight: 500 }}>{name || record.employee_name}</div>
                    {record.matched_employee_poste && (
                        <div style={{ fontSize: '11px', color: '#888' }}>
                            {record.matched_employee_poste}
                        </div>
                    )}
                    {record.match_confidence < 100 && (
                        <div style={{ fontSize: '10px', color: '#1890ff' }}>
                            Match: {record.match_confidence}%
                        </div>
                    )}
                </div>
            ),
            width: 200,
        },
        {
            title: 'Photo',
            dataIndex: 'has_photo',
            key: 'has_photo',
            render: (hasPhoto, record) => {
                if (!hasPhoto) return <Tag>Vide</Tag>;
                if (hasPhoto === 'Verifier') {
                    const isAuthorized = authorizedPhotos.has(record.log_id);
                    return (
                        <Space>
                            <Tag color="warning">Verifier</Tag>
                            {!isAuthorized && (
                                <Button
                                    size="small"
                                    type="primary"
                                    onClick={() => {
                                        setAuthorizedPhotos(prev => new Set([...prev, record.log_id]));
                                        message.success('Photo autorisée');
                                    }}
                                >
                                    Autoriser
                                </Button>
                            )}
                            {isAuthorized && <Tag color="success">✓ Autorisé</Tag>}
                        </Space>
                    );
                }
                return <Tag color="blue">{hasPhoto}</Tag>;
            },
            width: 200,
        },
        {
            title: 'Entrée',
            dataIndex: 'entry_time',
            key: 'entry_time',
            render: (time, record) => {
                if (!time) return '-';
                const formatted = dayjs(time).format('HH:mm');
                return record.was_estimated ? (
                    <span style={{ color: '#faad14' }}>{formatted} *</span>
                ) : formatted;
            },
            width: 80,
        },
        {
            title: 'Sortie',
            dataIndex: 'exit_time',
            key: 'exit_time',
            render: (time, record) => {
                if (!time) return '-';
                const formatted = dayjs(time).format('HH:mm');
                return record.was_estimated ? (
                    <span style={{ color: '#faad14' }}>{formatted} *</span>
                ) : formatted;
            },
            width: 80,
        },
        {
            title: 'Durée',
            dataIndex: 'worked_hours',
            key: 'worked_hours',
            render: (hours) => hours ? `${hours}h` : '-',
            width: 80,
        },
        {
            title: 'H. Sup',
            dataIndex: 'overtime_hours',
            key: 'overtime_hours',
            render: (hours) => hours > 0 ? (
                <span style={{ color: '#ff4d4f', fontWeight: 500 }}>+{hours}h</span>
            ) : '-',
            width: 80,
        },
        {
            title: 'Statut',
            dataIndex: 'status',
            key: 'status',
            render: (status, record) => (
                <Space direction="vertical" size="small" style={{ width: '100%' }}>
                    <Space>
                        {getStatusIcon(status)}
                        <Tag color={
                            status === 'ok' ? 'success' :
                                status === 'warning' ? 'warning' : 'error'
                        }>
                            {status.toUpperCase()}
                        </Tag>
                    </Space>
                    {record.warnings?.map((warning, idx) => (
                        <div key={idx} style={{ fontSize: '10px', color: '#faad14' }}>
                            ⚠️ {warning}
                        </div>
                    ))}
                    {record.errors?.map((error, idx) => (
                        <div key={idx} style={{ fontSize: '10px', color: '#ff4d4f' }}>
                            ❌ {error}
                        </div>
                    ))}
                </Space>
            ),
            width: 250,
        },
        {
            title: 'Pointage',
            dataIndex: 'day_value',
            key: 'day_value',
            render: (value) => {
                if (value === 1) {
                    return <Tag color="success">✓ Travaillé</Tag>;
                } else {
                    return <Tag color="default">✗ Non Pointé</Tag>;
                }
            },
            width: 120,
        },
    ];

    // Get unique employees for filter
    const uniqueEmployees = previewData ?
        [...new Map(previewData.items.map(item => [
            item.matched_employee_id,
            { id: item.matched_employee_id, name: item.matched_employee_name || item.employee_name }
        ])).values()] : [];

    // Filter data
    const filteredData = previewData?.items.filter(item => {
        // Status filter
        if (filterStatus !== 'all' && item.status !== filterStatus) return false;

        // Employee filter
        if (filterEmployee !== 'all' && item.matched_employee_id !== filterEmployee) return false;

        // Date range filter
        if (dateRange && dateRange.length === 2) {
            const itemDate = dayjs(item.work_date);
            if (itemDate.isBefore(dateRange[0], 'day') || itemDate.isAfter(dateRange[1], 'day')) {
                return false;
            }
        }

        return true;
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
                title="Import Pointages - Prévisualisation"
                extra={
                    !previewData ? (
                        <Space>
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
                                    Charger & Prévisualiser
                                </Button>
                            </Upload>
                            <Upload
                                beforeUpload={(file) => {
                                    handleDirectImport(file);
                                    return false;
                                }}
                                showUploadList={false}
                                accept=".xlsx,.xls,.csv"
                            >
                                <Button
                                    icon={<ThunderboltOutlined />}
                                    danger
                                    loading={loading}
                                    size="large"
                                >
                                    Import Direct
                                </Button>
                            </Upload>
                        </Space>
                    ) : null
                }
            >
                {!previewData ? (
                    <div style={{ textAlign: 'center', padding: '60px 0' }}>
                        <UploadOutlined style={{ fontSize: '64px', color: '#d9d9d9' }} />
                        <p style={{ marginTop: '16px', color: '#999', fontSize: '16px' }}>
                            Uploadez un fichier Excel pour prévisualiser l'import
                        </p>
                        <p style={{ color: '#999', fontSize: '12px' }}>
                            * Estimation automatique si entrée ou sortie manquante
                        </p>
                    </div>
                ) : (
                    <>
                        {/* Statistics */}
                        <Row gutter={16} style={{ marginBottom: '24px' }}>
                            <Col span={4}>
                                <Statistic
                                    title="Total Jours"
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
                                    title="Employés"
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
                        <Space style={{ marginBottom: '16px' }} wrap>
                            <span>Filtrer par:</span>
                            <Select
                                value={filterStatus}
                                onChange={setFilterStatus}
                                style={{ width: 150 }}
                            >
                                <Select.Option value="all">Tous statuts</Select.Option>
                                <Select.Option value="ok">OK</Select.Option>
                                <Select.Option value="warning">Warning</Select.Option>
                                <Select.Option value="error">Error</Select.Option>
                            </Select>

                            <Select
                                value={filterEmployee}
                                onChange={setFilterEmployee}
                                style={{ width: 200 }}
                                showSearch
                                placeholder="Tous les employés"
                                optionFilterProp="children"
                            >
                                <Select.Option value="all">Tous les employés</Select.Option>
                                {uniqueEmployees.map(emp => (
                                    <Select.Option key={emp.id} value={emp.id}>
                                        {emp.name}
                                    </Select.Option>
                                ))}
                            </Select>

                            <RangePicker
                                value={dateRange}
                                onChange={setDateRange}
                                format="DD/MM/YYYY"
                                placeholder={['Date début', 'Date fin']}
                            />

                            <span style={{ marginLeft: '16px', color: '#666' }}>
                                {selectedRowKeys.length} / {filteredData.length} jours sélectionnés
                            </span>
                        </Space>

                        {/* Table */}
                        <Table
                            rowSelection={rowSelection}
                            columns={columns}
                            dataSource={filteredData}
                            rowKey="log_id"
                            loading={loading}
                            pagination={{ pageSize: 50, showSizeChanger: true, showTotal: (total) => `Total: ${total} jours` }}
                            scroll={{ x: 1400 }}
                            size="small"
                        />

                        {/* Actions */}
                        <div style={{ marginTop: '16px', textAlign: 'right' }}>
                            <Space>
                                <Button onClick={() => {
                                    setPreviewData(null);
                                    setSelectedRowKeys([]);
                                    setFilterStatus('all');
                                    setFilterEmployee('all');
                                    setDateRange(null);
                                    setAuthorizedPhotos(new Set());
                                }}>
                                    Annuler
                                </Button>
                                <Button
                                    type="primary"
                                    icon={<CheckOutlined />}
                                    onClick={handleConfirmImport}
                                    disabled={
                                        selectedRowKeys.length === 0 ||
                                        (filteredData.some(item =>
                                            item.has_photo === 'Verifier' &&
                                            selectedRowKeys.includes(item.log_id) &&
                                            !authorizedPhotos.has(item.log_id)
                                        ))
                                    }
                                    loading={loading}
                                    size="large"
                                >
                                    Confirmer Import ({selectedRowKeys.length} jours)
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

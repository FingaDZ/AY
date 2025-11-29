import { useState } from 'react';
import { Card, DatePicker, Button, Select, message, Statistic, Row, Col, Spin, Table, Tag, Upload } from 'antd';
import { DownloadOutlined, SyncOutlined, UploadOutlined } from '@ant-design/icons';
import { attendanceService } from '../../services';
import dayjs from 'dayjs';

const { RangePicker } = DatePicker;

function ImportAttendance() {
    const [loading, setLoading] = useState(false);
    const [dateRange, setDateRange] = useState([dayjs().startOf('month'), dayjs().endOf('month')]);
    const [summary, setSummary] = useState(null);

    const handleImport = async () => {
        if (!dateRange || dateRange.length !== 2) {
            message.error('Veuillez sélectionner une plage de dates');
            return;
        }

        try {
            setLoading(true);
            const response = await attendanceService.importLogs(
                dateRange[0].format('YYYY-MM-DD'),
                dateRange[1].format('YYYY-MM-DD')
            );

            handleResponse(response.data);
        } catch (error) {
            message.error('Erreur lors de l\'importation API');
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    const handleFileImport = async (file) => {
        try {
            setLoading(true);
            const response = await attendanceService.importFile(file);
            handleResponse(response.data);
        } catch (error) {
            message.error('Erreur lors de l\'importation du fichier');
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    const handleResponse = (data) => {
        setSummary(data);

        if (data.imported > 0) {
            message.success(`${data.imported} logs importés avec succès`);
        }

        if (data.conflicts > 0) {
            message.warning(`${data.conflicts} conflits détectés. Consultez la page Conflits.`);
        }

        if (data.skipped_no_mapping > 0) {
            message.info(`${data.skipped_no_mapping} logs ignorés (employés non mappés)`);
        }

        if (data.incomplete_pending_validation > 0) {
            message.warning(`${data.incomplete_pending_validation} logs incomplets importés avec estimation. À valider.`);
        }
    };

    return (
        <div style={{ padding: '24px' }}>
            <Card title="Importer Pointages depuis Attendance" extra={<SyncOutlined spin={loading} />}>
                <Row gutter={16} style={{ marginBottom: 24 }}>
                    <Col xs={24} md={12}>
                        <label style={{ display: 'block', marginBottom: 8, fontWeight: 500 }}>
                            Plage de dates
                        </label>
                        <RangePicker
                            value={dateRange}
                            onChange={setDateRange}
                            style={{ width: '100%' }}
                            format="DD/MM/YYYY"
                            disabled={loading}
                        />
                    </Col>
                </Row>

                <div style={{ display: 'flex', gap: '10px' }}>
                    <Button
                        type="primary"
                        icon={<DownloadOutlined />}
                        onClick={handleImport}
                        loading={loading}
                        size="large"
                    >
                        Importer depuis API
                    </Button>

                    <Upload
                        beforeUpload={(file) => {
                            handleFileImport(file);
                            return false; // Prevent auto upload
                        }}
                        showUploadList={false}
                        accept=".xlsx,.xls,.csv"
                    >
                        <Button
                            icon={<UploadOutlined />}
                            loading={loading}
                            size="large"
                        >
                            Importer Fichier Excel
                        </Button>
                    </Upload>
                </div>

                {summary && (
                    <div style={{ marginTop: 32 }}>
                        <h3 style={{ marginBottom: 16 }}>Résumé de l'importation</h3>
                        <Row gutter={16}>
                            <Col xs={12} sm={8} md={4}>
                                <Card>
                                    <Statistic
                                        title="Total Logs"
                                        value={summary.total_logs}
                                    />
                                </Card>
                            </Col>
                            <Col xs={12} sm={8} md={4}>
                                <Card>
                                    <Statistic
                                        title="Importés"
                                        value={summary.imported}
                                        valueStyle={{ color: '#3f8600' }}
                                    />
                                </Card>
                            </Col>
                            <Col xs={12} sm={8} md={4}>
                                <Card>
                                    <Statistic
                                        title="Doublons"
                                        value={summary.skipped_duplicate}
                                        valueStyle={{ color: '#999' }}
                                    />
                                </Card>
                            </Col>
                            <Col xs={12} sm={8} md={4}>
                                <Card>
                                    <Statistic
                                        title="Sans Mapping"
                                        value={summary.skipped_no_mapping}
                                        valueStyle={{ color: '#cf1322' }}
                                    />
                                </Card>
                            </Col>
                            <Col xs={12} sm={8} md={4}>
                                <Card>
                                    <Statistic
                                        title="Conflits"
                                        value={summary.conflicts}
                                        valueStyle={{ color: '#faad14' }}
                                    />
                                </Card>
                            </Col>
                            <Col xs={12} sm={8} md={4}>
                                <Card>
                                    <Statistic
                                        title="Erreurs"
                                        value={summary.errors}
                                        valueStyle={{ color: '#cf1322' }}
                                    />
                                </Card>
                            </Col>
                            <Col xs={12} sm={8} md={4}>
                                <Card>
                                    <Statistic
                                        title="Incomplets"
                                        value={summary.incomplete_pending_validation}
                                        valueStyle={{ color: '#faad14' }}
                                    />
                                </Card>
                            </Col>
                        </Row>
                    </div>
                )}

                {summary && summary.details && summary.details.length > 0 && (
                    <div style={{ marginTop: 32 }}>
                        <h3 style={{ marginBottom: 16 }}>Détails des problèmes</h3>
                        <Table
                            dataSource={summary.details}
                            rowKey="log_id"
                            pagination={{ pageSize: 10 }}
                            columns={[
                                {
                                    title: 'ID Log',
                                    dataIndex: 'log_id',
                                    key: 'log_id',
                                    width: 100,
                                },
                                {
                                    title: 'Employé',
                                    dataIndex: 'employee_name',
                                    key: 'employee_name',
                                },
                                {
                                    title: 'Statut',
                                    dataIndex: 'status',
                                    key: 'status',
                                    render: (status) => {
                                        let color = 'default';
                                        if (status === 'error') color = 'red';
                                        if (status === 'conflict') color = 'orange';
                                        if (status === 'incomplete') color = 'gold';
                                        return <Tag color={color}>{status.toUpperCase()}</Tag>;
                                    }
                                },
                                {
                                    title: 'Message',
                                    dataIndex: 'message',
                                    key: 'message',
                                },
                            ]}
                        />
                    </div>
                )}
            </Card>
        </div>
    );
}

export default ImportAttendance;

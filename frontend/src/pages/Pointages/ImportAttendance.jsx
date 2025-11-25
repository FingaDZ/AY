import { useState } from 'react';
import { Card, DatePicker, Button, Select, message, Statistic, Row, Col, Spin } from 'antd';
import { DownloadOutlined, SyncOutlined } from '@ant-design/icons';
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

            setSummary(response.data);

            if (response.data.imported > 0) {
                message.success(`${response.data.imported} logs importés avec succès`);
            }

            if (response.data.conflicts > 0) {
                message.warning(`${response.data.conflicts} conflits détectés. Consultez la page Conflits.`);
            }

            if (response.data.skipped_no_mapping > 0) {
                message.info(`${response.data.skipped_no_mapping} logs ignorés (employés non mappés)`);
            }
        } catch (error) {
            message.error('Erreur lors de l\'importation');
            console.error(error);
        } finally {
            setLoading(false);
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

                <Button
                    type="primary"
                    icon={<DownloadOutlined />}
                    onClick={handleImport}
                    loading={loading}
                    size="large"
                >
                    Importer les Pointages
                </Button>

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
                        </Row>
                    </div>
                )}
            </Card>
        </div>
    );
}

export default ImportAttendance;

import { useState, useEffect } from 'react';
import { Card, Table, Select, InputNumber, Button, Space, message, Tag } from 'antd';
import { SearchOutlined, FilePdfOutlined, FileZipOutlined } from '@ant-design/icons';
import { salaireService } from '../../services';

const { Option } = Select;

const currentYear = new Date().getFullYear();

function SalaireHistorique() {
    const [loading, setLoading] = useState(false);
    const [historique, setHistorique] = useState([]);
    const [pagination, setPagination] = useState({
        current: 1,
        pageSize: 25,
        total: 0
    });
    const [filters, setFilters] = useState({
        annee: null,
        mois: null
    });

    useEffect(() => {
        loadHistorique();
    }, [pagination.current, pagination.pageSize]);

    const loadHistorique = async () => {
        try {
            setLoading(true);
            const params = {
                page: pagination.current,
                per_page: pagination.pageSize,
                ...(filters.annee && { annee: filters.annee }),
                ...(filters.mois && { mois: filters.mois })
            };

            const response = await salaireService.getHistorique(params);
            setHistorique(response.data.historique || []);
            setPagination(prev => ({
                ...prev,
                total: response.data.pagination.total
            }));
        } catch (error) {
            message.error('Erreur lors du chargement de l\'historique');
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    const handleSearch = () => {
        setPagination(prev => ({ ...prev, current: 1 }));
        loadHistorique();
    };

    const handleReset = () => {
        setFilters({ annee: null, mois: null });
        setPagination(prev => ({ ...prev, current: 1 }));
        setTimeout(() => loadHistorique(), 100);
    };

    const handleTableChange = (pag) => {
        setPagination({
            current: pag.current,
            pageSize: pag.pageSize,
            total: pagination.total
        });
    };

    const handleDownloadPDF = async (annee, mois) => {
        try {
            setLoading(true);
            const response = await salaireService.genererRapport({ annee, mois });

            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `rapport_salaires_${mois.toString().padStart(2, '0')}_${annee}.pdf`);
            document.body.appendChild(link);
            link.click();
            link.remove();

            message.success('Rapport PDF téléchargé');
        } catch (error) {
            message.error('Erreur lors de la génération du PDF');
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    const handleDownloadZIP = async (annee, mois) => {
        try {
            setLoading(true);
            const response = await salaireService.genererBulletins({ annee, mois, jours_supplementaires: 0 });

            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `bulletins_paie_${mois.toString().padStart(2, '0')}_${annee}.zip`);
            document.body.appendChild(link);
            link.click();
            link.remove();

            message.success('Bulletins ZIP téléchargés');
        } catch (error) {
            message.error('Erreur lors de la génération du ZIP');
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    const columns = [
        {
            title: 'Année',
            dataIndex: 'annee',
            key: 'annee',
            width: 100,
            align: 'center',
            sorter: (a, b) => a.annee - b.annee
        },
        {
            title: 'Mois',
            dataIndex: 'mois',
            key: 'mois',
            width: 150,
            align: 'center',
            render: (mois) => {
                const monthName = new Date(2000, mois - 1).toLocaleString('fr-FR', { month: 'long' });
                return monthName.charAt(0).toUpperCase() + monthName.slice(1);
            }
        },
        {
            title: 'Nb Employés',
            dataIndex: 'nb_employes',
            key: 'nb_employes',
            width: 120,
            align: 'center',
            render: (val) => <Tag color="blue">{val}</Tag>
        },
        {
            title: 'Total Cotisable',
            dataIndex: 'total_cotisable',
            key: 'total_cotisable',
            width: 150,
            align: 'right',
            render: (val) => `${parseFloat(val || 0).toLocaleString('fr-FR', { minimumFractionDigits: 2 })} DA`
        },
        {
            title: 'Total IRG',
            dataIndex: 'total_irg',
            key: 'total_irg',
            width: 150,
            align: 'right',
            render: (val) => (
                <span style={{ color: '#ff4d4f' }}>
                    {parseFloat(val || 0).toLocaleString('fr-FR', { minimumFractionDigits: 2 })} DA
                </span>
            )
        },
        {
            title: 'Total Net',
            dataIndex: 'total_net',
            key: 'total_net',
            width: 180,
            align: 'right',
            render: (val) => (
                <span style={{ fontWeight: 'bold', color: '#52c41a', fontSize: '14px' }}>
                    {parseFloat(val || 0).toLocaleString('fr-FR', { minimumFractionDigits: 2 })} DA
                </span>
            )
        },
        {
            title: 'Actions',
            key: 'actions',
            width: 200,
            align: 'center',
            render: (_, record) => (
                <Space>
                    <Button
                        type="primary"
                        size="small"
                        icon={<FilePdfOutlined />}
                        onClick={() => handleDownloadPDF(record.annee, record.mois)}
                    >
                        PDF
                    </Button>
                    <Button
                        type="default"
                        size="small"
                        icon={<FileZipOutlined />}
                        onClick={() => handleDownloadZIP(record.annee, record.mois)}
                        style={{ backgroundColor: '#52c41a', color: 'white', borderColor: '#52c41a' }}
                    >
                        ZIP
                    </Button>
                </Space>
            )
        }
    ];

    return (
        <div>
            <h2>Historique des Salaires</h2>

            <Card style={{ marginBottom: 16 }}>
                <Space size="middle" wrap>
                    <div>
                        <label style={{ marginRight: 8, fontWeight: 'bold' }}>Année:</label>
                        <InputNumber
                            value={filters.annee}
                            min={2000}
                            max={2100}
                            style={{ width: 120 }}
                            placeholder="Toutes"
                            onChange={(value) => setFilters({ ...filters, annee: value })}
                        />
                    </div>

                    <div>
                        <label style={{ marginRight: 8, fontWeight: 'bold' }}>Mois:</label>
                        <Select
                            value={filters.mois}
                            style={{ width: 150 }}
                            placeholder="Tous"
                            allowClear
                            onChange={(value) => setFilters({ ...filters, mois: value })}
                        >
                            {[...Array(12)].map((_, i) => (
                                <Option key={i + 1} value={i + 1}>
                                    {new Date(2000, i).toLocaleString('fr-FR', { month: 'long' })}
                                </Option>
                            ))}
                        </Select>
                    </div>

                    <Button
                        type="primary"
                        icon={<SearchOutlined />}
                        onClick={handleSearch}
                    >
                        Rechercher
                    </Button>

                    <Button onClick={handleReset}>
                        Réinitialiser
                    </Button>
                </Space>
            </Card>

            <Card>
                <Table
                    columns={columns}
                    dataSource={historique}
                    rowKey={(record) => `${record.annee}-${record.mois}`}
                    loading={loading}
                    pagination={{
                        current: pagination.current,
                        pageSize: pagination.pageSize,
                        total: pagination.total,
                        showTotal: (total) => `Total: ${total} période(s)`,
                        showSizeChanger: true,
                        pageSizeOptions: ['10', '25', '50', '100']
                    }}
                    onChange={handleTableChange}
                    bordered
                    size="small"
                />
            </Card>
        </div>
    );
}

export default SalaireHistorique;

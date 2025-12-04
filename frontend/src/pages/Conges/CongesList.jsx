import React, { useState, useEffect } from 'react';
import { Table, Card, Input, Button, Tag, Modal, Form, InputNumber, message, Select, Statistic, Row, Col } from 'antd';
import { SearchOutlined, EditOutlined, CalendarOutlined } from '@ant-design/icons';
import api from '../../services/api';

const { Option } = Select;

const CongesList = () => {
    const [conges, setConges] = useState([]);
    const [loading, setLoading] = useState(false);
    const [employes, setEmployes] = useState([]);
    const [searchText, setSearchText] = useState('');

    // Filtres
    const [selectedEmploye, setSelectedEmploye] = useState(null);
    const [selectedAnnee, setSelectedAnnee] = useState(new Date().getFullYear());

    // Modal Saisie
    const [isModalVisible, setIsModalVisible] = useState(false);
    const [currentConge, setCurrentConge] = useState(null);
    const [form] = Form.useForm();

    // Stats
    const [synthese, setSynthese] = useState(null);

    useEffect(() => {
        fetchConges();
        fetchEmployes();
    }, [selectedEmploye, selectedAnnee]);

    useEffect(() => {
        if (selectedEmploye) {
            fetchSynthese(selectedEmploye);
        } else {
            setSynthese(null);
        }
    }, [selectedEmploye]);

    const fetchEmployes = async () => {
        try {
            const response = await api.get('/employes');
            setEmployes(response.data);
        } catch (error) {
            console.error("Erreur chargement employés", error);
        }
    };

    const fetchConges = async () => {
        setLoading(true);
        try {
            let url = `/api/conges/?annee=${selectedAnnee}`;
            if (selectedEmploye) {
                url += `&employe_id=${selectedEmploye}`;
            }
            const response = await api.get(url);
            setConges(response.data);
        } catch (error) {
            message.error("Erreur lors du chargement des congés");
        } finally {
            setLoading(false);
        }
    };

    const fetchSynthese = async (employeId) => {
        try {
            const response = await api.get(`/conges/synthese/${employeId}`);
            setSynthese(response.data);
        } catch (error) {
            console.error("Erreur synthèse", error);
        }
    };

    const handleEdit = (record) => {
        setCurrentConge(record);
        form.setFieldsValue({
            jours_pris: record.jours_conges_pris
        });
        setIsModalVisible(true);
    };

    const handleSave = async () => {
        try {
            const values = await form.validateFields();
            await api.put(`/conges/${currentConge.id}/consommation`, {
                jours_pris: values.jours_pris
            });
            message.success("Consommation mise à jour");
            setIsModalVisible(false);
            fetchConges();
            if (selectedEmploye) fetchSynthese(selectedEmploye);
        } catch (error) {
            message.error("Erreur lors de la mise à jour");
        }
    };

    const columns = [
        {
            title: 'Employé',
            key: 'employe',
            render: (text, record) => `${record.employe_prenom} ${record.employe_nom}`,
            filteredValue: [searchText],
            onFilter: (value, record) => {
                const fullName = `${record.employe_prenom} ${record.employe_nom}`.toLowerCase();
                return fullName.includes(value.toLowerCase());
            },
        },
        {
            title: 'Période',
            key: 'periode',
            render: (text, record) => <Tag color="blue">{record.mois}/{record.annee}</Tag>,
        },
        {
            title: 'Jours Travaillés',
            dataIndex: 'jours_travailles',
            key: 'jours_travailles',
        },
        {
            title: 'Acquis (Jours)',
            dataIndex: 'jours_conges_acquis',
            key: 'jours_conges_acquis',
            render: (val) => <span className="font-semibold text-green-600">{val}</span>
        },
        {
            title: 'Pris (Jours)',
            dataIndex: 'jours_conges_pris',
            key: 'jours_conges_pris',
            render: (val) => <span className="font-semibold text-orange-500">{val}</span>
        },
        {
            title: 'Solde Mensuel',
            dataIndex: 'jours_conges_restants',
            key: 'jours_conges_restants',
            render: (val) => (
                <Tag color={val >= 0 ? 'green' : 'red'}>
                    {val}
                </Tag>
            )
        },
        {
            title: 'Action',
            key: 'action',
            render: (text, record) => (
                <Button
                    type="primary"
                    size="small"
                    icon={<EditOutlined />}
                    onClick={() => handleEdit(record)}
                >
                    Saisir
                </Button>
            ),
        },
    ];

    return (
        <div className="p-6">
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-2xl font-bold text-gray-800">Gestion des Congés</h1>
                <div className="flex gap-4">
                    <Select
                        style={{ width: 200 }}
                        placeholder="Filtrer par employé"
                        allowClear
                        onChange={setSelectedEmploye}
                        showSearch
                        optionFilterProp="children"
                    >
                        {employes.map(emp => (
                            <Option key={emp.id} value={emp.id}>{emp.prenom} {emp.nom}</Option>
                        ))}
                    </Select>
                    <InputNumber
                        style={{ width: 100 }}
                        value={selectedAnnee}
                        onChange={setSelectedAnnee}
                        prefix={<CalendarOutlined />}
                    />
                </div>
            </div>

            {synthese && (
                <Card className="mb-6 bg-blue-50 border-blue-200">
                    <Row gutter={16}>
                        <Col span={8}>
                            <Statistic title="Total Acquis (Année)" value={synthese.total_acquis} precision={1} suffix="jours" valueStyle={{ color: '#3f8600' }} />
                        </Col>
                        <Col span={8}>
                            <Statistic title="Total Consommé" value={synthese.total_pris} precision={1} suffix="jours" valueStyle={{ color: '#cf1322' }} />
                        </Col>
                        <Col span={8}>
                            <Statistic title="Solde Global" value={synthese.solde} precision={1} suffix="jours" valueStyle={{ color: '#1890ff' }} />
                        </Col>
                    </Row>
                </Card>
            )}

            <Card>
                <div className="mb-4">
                    <Input
                        placeholder="Rechercher un employé..."
                        prefix={<SearchOutlined />}
                        onChange={e => setSearchText(e.target.value)}
                        style={{ width: 300 }}
                    />
                </div>

                <Table
                    columns={columns}
                    dataSource={conges}
                    rowKey="id"
                    loading={loading}
                    pagination={{ pageSize: 12 }}
                />
            </Card>

            <Modal
                title="Saisie Consommation Congé"
                open={isModalVisible}
                onOk={handleSave}
                onCancel={() => setIsModalVisible(false)}
            >
                <Form form={form} layout="vertical">
                    <p className="mb-4 text-gray-500">
                        Saisissez le nombre de jours de congé pris pour la période {currentConge?.mois}/{currentConge?.annee}.
                    </p>
                    <Form.Item
                        name="jours_pris"
                        label="Jours Pris"
                        rules={[{ required: true, message: 'Veuillez saisir une valeur' }]}
                    >
                        <InputNumber min={0} max={30} step={0.5} style={{ width: '100%' }} />
                    </Form.Item>
                </Form>
            </Modal>
        </div>
    );
};

export default CongesList;

import React, { useState, useEffect } from 'react';
import { Table, Card, Button, Tag, Modal, Form, InputNumber, message, Select, Statistic, Row, Col, Space, Alert, Popconfirm, Divider, Descriptions, Input } from 'antd';
import { EditOutlined, CalendarOutlined, DownloadOutlined, EyeOutlined, DeleteOutlined, PlusOutlined } from '@ant-design/icons';
import api from '../../services/api';

const { Option } = Select;

const CongesList = () => {
    const [conges, setConges] = useState([]);
    const [loading, setLoading] = useState(false);
    const [employes, setEmployes] = useState([]);

    // Filtres
    const [selectedEmploye, setSelectedEmploye] = useState(null);
    const [selectedAnnee, setSelectedAnnee] = useState(new Date().getFullYear());

    // Modal Déduction v3.7.0
    const [deductionModalVisible, setDeductionModalVisible] = useState(false);
    const [selectedEmployeForDeduction, setSelectedEmployeForDeduction] = useState(null);
    const [deductionForm] = Form.useForm();

    // Modal Détails Périodes
    const [detailsModalVisible, setDetailsModalVisible] = useState(false);
    const [detailsEmploye, setDetailsEmploye] = useState(null);
    const [detailsEmployeId, setDetailsEmployeId] = useState(null);
    const [detailsPeriodes, setDetailsPeriodes] = useState([]);
    const [deductions, setDeductions] = useState([]);

    // Stats globales
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
            setEmployes(response.data.employes || []);
        } catch (error) {
            console.error("Erreur chargement employés", error);
        }
    };

    const fetchConges = async () => {
        setLoading(true);
        try {
            let url = `/conges/?annee=${selectedAnnee}`;
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
            // v3.7.0: Endpoint retourne total_deduit au lieu de total_pris
            setSynthese(response.data);
        } catch (error) {
            console.error("Erreur synthèse", error);
        }
    };

    const fetchDeductions = async (employeId) => {
        try {
            const response = await api.get(`/deductions-conges/employe/${employeId}`);
            setDeductions(response.data);
        } catch (error) {
            console.error("Erreur chargement déductions", error);
        }
    };

    // Grouper les congés par employé
    const groupCongesByEmploye = () => {
        const grouped = {};
        conges.forEach(conge => {
            const key = `${conge.employe_id}`;
            if (!grouped[key]) {
                grouped[key] = {
                    employe_id: conge.employe_id,
                    employe_nom: `${conge.employe_prenom} ${conge.employe_nom}`,
                    periodes: [],
                    total_travailles: 0,
                    total_acquis: 0,
                    total_pris: 0,
                    solde: 0
                };
            }
            grouped[key].periodes.push(conge);
            grouped[key].total_travailles += conge.jours_travailles || 0;
            grouped[key].total_acquis += conge.jours_conges_acquis || 0;
            grouped[key].total_pris += conge.jours_conges_pris || 0;
        });

        // Calculer soldes
        Object.keys(grouped).forEach(key => {
            grouped[key].solde = grouped[key].total_acquis - grouped[key].total_pris;
        });

        return Object.values(grouped);
    };

    const handleOpenDeductionModal = (employeId, employeNom) => {
        // v3.7.0: Ouvrir modal simple de création de déduction
        setSelectedEmployeForDeduction(employeId);
        deductionForm.resetFields();
        deductionForm.setFieldsValue({
            mois_deduction: new Date().getMonth() + 1,
            annee_deduction: new Date().getFullYear(),
            type_conge: 'ANNUEL'
        });
        setDeductionModalVisible(true);
    };

    const handleShowDetails = (employe) => {
        setDetailsEmploye(employe.employe_nom);
        setDetailsEmployeId(employe.employe_id);
        setDetailsPeriodes(employe.periodes);
        fetchDeductions(employe.employe_id);  // v3.7.0: Charger déductions
        setDetailsModalVisible(true);
    };

    const handleCreateDeduction = async () => {
        try {
            const values = await deductionForm.validateFields();
            const response = await api.post('/deductions-conges/', {
                employe_id: selectedEmployeForDeduction,
                jours_deduits: values.jours_deduits,
                mois_deduction: values.mois_deduction,
                annee_deduction: values.annee_deduction,
                type_conge: values.type_conge || 'ANNUEL',
                motif: values.motif
            });
            
            message.success(
                `Déduction créée: ${response.data.jours_deduits}j pour bulletin ${values.mois_deduction}/${values.annee_deduction}. ` +
                `Nouveau solde: ${response.data.nouveau_solde.toFixed(2)}j`,
                6
            );
            
            setDeductionModalVisible(false);
            fetchConges();
            if (selectedEmploye) fetchSynthese(selectedEmploye);
        } catch (error) {
            const errorMsg = error.response?.data?.detail || "Erreur lors de la création de la déduction";
            message.error(errorMsg, 8);
            console.error('Erreur:', error);
        }
    };

    const handleDeleteDeduction = async (deductionId) => {
        try {
            await api.delete(`/deductions-conges/${deductionId}`);
            message.success('Déduction supprimée, solde recalculé');
            fetchConges();
            if (detailsEmployeId) {
                fetchDeductions(detailsEmployeId);
                if (selectedEmploye === detailsEmployeId) {
                    fetchSynthese(selectedEmploye);
                }
            }
        } catch (error) {
            message.error(error.response?.data?.detail || 'Erreur lors de la suppression');
        }
    };

    const telechargerTitreConge = async (congeId) => {
        try {
            const response = await api.get(`/conges/${congeId}/titre-conge`, {
                responseType: 'blob'
            });
            
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `titre_conge_${congeId}.pdf`);
            document.body.appendChild(link);
            link.click();
            link.remove();
            window.URL.revokeObjectURL(url);
            
            message.success('Titre de congé téléchargé');
        } catch (error) {
            console.error('Erreur téléchargement titre:', error);
            message.error('Erreur lors du téléchargement du titre de congé');
        }
    };

    const columns = [
        {
            title: 'Employé',
            dataIndex: 'employe_nom',
            key: 'employe_nom',
            fixed: 'left',
            width: 200,
        },
        {
            title: 'Total Travaillés',
            dataIndex: 'total_travailles',
            key: 'total_travailles',
            width: 130,
            render: (val) => <span className="font-semibold">{val} j</span>
        },
        {
            title: 'Total Acquis',
            dataIndex: 'total_acquis',
            key: 'total_acquis',
            width: 120,
            render: (val) => <span className="font-semibold text-green-600">{val} j</span>
        },
        {
            title: 'Total Pris',
            dataIndex: 'total_pris',
            key: 'total_pris',
            width: 110,
            render: (val) => <span className="font-semibold text-orange-500">{val} j</span>
        },
        {
            title: 'Solde',
            dataIndex: 'solde',
            key: 'solde',
            width: 100,
            render: (val) => (
                <Tag color={val >= 0 ? 'green' : 'red'} className="font-bold">
                    {val} j
                </Tag>
            )
        },
        {
            title: 'Actions',
            key: 'actions',
            fixed: 'right',
            width: 200,
            render: (text, record) => (
                <Space>
                    <Button
                        type="link"
                        size="small"
                        icon={<EyeOutlined />}
                        onClick={() => handleShowDetails(record)}
                    >
                        Détails
                    </Button>
                    <Button
                        type="primary"
                        size="small"
                        icon={<PlusOutlined />}
                        onClick={() => handleOpenDeductionModal(record.employe_id, record.employe_nom)}
                    >
                        Déduire
                    </Button>
                </Space>
            )
        }
    ];

    const detailColumns = [
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
            title: 'Acquis',
            dataIndex: 'jours_conges_acquis',
            key: 'jours_conges_acquis',
            render: (val) => <span className="text-green-600">{Number(val).toFixed(2)} j</span>  // ⭐ v3.6.0 Phase 5
        },
        {
            title: 'Pris',
            dataIndex: 'jours_conges_pris',
            key: 'jours_conges_pris',
            render: (val) => <span className="text-orange-500">{Number(val).toFixed(2)} j</span>  // ⭐ v3.6.0
        },
        {
            title: 'Solde Cumulé',
            dataIndex: 'jours_conges_restants',
            key: 'jours_conges_restants',
            render: (val) => (
                <Tag color={val >= 0 ? 'green' : 'red'}>
                    {Number(val).toFixed(2)} j
                </Tag>
            )
        }
    ];

    const groupedData = groupCongesByEmploye();

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
                        <Col span={6}>
                            <Statistic 
                                title="Total Travaillés" 
                                value={groupedData[0]?.total_travailles || 0} 
                                suffix="jours" 
                            />
                        </Col>
                        <Col span={6}>
                            <Statistic 
                                title="Total Acquis" 
                                value={synthese.total_acquis} 
                                suffix="jours" 
                                valueStyle={{ color: '#3f8600' }} 
                            />
                        </Col>
                        <Col span={6}>
                            <Statistic 
                                title="Total Déduit" 
                                value={synthese.total_deduit} 
                                suffix="jours" 
                                valueStyle={{ color: '#cf1322' }} 
                            />
                        </Col>
                        <Col span={6}>
                            <Statistic 
                                title="Solde Global" 
                                value={synthese.solde} 
                                suffix="jours" 
                                valueStyle={{ color: synthese.solde >= 0 ? '#1890ff' : '#cf1322' }} 
                            />
                        </Col>
                    </Row>
                </Card>
            )}

            <Card>
                <Table
                    columns={columns}
                    dataSource={groupedData}
                    rowKey="employe_id"
                    loading={loading}
                    pagination={{ pageSize: 15 }}
                    scroll={{ x: 800 }}
                />
            </Card>

            {/* Modal Création Déduction v3.7.0 */}
            <Modal
                title="Créer une Déduction de Congé"
                open={deductionModalVisible}
                onOk={handleCreateDeduction}
                onCancel={() => setDeductionModalVisible(false)}
                okText="Créer"
                cancelText="Annuler"
                width={550}
            >
                <Alert
                    message="Nouvelle Architecture v3.7.0"
                    description="Cette déduction sera enregistrée séparément et impactera le bulletin du mois sélectionné."
                    type="info"
                    showIcon
                    style={{ marginBottom: 16 }}
                />

                <Form form={deductionForm} layout="vertical">
                    <Form.Item
                        name="jours_deduits"
                        label="Nombre de jours à déduire"
                        rules={[
                            { required: true, message: 'Requis' },
                            { type: 'number', min: 0.1, message: 'Minimum 0.1j' }
                        ]}
                    >
                        <InputNumber
                            style={{ width: '100%' }}
                            min={0.1}
                            max={30}
                            step={0.5}
                            precision={2}
                            placeholder="Ex: 2.5"
                        />
                    </Form.Item>

                    <Row gutter={16}>
                        <Col span={12}>
                            <Form.Item
                                name="mois_deduction"
                                label="Mois de déduction (bulletin)"
                                rules={[{ required: true, message: 'Requis' }]}
                            >
                                <Select placeholder="Sélectionnez le mois">
                                    <Option value={1}>Janvier</Option>
                                    <Option value={2}>Février</Option>
                                    <Option value={3}>Mars</Option>
                                    <Option value={4}>Avril</Option>
                                    <Option value={5}>Mai</Option>
                                    <Option value={6}>Juin</Option>
                                    <Option value={7}>Juillet</Option>
                                    <Option value={8}>Août</Option>
                                    <Option value={9}>Septembre</Option>
                                    <Option value={10}>Octobre</Option>
                                    <Option value={11}>Novembre</Option>
                                    <Option value={12}>Décembre</Option>
                                </Select>
                            </Form.Item>
                        </Col>
                        <Col span={12}>
                            <Form.Item
                                name="annee_deduction"
                                label="Année de déduction"
                                rules={[{ required: true, message: 'Requis' }]}
                            >
                                <InputNumber
                                    style={{ width: '100%' }}
                                    min={2020}
                                    max={2030}
                                    placeholder="2024"
                                />
                            </Form.Item>
                        </Col>
                    </Row>

                    <Form.Item
                        name="type_conge"
                        label="Type de congé"
                        initialValue="ANNUEL"
                    >
                        <Select>
                            <Option value="ANNUEL">Annuel</Option>
                            <Option value="MALADIE">Maladie</Option>
                            <Option value="EXCEPTIONNEL">Exceptionnel</Option>
                        </Select>
                    </Form.Item>

                    <Form.Item
                        name="motif"
                        label="Motif (optionnel)"
                    >
                        <Input.TextArea rows={2} placeholder="Ex: Vacances d'été" />
                    </Form.Item>
                </Form>
            </Modal>

            {/* Modal Détails Périodes avec Historique Déductions v3.7.0 */}
            <Modal
                title={`Détails des périodes - ${detailsEmploye}`}
                open={detailsModalVisible}
                onCancel={() => setDetailsModalVisible(false)}
                footer={[
                    <Button key="close" onClick={() => setDetailsModalVisible(false)}>
                        Fermer
                    </Button>
                ]}
                width={900}
            >
                <Descriptions bordered column={3} style={{ marginBottom: 16 }}>
                    <Descriptions.Item label="Total Acquis">
                        <Tag color="blue">{detailsPeriodes.reduce((sum, p) => sum + (p.jours_conges_acquis || 0), 0).toFixed(2)}j</Tag>
                    </Descriptions.Item>
                    <Descriptions.Item label="Solde Cumulé">
                        <Tag color={detailsPeriodes.length > 0 && detailsPeriodes[detailsPeriodes.length - 1].jours_conges_restants >= 0 ? 'green' : 'red'}>
                            {detailsPeriodes.length > 0 ? detailsPeriodes[detailsPeriodes.length - 1].jours_conges_restants.toFixed(2) : 0}j
                        </Tag>
                    </Descriptions.Item>
                    <Descriptions.Item label="Déductions">
                        <Tag color="orange">{deductions.length}</Tag>
                    </Descriptions.Item>
                </Descriptions>

                <h3 className="font-semibold mb-2">Périodes d'Acquisition</h3>
                <Table
                    columns={detailColumns}
                    dataSource={detailsPeriodes}
                    rowKey="id"
                    pagination={false}
                    size="small"
                    style={{ marginBottom: 24 }}
                />

                <Divider>Historique des Déductions</Divider>

                <Table
                    dataSource={deductions}
                    rowKey="id"
                    columns={[
                        {
                            title: 'Jours',
                            dataIndex: 'jours_deduits',
                            render: (val) => `${val}j`,
                            width: 80
                        },
                        {
                            title: 'Bulletin',
                            render: (_, record) => `${record.mois_deduction}/${record.annee_deduction}`,
                            width: 100
                        },
                        {
                            title: 'Type',
                            dataIndex: 'type_conge',
                            width: 100
                        },
                        {
                            title: 'Motif',
                            dataIndex: 'motif',
                            ellipsis: true
                        },
                        {
                            title: 'Créé le',
                            dataIndex: 'created_at',
                            render: (val) => new Date(val).toLocaleDateString('fr-FR'),
                            width: 110
                        },
                        {
                            title: 'Actions',
                            render: (_, record) => (
                                <Popconfirm
                                    title="Supprimer cette déduction?"
                                    description="Le solde sera recalculé automatiquement."
                                    onConfirm={() => handleDeleteDeduction(record.id)}
                                    okText="Oui"
                                    cancelText="Non"
                                >
                                    <Button danger size="small" icon={<DeleteOutlined />}>
                                        Supprimer
                                    </Button>
                                </Popconfirm>
                            ),
                            width: 120
                        }
                    ]}
                    pagination={false}
                    size="small"
                    locale={{ emptyText: 'Aucune déduction enregistrée' }}
                />
            </Modal>
        </div>
    );
};

export default CongesList;

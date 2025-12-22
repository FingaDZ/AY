import React, { useState, useEffect } from 'react';
import { Table, Card, Button, Tag, Modal, Form, InputNumber, message, Select, Statistic, Row, Col, Space } from 'antd';
import { EditOutlined, CalendarOutlined, DownloadOutlined, EyeOutlined } from '@ant-design/icons';
import api from '../../services/api';

const { Option } = Select;

const CongesList = () => {
    const [conges, setConges] = useState([]);
    const [loading, setLoading] = useState(false);
    const [employes, setEmployes] = useState([]);

    // Filtres
    const [selectedEmploye, setSelectedEmploye] = useState(null);
    const [selectedAnnee, setSelectedAnnee] = useState(new Date().getFullYear());

    // Modal Saisie
    const [isModalVisible, setIsModalVisible] = useState(false);
    const [currentConge, setCurrentConge] = useState(null);
    const [form] = Form.useForm();

    // Modal Détails Périodes
    const [detailsModalVisible, setDetailsModalVisible] = useState(false);
    const [detailsEmploye, setDetailsEmploye] = useState(null);
    const [detailsPeriodes, setDetailsPeriodes] = useState([]);

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
            setSynthese(response.data);
        } catch (error) {
            console.error("Erreur synthèse", error);
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

    const handleEdit = (periode) => {
        // Ouvrir la modal de saisie pour cette période spécifique
        setCurrentConge(periode);
        form.setFieldsValue({
            jours_pris: periode.jours_conges_pris,
            mois_deduction: periode.mois_deduction || periode.mois,
            annee_deduction: periode.annee_deduction || periode.annee
        });
        setIsModalVisible(true);
    };

    const handleShowDetails = (employe) => {
        setDetailsEmploye(employe.employe_nom);
        setDetailsPeriodes(employe.periodes);
        setDetailsModalVisible(true);
    };

    const handleSave = async () => {
        try {
            const values = await form.validateFields();
            const response = await api.put(`/conges/${currentConge.id}/consommation`, {
                jours_pris: values.jours_pris,
                mois_deduction: values.mois_deduction,
                annee_deduction: values.annee_deduction
            });
            
            // Afficher message avec détails de répartition
            const ancienTotal = response.data.ancien_total || 0;
            const nouveauTotal = response.data.nouveau_total || 0;
            const difference = response.data.difference || 0;
            
            if (response.data.repartition && response.data.repartition.length > 0) {
                const details = response.data.details.join('\n');
                const diffText = difference >= 0 ? `+${difference.toFixed(2)}j` : `${difference.toFixed(2)}j`;
                message.success(
                    <div>
                        <strong>✅ Répartition automatique effectuée!</strong>
                        <div style={{fontSize: '12px', marginTop: '8px', marginBottom: '8px'}}>
                            Ancien total: {ancienTotal.toFixed(2)}j → Nouveau total: {nouveauTotal.toFixed(2)}j ({diffText})
                        </div>
                        <pre style={{fontSize: '11px', whiteSpace: 'pre-wrap', backgroundColor: '#f0f0f0', padding: '8px', borderRadius: '4px'}}>
                            {details}
                        </pre>
                    </div>,
                    10
                );
            } else {
                message.success(`Consommation mise à jour: ${nouveauTotal.toFixed(2)}j`);
            }
            
            setIsModalVisible(false);
            fetchConges();
            if (selectedEmploye) fetchSynthese(selectedEmploye);
        } catch (error) {
            const errorMsg = error.response?.data?.detail || "Erreur lors de la mise à jour";
            message.error(errorMsg, 8);
            console.error('Erreur:', error);
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
                        icon={<EditOutlined />}
                        onClick={() => {
                            // Ouvrir modal pour la dernière période de cet employé
                            const lastPeriode = record.periodes[record.periodes.length - 1];
                            handleEdit(lastPeriode);
                        }}
                    >
                        Éditer
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
            title: 'Solde',
            dataIndex: 'jours_conges_restants',
            key: 'jours_conges_restants',
            render: (val) => (
                <Tag color={val >= 0 ? 'green' : 'red'}>
                    {Number(val).toFixed(2)} j
                </Tag>
            )
        },
        {
            title: 'Actions',
            key: 'actions',
            width: 100,
            render: (text, record) => (
                <Button
                    type="primary"
                    size="small"
                    onClick={() => handleEdit(record)}
                >
                    Saisie
                </Button>
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
                                title="Total Pris" 
                                value={synthese.total_pris} 
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

            {/* Modal Saisie Congés */}
            <Modal
                title="Saisie Consommation Congé"
                open={isModalVisible}
                onOk={handleSave}
                onCancel={() => setIsModalVisible(false)}
                width={650}
            >
                <Form form={form} layout="vertical">
                    <div className="mb-4 p-3 bg-blue-50 rounded border border-blue-200">
                        <p className="text-sm font-semibold text-blue-700 mb-2">
                            ⚠️ MODE: TOTAL GLOBAL (pas un ajout!)
                        </p>
                        <p className="text-xs text-blue-600 mb-2">
                            Saisissez le <strong>nombre TOTAL de jours</strong> que l'employé doit avoir pris au total.
                            Cette valeur <strong>remplace toutes les saisies précédentes</strong>.
                        </p>
                        <p className="text-xs text-blue-600">
                            Le système répartira automatiquement sur les périodes disponibles 
                            (du plus ancien au plus récent). Exemple: 5j total = 2.5j (oct) + 2.42j (nov) + 0.08j (déc).
                        </p>
                    </div>
                    
                    <p className="mb-4 text-gray-500">
                        Période sélectionnée: <strong>{currentConge?.mois}/{currentConge?.annee}</strong>
                    </p>
                    <Form.Item
                        name="jours_pris"
                        label="TOTAL de jours à prendre (remplace les saisies précédentes)"
                        rules={[{ required: true, message: 'Veuillez saisir le total global' }]}
                        extra="Saisissez le total cumulé que l'employé doit avoir pris, pas un ajout"
                    >
                        <InputNumber min={0} max={100} step={0.5} style={{ width: '100%' }} placeholder="Ex: 5.0 (total global)" />
                    </Form.Item>
                    
                    <div className="mb-4 p-3 bg-blue-50 rounded border border-blue-200">
                        <p className="text-sm font-semibold text-blue-700 mb-2">📅 Affectation sur le bulletin de paie</p>
                        <p className="text-xs text-blue-600 mb-3">
                            Par défaut, les jours seront déduits du bulletin du mois d'acquisition. 
                            Vous pouvez choisir un autre mois si nécessaire.
                        </p>
                        
                        <Row gutter={16}>
                            <Col span={12}>
                                <Form.Item
                                    name="mois_deduction"
                                    label="Mois de déduction"
                                    rules={[{ required: true, message: 'Requis' }]}
                                >
                                    <Select placeholder="Sélectionnez un mois">
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
                                        min={2020} 
                                        max={2100} 
                                        style={{ width: '100%' }} 
                                        placeholder="2025"
                                    />
                                </Form.Item>
                            </Col>
                        </Row>
                    </div>
                </Form>
            </Modal>

            {/* Modal Détails Périodes */}
            <Modal
                title={`Détails des périodes - ${detailsEmploye}`}
                open={detailsModalVisible}
                onCancel={() => setDetailsModalVisible(false)}
                footer={[
                    <Button key="close" onClick={() => setDetailsModalVisible(false)}>
                        Fermer
                    </Button>
                ]}
                width={700}
            >
                <Table
                    columns={detailColumns}
                    dataSource={detailsPeriodes}
                    rowKey="id"
                    pagination={false}
                    size="small"
                />
            </Modal>
        </div>
    );
};

export default CongesList;

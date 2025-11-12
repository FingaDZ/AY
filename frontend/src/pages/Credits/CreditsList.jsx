import { useState, useEffect } from 'react';
import { Table, Button, message, Modal, Form, InputNumber, DatePicker, Select, Tag, Card, Row, Col, Drawer, Popconfirm, Space } from 'antd';
import { PlusOutlined, EyeOutlined, ClearOutlined, EditOutlined, DeleteOutlined, PrinterOutlined } from '@ant-design/icons';
import { creditService, employeService } from '../../services';
import dayjs from 'dayjs';

const { Option } = Select;

function CreditsList() {
  const [loading, setLoading] = useState(false);
  const [credits, setCredits] = useState([]);
  const [employes, setEmployes] = useState([]);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingCredit, setEditingCredit] = useState(null);
  const [detailDrawerVisible, setDetailDrawerVisible] = useState(false);
  const [selectedCredit, setSelectedCredit] = useState(null);
  const [echeancier, setEcheancier] = useState([]);
  const [form] = Form.useForm();
  
  // Filtres
  const [filters, setFilters] = useState({
    employe_id: null,
    statut: null,
  });

  useEffect(() => {
    loadData();
  }, [filters]);

  const loadData = async () => {
    try {
      setLoading(true);
      
      const params = {};
      if (filters.employe_id) params.employe_id = filters.employe_id;
      if (filters.statut) params.statut = filters.statut;
      
      const [creditsRes, employesRes] = await Promise.all([
        creditService.getAll(params),
        employeService.getAll({ statut: 'Actif' }),
      ]);
      setCredits(creditsRes.data.credits || []);
      setEmployes(employesRes.data.employes || []);
    } catch (error) {
      message.error('Erreur lors du chargement');
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const handleClearFilters = () => {
    setFilters({
      employe_id: null,
      statut: null,
    });
  };

  const handleViewDetails = async (credit) => {
    try {
      setSelectedCredit(credit);
      const response = await creditService.getEcheancier(credit.id);
      setEcheancier(response.data);
      setDetailDrawerVisible(true);
    } catch (error) {
      message.error('Erreur lors du chargement de l\'échéancier');
    }
  };

  const handleEdit = (record) => {
    setEditingCredit(record);
    form.setFieldsValue({
      employe_id: record.employe_id,
      date_octroi: dayjs(record.date_octroi),
      montant_total: parseFloat(record.montant_total),
      nombre_mensualites: record.nombre_mensualites,
    });
    setModalVisible(true);
  };

  const handleDelete = async (id) => {
    try {
      await creditService.delete(id);
      message.success('Crédit supprimé avec succès');
      loadData();
    } catch (error) {
      const errorMsg = error.response?.data?.detail || 'Erreur lors de la suppression';
      message.error(errorMsg);
    }
  };

  const handleSubmit = async (values) => {
    try {
      const data = {
        ...values,
        date_octroi: values.date_octroi.format('YYYY-MM-DD'),
      };

      if (editingCredit) {
        // Pour la modification, on n'envoie que le nombre de mensualités
        await creditService.update(editingCredit.id, { nombre_mensualites: data.nombre_mensualites });
        message.success('Crédit modifié avec succès');
      } else {
        await creditService.create(data);
        message.success('Crédit créé avec succès');
      }

      setModalVisible(false);
      setEditingCredit(null);
      form.resetFields();
      loadData();
    } catch (error) {
      const errorMsg = error.response?.data?.detail || 'Erreur lors de l\'opération';
      message.error(errorMsg);
    }
  };

  const handleCancel = () => {
    setModalVisible(false);
    setEditingCredit(null);
    form.resetFields();
  };

  const handlePrintPdf = async () => {
    try {
      const params = {};
      if (filters.employe_id) params.employe_id = filters.employe_id;
      if (filters.statut) params.statut = filters.statut;

      const response = await creditService.getPdf(params);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `credits_${new Date().toISOString().split('T')[0]}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      message.success('PDF généré avec succès');
    } catch (error) {
      message.error('Erreur lors de la génération du PDF');
    }
  };

  const columns = [
    { title: 'Date', dataIndex: 'date_octroi', key: 'date_octroi' },
    { 
      title: 'Employé', 
      dataIndex: 'employe_id', 
      key: 'employe_id',
      render: (id) => {
        const emp = employes.find(e => e.id === id);
        return emp ? `${emp.prenom} ${emp.nom}` : id;
      }
    },
    { 
      title: 'Montant Total', 
      dataIndex: 'montant_total', 
      key: 'montant_total',
      render: (val) => `${parseFloat(val).toLocaleString('fr-FR')} DA`
    },
    { title: 'Mensualités', dataIndex: 'nombre_mensualites', key: 'nombre_mensualites' },
    { 
      title: 'Mensualité', 
      dataIndex: 'montant_mensualite', 
      key: 'montant_mensualite',
      render: (val) => `${parseFloat(val).toLocaleString('fr-FR')} DA`
    },
    { 
      title: 'Retenu', 
      dataIndex: 'montant_retenu', 
      key: 'montant_retenu',
      render: (val) => `${parseFloat(val).toLocaleString('fr-FR')} DA`
    },
    { 
      title: 'Restant', 
      key: 'montant_restant',
      render: (_, record) => {
        const restant = parseFloat(record.montant_total) - parseFloat(record.montant_retenu);
        return `${restant.toLocaleString('fr-FR')} DA`;
      }
    },
    { 
      title: 'Statut', 
      dataIndex: 'statut', 
      key: 'statut',
      render: (val) => (
        <Tag color={val === 'En cours' ? 'blue' : 'green'}>{val}</Tag>
      )
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <div style={{ display: 'flex', gap: '8px' }}>
          <Button 
            type="link" 
            icon={<EyeOutlined />}
            onClick={() => handleViewDetails(record)}
          >
            Détails
          </Button>
          <Button 
            type="link" 
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
            disabled={record.statut === 'Soldé'}
          >
            Modifier
          </Button>
          <Popconfirm
            title="Supprimer ce crédit ?"
            description="Cette action est irréversible. Toutes les retenues associées seront supprimées."
            onConfirm={() => handleDelete(record.id)}
            okText="Oui"
            cancelText="Non"
          >
            <Button 
              type="link" 
              danger
              icon={<DeleteOutlined />}
            >
              Supprimer
            </Button>
          </Popconfirm>
        </div>
      )
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <h2>Crédits</h2>
        <Space>
          <Button icon={<PrinterOutlined />} onClick={handlePrintPdf}>
            Imprimer PDF
          </Button>
          <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalVisible(true)}>
            Nouveau Crédit
          </Button>
        </Space>
      </div>

      {/* Filtres */}
      <Card style={{ marginBottom: 16 }}>
        <Row gutter={16}>
          <Col span={8}>
            <Select
              placeholder="Filtrer par employé"
              style={{ width: '100%' }}
              allowClear
              value={filters.employe_id}
              onChange={(value) => handleFilterChange('employe_id', value)}
            >
              {employes.map(emp => (
                <Option key={emp.id} value={emp.id}>{emp.prenom} {emp.nom}</Option>
              ))}
            </Select>
          </Col>
          <Col span={8}>
            <Select
              placeholder="Filtrer par statut"
              style={{ width: '100%' }}
              allowClear
              value={filters.statut}
              onChange={(value) => handleFilterChange('statut', value)}
            >
              <Option value="En cours">En cours</Option>
              <Option value="Soldé">Soldé</Option>
            </Select>
          </Col>
          <Col span={8}>
            <Button 
              icon={<ClearOutlined />} 
              onClick={handleClearFilters}
              style={{ width: '100%' }}
            >
              Réinitialiser les filtres
            </Button>
          </Col>
        </Row>
      </Card>

      <Table loading={loading} columns={columns} dataSource={credits} rowKey="id" />

      {/* Modal Création/Modification */}
      <Modal 
        title={editingCredit ? "Modifier le Crédit" : "Nouveau Crédit"} 
        open={modalVisible} 
        onCancel={handleCancel} 
        footer={null}
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Form.Item label="Employé" name="employe_id" rules={[{ required: true }]}>
            <Select disabled={!!editingCredit}>
              {employes.map(emp => (
                <Option key={emp.id} value={emp.id}>{emp.prenom} {emp.nom}</Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item 
            label="Date de début de remboursement (Mois/Année)" 
            name="date_octroi" 
            rules={[{ required: true, message: 'Veuillez sélectionner le mois de début' }]}
          >
            <DatePicker 
              picker="month" 
              style={{ width: '100%' }} 
              format="MMMM YYYY"
              placeholder="Sélectionner le mois"
              disabled={!!editingCredit}
            />
          </Form.Item>
          <Form.Item label="Montant total (DA)" name="montant_total" rules={[{ required: true }]}>
            <InputNumber style={{ width: '100%' }} min={0} disabled={!!editingCredit} />
          </Form.Item>
          <Form.Item 
            label="Nombre de mensualités" 
            name="nombre_mensualites" 
            rules={[{ required: true }]}
            help={editingCredit ? "Vous pouvez modifier le nombre de mensualités restantes" : ""}
          >
            <InputNumber style={{ width: '100%' }} min={1} />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit">
              {editingCredit ? "Modifier" : "Créer"}
            </Button>
          </Form.Item>
        </Form>
      </Modal>

      {/* Drawer Détails */}
      <Drawer
        title={`Détails du Crédit #${selectedCredit?.id || ''}`}
        placement="right"
        width={720}
        onClose={() => setDetailDrawerVisible(false)}
        open={detailDrawerVisible}
      >
        {selectedCredit && (
          <div>
            <Card title="Informations Générales" style={{ marginBottom: 16 }}>
              <p><strong>Employé:</strong> {employes.find(e => e.id === selectedCredit.employe_id)?.prenom} {employes.find(e => e.id === selectedCredit.employe_id)?.nom}</p>
              <p><strong>Date d'octroi:</strong> {selectedCredit.date_octroi}</p>
              <p><strong>Montant total:</strong> {parseFloat(selectedCredit.montant_total).toLocaleString('fr-FR')} DA</p>
              <p><strong>Nombre de mensualités:</strong> {selectedCredit.nombre_mensualites}</p>
              <p><strong>Montant mensualité:</strong> {parseFloat(selectedCredit.montant_mensualite).toLocaleString('fr-FR')} DA</p>
              <p><strong>Montant retenu:</strong> {parseFloat(selectedCredit.montant_retenu).toLocaleString('fr-FR')} DA</p>
              <p style={{ fontSize: '16px', fontWeight: 'bold', color: '#1890ff' }}>
                <strong>Montant restant:</strong> {(parseFloat(selectedCredit.montant_total) - parseFloat(selectedCredit.montant_retenu)).toLocaleString('fr-FR')} DA
              </p>
              <p><strong>Statut:</strong> <Tag color={selectedCredit.statut === 'En cours' ? 'blue' : 'green'}>{selectedCredit.statut}</Tag></p>
            </Card>

            <Card title="Échéancier de Paiement">
              <Table
                dataSource={echeancier}
                rowKey={(record) => `${record.annee}-${record.mois}`}
                pagination={false}
                columns={[
                  {
                    title: 'Période',
                    key: 'periode',
                    render: (_, record) => {
                      const moisNom = new Date(2000, record.mois - 1).toLocaleDateString('fr-FR', { month: 'long' });
                      return `${moisNom.charAt(0).toUpperCase() + moisNom.slice(1)} ${record.annee}`;
                    }
                  },
                  {
                    title: 'Mensualité',
                    dataIndex: 'montant',
                    render: (val) => `${parseFloat(val).toLocaleString('fr-FR')} DA`
                  },
                  {
                    title: 'Statut',
                    dataIndex: 'statut',
                    render: (statut, record) => {
                      if (record.prorogation) {
                        return <Tag color="orange">Prorogé</Tag>;
                      }
                      return statut === 'payé' ? 
                        <Tag color="success">Payé</Tag> : 
                        <Tag color="default">Non payé</Tag>;
                    }
                  },
                  {
                    title: 'Remarque',
                    dataIndex: 'prorogation',
                    render: (prorogation) => prorogation ? `Reporté au ${prorogation.mois_reporte}/${prorogation.annee_reportee}` : '-'
                  }
                ]}
              />
            </Card>
          </div>
        )}
      </Drawer>
    </div>
  );
}

export default CreditsList;

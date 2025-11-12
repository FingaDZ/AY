// Pages simplifiées pour Avances
import { useState, useEffect } from 'react';
import { Table, Button, message, Modal, Form, InputNumber, DatePicker, Select, Input, Space, Popconfirm, Card, Row, Col } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, SearchOutlined, ClearOutlined, FilePdfOutlined } from '@ant-design/icons';
import { avanceService, employeService } from '../../services';
import dayjs from 'dayjs';

const { Option } = Select;
const { RangePicker } = DatePicker;

function AvancesList() {
  const [loading, setLoading] = useState(false);
  const [avances, setAvances] = useState([]);
  const [employes, setEmployes] = useState([]);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingAvance, setEditingAvance] = useState(null);
  const [filters, setFilters] = useState({
    employe_id: null,
    annee: null,
    mois: null,
  });
  const [form] = Form.useForm();

  useEffect(() => {
    loadData();
  }, [filters]);

  const loadData = async () => {
    try {
      setLoading(true);
      const params = {};
      if (filters.employe_id) params.employe_id = filters.employe_id;
      if (filters.annee) params.annee = filters.annee;
      if (filters.mois) params.mois = filters.mois;

      const [avancesRes, employesRes] = await Promise.all([
        avanceService.getAll(params),
        employeService.getAll({ statut: 'Actif' }),
      ]);
      setAvances(avancesRes.data.avances || []);
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
      annee: null,
      mois: null,
    });
  };

  const handleSubmit = async (values) => {
    try {
      const data = {
        ...values,
        date_avance: values.date_avance.format('YYYY-MM-DD'),
      };

      if (editingAvance) {
        await avanceService.update(editingAvance.id, data);
        message.success('Avance modifiée avec succès');
      } else {
        await avanceService.create(data);
        message.success('Avance créée avec succès');
      }

      setModalVisible(false);
      setEditingAvance(null);
      form.resetFields();
      loadData();
    } catch (error) {
      const errorMsg = error.response?.data?.detail || 'Erreur lors de l\'opération';
      message.error(errorMsg);
    }
  };

  const handleEdit = (record) => {
    setEditingAvance(record);
    form.setFieldsValue({
      employe_id: record.employe_id,
      date_avance: dayjs(record.date_avance),
      montant: parseFloat(record.montant),
      mois_deduction: record.mois_deduction,
      annee_deduction: record.annee_deduction,
      motif: record.motif,
    });
    setModalVisible(true);
  };

  const handleDelete = async (id) => {
    try {
      await avanceService.delete(id);
      message.success('Avance supprimée avec succès');
      loadData();
    } catch (error) {
      message.error('Erreur lors de la suppression');
    }
  };

  const handleGenererRapport = async () => {
    try {
      setLoading(true);
      const annee = filters.annee || new Date().getFullYear();
      const mois = filters.mois || new Date().getMonth() + 1;
      
      const response = await avanceService.getRapportMensuel(annee, mois);
      
      // Télécharger le PDF
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      const moisStr = String(mois).padStart(2, '0');
      link.setAttribute('download', `avances_${moisStr}_${annee}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      message.success('Rapport généré avec succès');
    } catch (error) {
      message.error(error.response?.data?.detail || 'Erreur lors de la génération du rapport');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    setModalVisible(false);
    setEditingAvance(null);
    form.resetFields();
  };

  const columns = [
    { title: 'Date', dataIndex: 'date_avance', key: 'date_avance' },
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
      title: 'Montant', 
      dataIndex: 'montant', 
      key: 'montant',
      render: (val) => `${parseFloat(val).toLocaleString('fr-FR')} DA`
    },
    { 
      title: 'Déduction', 
      key: 'deduction',
      render: (_, record) => `${record.mois_deduction}/${record.annee_deduction}`
    },
    { title: 'Motif', dataIndex: 'motif', key: 'motif' },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            Modifier
          </Button>
          <Popconfirm
            title="Supprimer cette avance ?"
            description="Cette action est irréversible."
            onConfirm={() => handleDelete(record.id)}
            okText="Oui"
            cancelText="Non"
          >
            <Button type="link" danger icon={<DeleteOutlined />}>
              Supprimer
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <h2>Avances Salariales</h2>
        <Space>
          <Button 
            type="default" 
            icon={<FilePdfOutlined />} 
            onClick={handleGenererRapport}
            loading={loading}
          >
            Rapport PDF
          </Button>
          <Button 
            type="primary" 
            icon={<PlusOutlined />} 
            onClick={() => { setEditingAvance(null); setModalVisible(true); }}
          >
            Nouvelle Avance
          </Button>
        </Space>
      </div>

      {/* Filtres */}
      <Card style={{ marginBottom: 16 }}>
        <Row gutter={16}>
          <Col span={6}>
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
          <Col span={6}>
            <InputNumber
              placeholder="Année de déduction"
              style={{ width: '100%' }}
              min={2000}
              max={2100}
              value={filters.annee}
              onChange={(value) => handleFilterChange('annee', value)}
            />
          </Col>
          <Col span={6}>
            <Select
              placeholder="Mois de déduction"
              style={{ width: '100%' }}
              allowClear
              value={filters.mois}
              onChange={(value) => handleFilterChange('mois', value)}
            >
              {[...Array(12)].map((_, i) => (
                <Option key={i+1} value={i+1}>
                  {new Date(2000, i).toLocaleDateString('fr-FR', { month: 'long' })}
                </Option>
              ))}
            </Select>
          </Col>
          <Col span={6}>
            <Button icon={<ClearOutlined />} onClick={handleClearFilters}>
              Réinitialiser
            </Button>
          </Col>
        </Row>
      </Card>

      <Table loading={loading} columns={columns} dataSource={avances} rowKey="id" />

      <Modal 
        title={editingAvance ? "Modifier l'Avance" : "Nouvelle Avance"} 
        open={modalVisible} 
        onCancel={handleCancel} 
        footer={null}
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Form.Item label="Employé" name="employe_id" rules={[{ required: true }]}>
            <Select>
              {employes.map(emp => (
                <Option key={emp.id} value={emp.id}>{emp.prenom} {emp.nom}</Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item label="Date" name="date_avance" rules={[{ required: true }]}>
            <DatePicker style={{ width: '100%' }} format="DD/MM/YYYY" />
          </Form.Item>
          <Form.Item label="Montant (DA)" name="montant" rules={[{ required: true }]}>
            <InputNumber style={{ width: '100%' }} min={0} />
          </Form.Item>
          <Form.Item label="Mois déduction" name="mois_deduction" rules={[{ required: true }]}>
            <Select>
              {[...Array(12)].map((_, i) => <Option key={i+1} value={i+1}>{i+1}</Option>)}
            </Select>
          </Form.Item>
          <Form.Item label="Année déduction" name="annee_deduction" rules={[{ required: true }]}>
            <InputNumber style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item label="Motif" name="motif">
            <Input.TextArea />
          </Form.Item>
          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                {editingAvance ? 'Modifier' : 'Créer'}
              </Button>
              <Button onClick={handleCancel}>Annuler</Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}

export default AvancesList;

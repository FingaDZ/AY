// Pages simplifiées pour Avances
import { useState, useEffect } from 'react';
import { Table, Button, message, Modal, Form, InputNumber, DatePicker, Select, Input } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { avanceService, employeService } from '../../services';
import dayjs from 'dayjs';

const { Option } = Select;

function AvancesList() {
  const [loading, setLoading] = useState(false);
  const [avances, setAvances] = useState([]);
  const [employes, setEmployes] = useState([]);
  const [modalVisible, setModalVisible] = useState(false);
  const [form] = Form.useForm();

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [avancesRes, employesRes] = await Promise.all([
        avanceService.getAll(),
        employeService.getAll({ statut: 'Actif' }),
      ]);
      setAvances(avancesRes.data);
      setEmployes(employesRes.data.employes || []);
    } catch (error) {
      message.error('Erreur lors du chargement');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (values) => {
    try {
      await avanceService.create({
        ...values,
        date_avance: values.date_avance.format('YYYY-MM-DD'),
      });
      message.success('Avance créée avec succès');
      setModalVisible(false);
      form.resetFields();
      loadData();
    } catch (error) {
      message.error('Erreur lors de la création');
    }
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
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <h2>Avances Salariales</h2>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalVisible(true)}>
          Nouvelle Avance
        </Button>
      </div>

      <Table loading={loading} columns={columns} dataSource={avances} rowKey="id" />

      <Modal title="Nouvelle Avance" open={modalVisible} onCancel={() => setModalVisible(false)} footer={null}>
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Form.Item label="Employé" name="employe_id" rules={[{ required: true }]}>
            <Select>
              {employes.map(emp => (
                <Option key={emp.id} value={emp.id}>{emp.prenom} {emp.nom}</Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item label="Date" name="date_avance" rules={[{ required: true }]}>
            <DatePicker style={{ width: '100%' }} />
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
            <Button type="primary" htmlType="submit">Créer</Button>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}

export default AvancesList;

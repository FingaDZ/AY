import { useState, useEffect } from 'react';
import { Table, Button, message, Modal, Form, InputNumber, DatePicker, Select, Tag } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { creditService, employeService } from '../../services';
import dayjs from 'dayjs';

const { Option } = Select;

function CreditsList() {
  const [loading, setLoading] = useState(false);
  const [credits, setCredits] = useState([]);
  const [employes, setEmployes] = useState([]);
  const [modalVisible, setModalVisible] = useState(false);
  const [form] = Form.useForm();

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [creditsRes, employesRes] = await Promise.all([
        creditService.getAll(),
        employeService.getAll({ statut: 'Actif' }),
      ]);
      setCredits(creditsRes.data);
      setEmployes(employesRes.data.employes || []);
    } catch (error) {
      message.error('Erreur lors du chargement');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (values) => {
    try {
      await creditService.create({
        ...values,
        date_octroi: values.date_octroi.format('YYYY-MM-DD'),
      });
      message.success('Crédit créé avec succès');
      setModalVisible(false);
      form.resetFields();
      loadData();
    } catch (error) {
      message.error('Erreur lors de la création');
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
      title: 'Statut', 
      dataIndex: 'statut', 
      key: 'statut',
      render: (val) => (
        <Tag color={val === 'En cours' ? 'blue' : 'green'}>{val}</Tag>
      )
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <h2>Crédits</h2>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalVisible(true)}>
          Nouveau Crédit
        </Button>
      </div>

      <Table loading={loading} columns={columns} dataSource={credits} rowKey="id" />

      <Modal title="Nouveau Crédit" open={modalVisible} onCancel={() => setModalVisible(false)} footer={null}>
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Form.Item label="Employé" name="employe_id" rules={[{ required: true }]}>
            <Select>
              {employes.map(emp => (
                <Option key={emp.id} value={emp.id}>{emp.prenom} {emp.nom}</Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item label="Date d'octroi" name="date_octroi" rules={[{ required: true }]}>
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item label="Montant total (DA)" name="montant_total" rules={[{ required: true }]}>
            <InputNumber style={{ width: '100%' }} min={0} />
          </Form.Item>
          <Form.Item label="Nombre de mensualités" name="nombre_mensualites" rules={[{ required: true }]}>
            <InputNumber style={{ width: '100%' }} min={1} />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit">Créer</Button>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}

export default CreditsList;

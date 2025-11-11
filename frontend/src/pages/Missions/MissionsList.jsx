import { useState, useEffect } from 'react';
import { Table, Button, DatePicker, Select, message, Modal, Form, InputNumber } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { missionService, employeService, clientService } from '../../services';
import dayjs from 'dayjs';

const { Option } = Select;

function MissionsList() {
  const [loading, setLoading] = useState(false);
  const [missions, setMissions] = useState([]);
  const [employes, setEmployes] = useState([]);
  const [clients, setClients] = useState([]);
  const [modalVisible, setModalVisible] = useState(false);
  const [tarifKm, setTarifKm] = useState(15.5);
  const [form] = Form.useForm();

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [missionsRes, employesRes, clientsRes, tarifRes] = await Promise.all([
        missionService.getAll(),
        employeService.getAll({ statut: 'Actif' }),
        clientService.getAll(),
        missionService.getTarifKm(),
      ]);
      
      setMissions(missionsRes.data);
      setEmployes(employesRes.data.employes || []);
      setClients(clientsRes.data);
      setTarifKm(tarifRes.data.valeur);
    } catch (error) {
      message.error('Erreur lors du chargement');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (values) => {
    try {
      await missionService.create({
        ...values,
        date_mission: values.date_mission.format('YYYY-MM-DD'),
      });
      message.success('Mission créée avec succès');
      setModalVisible(false);
      form.resetFields();
      loadData();
    } catch (error) {
      message.error('Erreur lors de la création');
    }
  };

  const columns = [
    { title: 'Date', dataIndex: 'date_mission', key: 'date_mission' },
    { 
      title: 'Chauffeur', 
      dataIndex: 'chauffeur_id', 
      key: 'chauffeur_id',
      render: (id) => {
        const emp = employes.find(e => e.id === id);
        return emp ? `${emp.prenom} ${emp.nom}` : id;
      }
    },
    { 
      title: 'Client', 
      dataIndex: 'client_id', 
      key: 'client_id',
      render: (id) => {
        const cli = clients.find(c => c.id === id);
        return cli ? `${cli.prenom} ${cli.nom}` : id;
      }
    },
    { 
      title: 'Distance (km)', 
      dataIndex: 'distance', 
      key: 'distance',
      render: (val) => `${parseFloat(val).toFixed(2)} km`
    },
    { 
      title: 'Tarif/km', 
      dataIndex: 'tarif_km', 
      key: 'tarif_km',
      render: (val) => `${parseFloat(val).toFixed(2)} DA`
    },
    { 
      title: 'Prime', 
      dataIndex: 'prime_calculee', 
      key: 'prime_calculee',
      render: (val) => `${parseFloat(val).toLocaleString('fr-FR')} DA`
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <h2>Ordres de Mission</h2>
        <div>
          <span style={{ marginRight: 16 }}>Tarif/km: {tarifKm} DA</span>
          <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalVisible(true)}>
            Nouvelle Mission
          </Button>
        </div>
      </div>

      <Table
        loading={loading}
        columns={columns}
        dataSource={missions}
        rowKey="id"
        pagination={{ pageSize: 10 }}
      />

      <Modal
        title="Nouvelle Mission"
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Form.Item
            label="Date"
            name="date_mission"
            rules={[{ required: true }]}
          >
            <DatePicker style={{ width: '100%' }} format="DD/MM/YYYY" />
          </Form.Item>

          <Form.Item
            label="Chauffeur"
            name="chauffeur_id"
            rules={[{ required: true }]}
          >
            <Select>
              {employes.filter(e => e.poste_travail.toLowerCase().includes('chauffeur')).map(emp => (
                <Option key={emp.id} value={emp.id}>
                  {emp.prenom} {emp.nom}
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            label="Client"
            name="client_id"
            rules={[{ required: true }]}
          >
            <Select>
              {clients.map(cli => (
                <Option key={cli.id} value={cli.id}>
                  {cli.prenom} {cli.nom} ({cli.distance} km)
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit">Créer</Button>
            <Button onClick={() => setModalVisible(false)} style={{ marginLeft: 8 }}>Annuler</Button>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}

export default MissionsList;

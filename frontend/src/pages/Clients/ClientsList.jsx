import { useState, useEffect } from 'react';
import { Table, Button, Space, Input, message, Modal, Form, InputNumber, Popconfirm, Tag } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, FilePdfOutlined, InfoCircleOutlined } from '@ant-design/icons';
import { clientService } from '../../services';
import api from '../../services/api';

function ClientsList() {
  const [loading, setLoading] = useState(false);
  const [clients, setClients] = useState([]);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingClient, setEditingClient] = useState(null);
  const [form] = Form.useForm();
  const [logisticsModalVisible, setLogisticsModalVisible] = useState(false);
  const [logisticsData, setLogisticsData] = useState(null);
  const [loadingLogistics, setLoadingLogistics] = useState(false);

  useEffect(() => {
    loadClients();
  }, []);

  const loadClients = async () => {
    try {
      setLoading(true);
      const response = await clientService.getAll();
      console.log('Clients response:', response.data);
      // Le backend peut retourner {clients: []} ou directement []
      const clientsData = response.data.clients || response.data || [];
      setClients(Array.isArray(clientsData) ? clientsData : []);
    } catch (error) {
      message.error('Erreur lors du chargement des clients');
      console.error('Error loading clients:', error);
      setClients([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (values) => {
    try {
      if (editingClient) {
        await clientService.update(editingClient.id, values);
        message.success('Client modifié avec succès');
      } else {
        await clientService.create(values);
        message.success('Client créé avec succès');
      }
      setModalVisible(false);
      form.resetFields();
      setEditingClient(null);
      loadClients();
    } catch (error) {
      message.error('Erreur lors de l\'enregistrement');
    }
  };

  const handleDelete = async (id) => {
    try {
      // Vérifier si le client peut être supprimé
      const checkResponse = await api.get(`/clients/${id}/can-delete`);
      if (!checkResponse.data.can_delete) {
        message.error(checkResponse.data.reason);
        return;
      }

      await clientService.delete(id);
      message.success('Client supprimé avec succès');
      loadClients();
    } catch (error) {
      message.error(error.response?.data?.detail || 'Erreur lors de la suppression');
    }
  };

  const handleGenererRapport = async () => {
    try {
      setLoading(true);
      const response = await clientService.getRapportListe();

      // Télécharger le PDF
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      const today = new Date().toISOString().slice(0, 10).replace(/-/g, '');
      link.setAttribute('download', `clients_${today}.pdf`);
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

  const handleEdit = (client) => {
    setEditingClient(client);
    form.setFieldsValue(client);
    setModalVisible(true);
  };

  const handleAdd = () => {
    setEditingClient(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handlePrintLogistics = async (client) => {
    try {
      const response = await api.get(`/clients/${client.id}/logistics-balance/pdf`, { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `logistique_${client.nom}_${new Date().toISOString().slice(0, 10)}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      message.success('PDF généré avec succès');
    } catch (error) {
      message.error('Erreur lors de la génération du PDF');
      console.error(error);
    }
  };

  const handlePrintAllLogistics = async () => {
    try {
      setLoading(true);
      const response = await api.get('/clients/logistics-balance/all/pdf', { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `logistique_tous_clients_${new Date().toISOString().slice(0, 10)}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      message.success('Rapport global généré avec succès');
    } catch (error) {
      message.error('Erreur lors de la génération du rapport');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleViewLogistics = async (client) => {
    try {
      setLoadingLogistics(true);
      const response = await api.get(`/clients/${client.id}/logistics-balance`);
      setLogisticsData(response.data);
      setLogisticsModalVisible(true);
    } catch (error) {
      message.error('Erreur lors du chargement de la logistique');
      console.error(error);
    } finally {
      setLoadingLogistics(false);
    }
  };

  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 60,
    },
    {
      title: 'Nom',
      dataIndex: 'nom',
      key: 'nom',
    },
    {
      title: 'Prénom',
      dataIndex: 'prenom',
      key: 'prenom',
    },
    {
      title: 'Distance (km)',
      dataIndex: 'distance',
      key: 'distance',
      render: (value) => `${parseFloat(value).toFixed(2)} km`,
    },
    {
      title: 'Tarif (DA/km)',
      dataIndex: 'tarif_km',
      key: 'tarif_km',
      render: (value) => `${parseFloat(value).toFixed(2)} DA/km`,
    },
    {
      title: 'Téléphone',
      dataIndex: 'telephone',
      key: 'telephone',
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Button
            type="link"
            icon={<InfoCircleOutlined />}
            onClick={() => handleViewLogistics(record)}
            loading={loadingLogistics}
          >
            Logistique
          </Button>
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            Modifier
          </Button>
          <Popconfirm
            title="Êtes-vous sûr de vouloir supprimer ce client ?"
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
        <h2>Liste des Clients</h2>
        <Space>
          <Button
            type="default"
            icon={<FilePdfOutlined />}
            onClick={handlePrintAllLogistics}
            loading={loading}
          >
            Rapport Logistique Global
          </Button>
          <Button
            type="default"
            icon={<FilePdfOutlined />}
            onClick={handleGenererRapport}
            loading={loading}
          >
            Rapport Clients
          </Button>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={handleAdd}
          >
            Nouveau Client
          </Button>
        </Space>
      </div>

      <Table
        loading={loading}
        columns={columns}
        dataSource={clients}
        rowKey="id"
        pagination={{
          pageSize: 10,
          showTotal: (total) => `Total: ${total} clients`,
        }}
      />

      <Modal
        title={editingClient ? 'Modifier Client' : 'Nouveau Client'}
        open={modalVisible}
        onCancel={() => {
          setModalVisible(false);
          setEditingClient(null);
          form.resetFields();
        }}
        footer={null}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
        >
          <Form.Item
            label="Nom"
            name="nom"
            rules={[{ required: true, message: 'Veuillez saisir le nom' }]}
          >
            <Input />
          </Form.Item>

          <Form.Item
            label="Prénom"
            name="prenom"
            rules={[{ required: true, message: 'Veuillez saisir le prénom' }]}
          >
            <Input />
          </Form.Item>

          <Form.Item
            label="Distance (km)"
            name="distance"
            rules={[{ required: true, message: 'Veuillez saisir la distance' }]}
          >
            <InputNumber
              style={{ width: '100%' }}
              min={0}
              step={0.1}
              precision={2}
            />
          </Form.Item>

          <Form.Item
            label="Tarif kilométrique (DA/km)"
            name="tarif_km"
            rules={[{ required: true, message: 'Veuillez saisir le tarif kilométrique' }]}
            initialValue={3.00}
          >
            <InputNumber
              style={{ width: '100%' }}
              min={0}
              step={0.5}
              precision={2}
            />
          </Form.Item>

          <Form.Item
            label="Téléphone"
            name="telephone"
            rules={[{ required: true, message: 'Veuillez saisir le téléphone' }]}
          >
            <Input />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" style={{ marginRight: 8 }}>
              {editingClient ? 'Modifier' : 'Créer'}
            </Button>
            <Button onClick={() => setModalVisible(false)}>
              Annuler
            </Button>
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        title={`Solde Logistique - ${logisticsData?.client_nom || ''}`}
        open={logisticsModalVisible}
        onCancel={() => setLogisticsModalVisible(false)}
        footer={[
          <Button key="print" type="primary" icon={<FilePdfOutlined />}
            onClick={() => handlePrintLogistics({ id: logisticsData?.client_id, nom: logisticsData?.client_nom.split(' ')[1] })}>
            Imprimer
          </Button>,
          <Button key="close" onClick={() => setLogisticsModalVisible(false)}>
            Fermer
          </Button>
        ]}
        width={600}
      >
        {logisticsData && logisticsData.logistics_balance.length > 0 ? (
          <Table
            dataSource={logisticsData.logistics_balance}
            rowKey="type_id"
            pagination={false}
            columns={[
              {
                title: 'Type',
                dataIndex: 'type_name',
                key: 'type_name',
              },
              {
                title: 'Prises',
                dataIndex: 'total_prises',
                key: 'total_prises',
                align: 'center',
              },
              {
                title: 'Retournées',
                dataIndex: 'total_retournees',
                key: 'total_retournees',
                align: 'center',
              },
              {
                title: 'Solde',
                dataIndex: 'solde',
                key: 'solde',
                align: 'center',
                render: (solde) => (
                  <Tag color={solde > 0 ? 'red' : 'green'}>
                    {solde}
                  </Tag>
                ),
              },
            ]}
          />
        ) : (
          <p>Aucune donnée logistique pour ce client.</p>
        )}
      </Modal>
    </div>
  );
}

export default ClientsList;

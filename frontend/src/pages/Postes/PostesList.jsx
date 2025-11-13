import React, { useState, useEffect } from 'react';
import { Table, Button, Space, message, Popconfirm, Tag, Switch } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, CarOutlined } from '@ant-design/icons';
import { posteService } from '../../services';
import PosteForm from './PosteForm';

const PostesList = () => {
  const [postes, setPostes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingPoste, setEditingPoste] = useState(null);
  const [showInactive, setShowInactive] = useState(false);

  const fetchPostes = async () => {
    setLoading(true);
    try {
      const response = await posteService.getAll({ 
        actif_seulement: !showInactive 
      });
      setPostes(response.data.postes);
    } catch (error) {
      message.error('Erreur lors du chargement des postes');
      console.error('Erreur:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPostes();
  }, [showInactive]);

  const handleCreate = () => {
    setEditingPoste(null);
    setModalVisible(true);
  };

  const handleEdit = (record) => {
    setEditingPoste(record);
    setModalVisible(true);
  };

  const handleDelete = async (id, libelle) => {
    try {
      await posteService.delete(id);
      message.success(`Poste "${libelle}" supprimé`);
      fetchPostes();
    } catch (error) {
      message.error(error.response?.data?.detail || 'Erreur lors de la suppression');
    }
  };

  const handleFormSuccess = () => {
    setModalVisible(false);
    setEditingPoste(null);
    fetchPostes();
  };

  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 70,
    },
    {
      title: 'Libellé',
      dataIndex: 'libelle',
      key: 'libelle',
      render: (text, record) => (
        <Space>
          {text}
          {record.est_chauffeur && <CarOutlined style={{ color: '#1890ff' }} />}
        </Space>
      ),
    },
    {
      title: 'Chauffeur',
      dataIndex: 'est_chauffeur',
      key: 'est_chauffeur',
      width: 120,
      render: (value) => (
        <Tag color={value ? 'blue' : 'default'}>
          {value ? 'Oui' : 'Non'}
        </Tag>
      ),
    },
    {
      title: 'Modifiable',
      dataIndex: 'modifiable',
      key: 'modifiable',
      width: 120,
      render: (value) => (
        <Tag color={value ? 'green' : 'red'}>
          {value ? 'Oui' : 'Non'}
        </Tag>
      ),
    },
    {
      title: 'Statut',
      dataIndex: 'actif',
      key: 'actif',
      width: 100,
      render: (value) => (
        <Tag color={value ? 'success' : 'default'}>
          {value ? 'Actif' : 'Inactif'}
        </Tag>
      ),
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 150,
      render: (_, record) => (
        <Space size="small">
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
            disabled={!record.modifiable}
          >
            Modifier
          </Button>
          <Popconfirm
            title="Êtes-vous sûr de vouloir supprimer ce poste ?"
            description="Cette action désactivera le poste"
            onConfirm={() => handleDelete(record.id, record.libelle)}
            okText="Oui"
            cancelText="Non"
            disabled={!record.modifiable}
          >
            <Button
              type="link"
              danger
              icon={<DeleteOutlined />}
              disabled={!record.modifiable}
            >
              Supprimer
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: '24px' }}>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
        <Space>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={handleCreate}
          >
            Nouveau Poste
          </Button>
          <Switch
            checkedChildren="Inactifs inclus"
            unCheckedChildren="Actifs uniquement"
            checked={showInactive}
            onChange={setShowInactive}
          />
        </Space>
      </div>

      <Table
        columns={columns}
        dataSource={postes}
        rowKey="id"
        loading={loading}
        pagination={{
          pageSize: 20,
          showSizeChanger: true,
          showTotal: (total) => `Total: ${total} poste(s)`,
        }}
      />

      {modalVisible && (
        <PosteForm
          visible={modalVisible}
          onCancel={() => {
            setModalVisible(false);
            setEditingPoste(null);
          }}
          onSuccess={handleFormSuccess}
          poste={editingPoste}
        />
      )}
    </div>
  );
};

export default PostesList;

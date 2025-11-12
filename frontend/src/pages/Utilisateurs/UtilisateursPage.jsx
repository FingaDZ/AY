import { useState, useEffect } from 'react';
import {
  Card,
  Typography,
  Table,
  Button,
  Modal,
  Form,
  Input,
  Select,
  Switch,
  message,
  Space,
  Tag,
  Popconfirm,
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  UserOutlined,
  LockOutlined,
} from '@ant-design/icons';
import utilisateursService from '../../services/utilisateurs';

const { Title, Text } = Typography;
const { Option } = Select;

function UtilisateursPage() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [form] = Form.useForm();

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const data = await utilisateursService.list();
      setUsers(data);
    } catch (error) {
      console.error('Erreur lors du chargement des utilisateurs:', error);
      message.error('Impossible de charger les utilisateurs');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const handleCreate = () => {
    setEditingUser(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEdit = (user) => {
    setEditingUser(user);
    form.setFieldsValue({
      email: user.email,
      nom: user.nom,
      prenom: user.prenom,
      role: user.role,
      actif: user.actif,
    });
    setModalVisible(true);
  };

  const handleDelete = async (userId) => {
    try {
      await utilisateursService.delete(userId);
      message.success('Utilisateur supprimé avec succès');
      fetchUsers();
    } catch (error) {
      console.error('Erreur lors de la suppression:', error);
      message.error(error.response?.data?.detail || 'Erreur lors de la suppression');
    }
  };

  const handleSubmit = async (values) => {
    try {
      if (editingUser) {
        // Mise à jour
        const updateData = { ...values };
        if (!updateData.password) {
          delete updateData.password; // Ne pas envoyer si vide
        }
        await utilisateursService.update(editingUser.id, updateData);
        message.success('Utilisateur modifié avec succès');
      } else {
        // Création
        await utilisateursService.create(values);
        message.success('Utilisateur créé avec succès');
      }
      setModalVisible(false);
      form.resetFields();
      fetchUsers();
    } catch (error) {
      console.error('Erreur lors de la sauvegarde:', error);
      message.error(error.response?.data?.detail || 'Erreur lors de la sauvegarde');
    }
  };

  const columns = [
    {
      title: 'Email',
      dataIndex: 'email',
      key: 'email',
      sorter: (a, b) => a.email.localeCompare(b.email),
    },
    {
      title: 'Nom',
      dataIndex: 'nom',
      key: 'nom',
      sorter: (a, b) => a.nom.localeCompare(b.nom),
    },
    {
      title: 'Prénom',
      dataIndex: 'prenom',
      key: 'prenom',
      sorter: (a, b) => a.prenom.localeCompare(b.prenom),
    },
    {
      title: 'Rôle',
      dataIndex: 'role',
      key: 'role',
      render: (role) => (
        <Tag color={role === 'Admin' ? 'red' : 'blue'}>
          {role}
        </Tag>
      ),
      filters: [
        { text: 'Admin', value: 'Admin' },
        { text: 'Utilisateur', value: 'Utilisateur' },
      ],
      onFilter: (value, record) => record.role === value,
    },
    {
      title: 'Statut',
      dataIndex: 'actif',
      key: 'actif',
      render: (actif) => (
        <Tag color={actif ? 'green' : 'red'}>
          {actif ? 'Actif' : 'Inactif'}
        </Tag>
      ),
      filters: [
        { text: 'Actif', value: true },
        { text: 'Inactif', value: false },
      ],
      onFilter: (value, record) => record.actif === value,
    },
    {
      title: 'Dernière Connexion',
      dataIndex: 'derniere_connexion',
      key: 'derniere_connexion',
      render: (date) => {
        if (!date) return '-';
        return new Date(date).toLocaleString('fr-FR');
      },
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <Space size="small">
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            Modifier
          </Button>
          <Popconfirm
            title="Êtes-vous sûr de vouloir supprimer cet utilisateur ?"
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
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <div>
          <Title level={2}>Gestion des Utilisateurs</Title>
          <Text type="secondary">
            Gérez les utilisateurs et leurs rôles (Admin / Utilisateur)
          </Text>
        </div>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={handleCreate}
          size="large"
        >
          Nouvel Utilisateur
        </Button>
      </div>

      <Card>
        <Table
          columns={columns}
          dataSource={users}
          rowKey="id"
          loading={loading}
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showTotal: (total) => `Total: ${total} utilisateur(s)`,
          }}
        />
      </Card>

      <Modal
        title={editingUser ? 'Modifier l\'Utilisateur' : 'Nouvel Utilisateur'}
        open={modalVisible}
        onCancel={() => {
          setModalVisible(false);
          form.resetFields();
        }}
        footer={null}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          initialValues={{ role: 'Utilisateur', actif: true }}
        >
          <Form.Item
            label="Email"
            name="email"
            rules={[
              { required: true, message: 'Email requis' },
              { type: 'email', message: 'Email invalide' },
            ]}
          >
            <Input prefix={<UserOutlined />} placeholder="utilisateur@exemple.com" />
          </Form.Item>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <Form.Item
              label="Nom"
              name="nom"
              rules={[{ required: true, message: 'Nom requis' }]}
            >
              <Input placeholder="Dupont" />
            </Form.Item>

            <Form.Item
              label="Prénom"
              name="prenom"
              rules={[{ required: true, message: 'Prénom requis' }]}
            >
              <Input placeholder="Jean" />
            </Form.Item>
          </div>

          <Form.Item
            label="Mot de passe"
            name="password"
            rules={[
              { required: !editingUser, message: 'Mot de passe requis' },
              { min: 6, message: 'Minimum 6 caractères' },
            ]}
            extra={editingUser ? 'Laissez vide pour ne pas modifier' : null}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder={editingUser ? 'Laisser vide pour ne pas changer' : 'Minimum 6 caractères'}
            />
          </Form.Item>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <Form.Item
              label="Rôle"
              name="role"
              rules={[{ required: true, message: 'Rôle requis' }]}
            >
              <Select placeholder="Sélectionner un rôle">
                <Option value="Admin">
                  <Tag color="red">Admin</Tag> - Accès complet
                </Option>
                <Option value="Utilisateur">
                  <Tag color="blue">Utilisateur</Tag> - Gestion missions uniquement
                </Option>
              </Select>
            </Form.Item>

            <Form.Item
              label="Statut"
              name="actif"
              valuePropName="checked"
            >
              <Switch
                checkedChildren="Actif"
                unCheckedChildren="Inactif"
              />
            </Form.Item>
          </div>

          <Form.Item style={{ marginBottom: 0, marginTop: 24 }}>
            <Space>
              <Button type="primary" htmlType="submit">
                {editingUser ? 'Mettre à jour' : 'Créer'}
              </Button>
              <Button onClick={() => {
                setModalVisible(false);
                form.resetFields();
              }}>
                Annuler
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}

export default UtilisateursPage;

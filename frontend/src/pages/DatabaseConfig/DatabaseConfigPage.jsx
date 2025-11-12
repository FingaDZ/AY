import { useState, useEffect } from 'react';
import { 
  Card, 
  Typography, 
  Form, 
  Input, 
  InputNumber,
  Button, 
  message, 
  Space,
  Alert,
  Divider,
  Table,
  Tag,
  Modal
} from 'antd';
import { 
  SaveOutlined, 
  ReloadOutlined, 
  ThunderboltOutlined,
  DatabaseOutlined,
  HistoryOutlined,
  ExclamationCircleOutlined
} from '@ant-design/icons';
import databaseConfigService from '../../services/databaseConfig';

const { Title, Text, Paragraph } = Typography;

function DatabaseConfigPage() {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [testing, setTesting] = useState(false);
  const [fetching, setFetching] = useState(true);
  const [initialData, setInitialData] = useState({});
  const [testResult, setTestResult] = useState(null);
  const [showHistory, setShowHistory] = useState(false);
  const [history, setHistory] = useState([]);

  const fetchConfig = async () => {
    try {
      setFetching(true);
      const data = await databaseConfigService.getConfig();
      setInitialData(data);
    } catch (error) {
      console.error('Erreur lors du chargement de la configuration:', error);
      message.error('Impossible de charger la configuration');
    } finally {
      setFetching(false);
    }
  };

  const fetchHistory = async () => {
    try {
      const data = await databaseConfigService.getHistory();
      setHistory(data);
      setShowHistory(true);
    } catch (error) {
      message.error('Impossible de charger l\'historique');
    }
  };

  useEffect(() => {
    fetchConfig();
  }, []);

  useEffect(() => {
    if (initialData && Object.keys(initialData).length > 0) {
      form.setFieldsValue(initialData);
    }
  }, [initialData, form]);

  const handleTestConnection = async () => {
    try {
      await form.validateFields();
      const values = form.getFieldsValue();
      
      setTesting(true);
      setTestResult(null);
      
      const result = await databaseConfigService.testConnection(values);
      setTestResult(result);
      
      if (result.success) {
        message.success('Connexion réussie!');
      } else {
        message.error('Échec de la connexion');
      }
    } catch (error) {
      if (error.errorFields) {
        message.warning('Veuillez remplir tous les champs requis');
      } else {
        message.error('Erreur lors du test de connexion');
      }
    } finally {
      setTesting(false);
    }
  };

  const handleSubmit = async (values) => {
    Modal.confirm({
      title: 'Confirmer la sauvegarde',
      icon: <ExclamationCircleOutlined />,
      content: 'Cette configuration remplacera la configuration actuelle. Le serveur devra être redémarré pour appliquer les changements. Voulez-vous continuer?',
      okText: 'Oui, sauvegarder',
      cancelText: 'Annuler',
      onOk: async () => {
        try {
          setLoading(true);
          const result = await databaseConfigService.createOrUpdate(values);
          message.success(result.message || 'Configuration sauvegardée avec succès');
          message.warning('Redémarrez le serveur backend pour appliquer les changements', 5);
          fetchConfig();
        } catch (error) {
          console.error('Erreur lors de la sauvegarde:', error);
          message.error(error.response?.data?.detail || 'Erreur lors de la sauvegarde');
        } finally {
          setLoading(false);
        }
      }
    });
  };

  const historyColumns = [
    {
      title: 'Date',
      dataIndex: 'date_creation',
      key: 'date_creation',
      render: (text) => new Date(text).toLocaleString('fr-FR'),
    },
    {
      title: 'Host',
      dataIndex: 'host',
      key: 'host',
    },
    {
      title: 'Port',
      dataIndex: 'port',
      key: 'port',
    },
    {
      title: 'Base de données',
      dataIndex: 'database_name',
      key: 'database_name',
    },
    {
      title: 'Utilisateur',
      dataIndex: 'username',
      key: 'username',
    },
    {
      title: 'Statut',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (active) => (
        <Tag color={active ? 'green' : 'default'}>
          {active ? 'Active' : 'Inactive'}
        </Tag>
      ),
    },
  ];

  return (
    <div>
      <Title level={2}>
        <DatabaseOutlined /> Configuration Base de Données
      </Title>
      <Text type="secondary">
        Configuration de la connexion à la base de données MySQL. Ces paramètres remplacent ceux du fichier config.py.
      </Text>

      <Alert
        message="Important"
        description="Après avoir sauvegardé une nouvelle configuration, vous devez redémarrer le serveur backend pour que les changements prennent effet."
        type="warning"
        showIcon
        style={{ marginTop: 16, marginBottom: 16 }}
      />

      {initialData.source === 'config.py' && (
        <Alert
          message="Configuration actuelle depuis config.py"
          description="Aucune configuration personnalisée n'a été enregistrée. Les paramètres affichés proviennent du fichier de configuration par défaut."
          type="info"
          showIcon
          style={{ marginBottom: 16 }}
        />
      )}

      <Card style={{ marginTop: 24 }} loading={fetching}>
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          autoComplete="off"
          initialValues={initialData}
        >
          <Divider orientation="left">Serveur MySQL</Divider>
          
          <Form.Item
            label="Hôte"
            name="host"
            rules={[{ required: true, message: 'L\'hôte est requis' }]}
            tooltip="Adresse du serveur MySQL (ex: localhost, 127.0.0.1, ou IP distante)"
          >
            <Input placeholder="localhost" />
          </Form.Item>

          <Form.Item
            label="Port"
            name="port"
            rules={[{ required: true, message: 'Le port est requis' }]}
            tooltip="Port MySQL (par défaut: 3306)"
          >
            <InputNumber min={1} max={65535} style={{ width: '100%' }} placeholder="3306" />
          </Form.Item>

          <Divider orientation="left">Base de Données</Divider>

          <Form.Item
            label="Nom de la base de données"
            name="database_name"
            rules={[{ required: true, message: 'Le nom de la base de données est requis' }]}
            tooltip="Nom de la base de données MySQL à utiliser"
          >
            <Input placeholder="ay_hr" />
          </Form.Item>

          <Form.Item
            label="Charset"
            name="charset"
            tooltip="Encodage des caractères (recommandé: utf8mb4)"
          >
            <Input placeholder="utf8mb4" />
          </Form.Item>

          <Divider orientation="left">Authentification</Divider>

          <Form.Item
            label="Nom d'utilisateur"
            name="username"
            rules={[{ required: true, message: 'Le nom d\'utilisateur est requis' }]}
            tooltip="Utilisateur MySQL avec droits d'accès à la base"
          >
            <Input placeholder="root" />
          </Form.Item>

          <Form.Item
            label="Mot de passe"
            name="password"
            rules={[{ required: true, message: 'Le mot de passe est requis' }]}
            tooltip="Mot de passe de l'utilisateur MySQL"
          >
            <Input.Password placeholder="••••••••" />
          </Form.Item>

          {testResult && (
            <Alert
              message={testResult.success ? 'Test réussi' : 'Test échoué'}
              description={
                testResult.success 
                  ? `Connexion établie avec succès. Version MySQL: ${testResult.mysql_version}`
                  : testResult.message
              }
              type={testResult.success ? 'success' : 'error'}
              showIcon
              closable
              style={{ marginBottom: 16 }}
            />
          )}

          <Form.Item>
            <Space>
              <Button
                type="default"
                icon={<ThunderboltOutlined />}
                onClick={handleTestConnection}
                loading={testing}
              >
                Tester la connexion
              </Button>

              <Button
                type="primary"
                icon={<SaveOutlined />}
                htmlType="submit"
                loading={loading}
                disabled={testing}
              >
                Enregistrer
              </Button>

              <Button
                icon={<ReloadOutlined />}
                onClick={fetchConfig}
                disabled={loading || testing}
              >
                Recharger
              </Button>

              <Button
                icon={<HistoryOutlined />}
                onClick={fetchHistory}
              >
                Historique
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>

      <Modal
        title="Historique des configurations"
        open={showHistory}
        onCancel={() => setShowHistory(false)}
        footer={null}
        width={900}
      >
        <Table
          columns={historyColumns}
          dataSource={history}
          rowKey="id"
          pagination={{ pageSize: 10 }}
        />
      </Modal>
    </div>
  );
}

export default DatabaseConfigPage;

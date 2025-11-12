import { useState, useEffect } from 'react';
import { Card, Typography, Form, Input, Button, message, Spin, Divider } from 'antd';
import { SaveOutlined, ReloadOutlined } from '@ant-design/icons';
import parametresService from '../../services/parametres';

const { Title, Text } = Typography;

function ParametresPage() {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [fetching, setFetching] = useState(true);
  const [initialData, setInitialData] = useState({});

  const fetchParametres = async () => {
    try {
      setFetching(true);
      const data = await parametresService.getParametres();
      setInitialData(data);
      // Ne plus utiliser form.setFieldsValue ici
    } catch (error) {
      console.error('Erreur lors du chargement des paramètres:', error);
      message.error('Impossible de charger les paramètres');
    } finally {
      setFetching(false);
    }
  };

  useEffect(() => {
    fetchParametres();
  }, []);

  // Mettre à jour le form quand les données initiales changent
  useEffect(() => {
    if (initialData && Object.keys(initialData).length > 0) {
      form.setFieldsValue(initialData);
    }
  }, [initialData, form]);

  const handleSubmit = async (values) => {
    try {
      setLoading(true);
      await parametresService.updateParametres(values);
      message.success('Paramètres enregistrés avec succès');
    } catch (error) {
      console.error('Erreur lors de la sauvegarde:', error);
      message.error('Erreur lors de la sauvegarde des paramètres');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <Title level={2}>Paramètres de l'Entreprise</Title>
      <Text type="secondary">
        Configuration des informations de l'entreprise utilisées dans les rapports et documents.
      </Text>

      <Card style={{ marginTop: 24 }} loading={fetching}>
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          autoComplete="off"
          initialValues={initialData}
        >
          <Divider orientation="left">Identification de l'Entreprise</Divider>
          
          <Form.Item
            label="Raison Sociale"
            name="raison_sociale"
            tooltip="Nom juridique de l'entreprise (ou Nom et Prénom si personne physique)"
          >
            <Input placeholder="Ex: SARL AY Ressources Humaines" />
          </Form.Item>

          <Form.Item
            label="Nom Commercial"
            name="nom_entreprise"
            tooltip="Nom d'usage de l'entreprise"
          >
            <Input placeholder="Ex: AY HR" />
          </Form.Item>

          <Form.Item
            label="Adresse"
            name="adresse"
          >
            <Input.TextArea 
              rows={2} 
              placeholder="Ex: 123 Rue de la République, Alger 16000" 
            />
          </Form.Item>

          <Divider orientation="left">Numéros d'Identification</Divider>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <Form.Item
              label="Registre de Commerce (RC)"
              name="rc"
            >
              <Input placeholder="Ex: 12345678" />
            </Form.Item>

            <Form.Item
              label="NIF (Numéro Immatriculation Fiscale)"
              name="nif"
            >
              <Input placeholder="Ex: 098765432101234" />
            </Form.Item>

            <Form.Item
              label="NIS (Numéro Identification Statistique)"
              name="nis"
            >
              <Input placeholder="Ex: 098765432101" />
            </Form.Item>

            <Form.Item
              label="ART (Article Imposition)"
              name="art"
            >
              <Input placeholder="Ex: 16011234567890" />
            </Form.Item>
          </div>

          <Divider orientation="left">Informations de Contact</Divider>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <Form.Item
              label="N° Sécurité Sociale (Employeur)"
              name="numero_secu_employeur"
            >
              <Input placeholder="Ex: 12345678901234567890" />
            </Form.Item>

            <Form.Item
              label="Téléphone"
              name="telephone"
            >
              <Input placeholder="Ex: +213 21 23 45 67" />
            </Form.Item>
          </div>

          <Divider orientation="left">Informations Bancaires</Divider>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <Form.Item
              label="Banque"
              name="banque"
            >
              <Input placeholder="Ex: BNA - Agence Alger Centre" />
            </Form.Item>

            <Form.Item
              label="Compte Bancaire"
              name="compte_bancaire"
            >
              <Input placeholder="Ex: 0123456789012345678" />
            </Form.Item>
          </div>

          <Form.Item style={{ marginTop: 24 }}>
            <Button 
              type="primary" 
              htmlType="submit" 
              icon={<SaveOutlined />}
              loading={loading}
              size="large"
            >
              Enregistrer les Paramètres
            </Button>
            <Button 
              icon={<ReloadOutlined />}
              onClick={fetchParametres}
              style={{ marginLeft: 8 }}
              size="large"
            >
              Recharger
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
}

export default ParametresPage;

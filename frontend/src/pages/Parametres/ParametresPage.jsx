import { useState, useEffect } from 'react';
import { Card, Typography, Form, Input, InputNumber, Button, message, Spin, Divider, Alert } from 'antd';
import { SaveOutlined, ReloadOutlined, CarOutlined } from '@ant-design/icons';
import parametresService from '../../services/parametres';
import { parametresSalaireService } from '../../services';
import LogisticsTypesManager from '../../components/LogisticsTypesManager';

const { Title, Text } = Typography;

// ⭐ v3.6.0: Composant pour les paramètres Missions
function MissionsParametres() {
  const [kmSupp, setKmSupp] = useState(10);
  const [loading, setLoading] = useState(false);
  const [fetching, setFetching] = useState(true);

  useEffect(() => {
    fetchParams();
  }, []);

  const fetchParams = async () => {
    try {
      setFetching(true);
      const response = await parametresSalaireService.getParametres();
      setKmSupp(response.data?.km_supplementaire_par_client || 10);
    } catch (error) {
      console.error('Erreur chargement paramètres missions:', error);
    } finally {
      setFetching(false);
    }
  };

  const handleSave = async () => {
    try {
      setLoading(true);
      await parametresSalaireService.updateParametres({ km_supplementaire_par_client: kmSupp });
      message.success('Km supplémentaire mis à jour');
    } catch (error) {
      console.error('Erreur sauvegarde:', error);
      message.error('Erreur lors de la sauvegarde');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card 
      title={<span><CarOutlined /> Paramètres Missions</span>}
      style={{ marginTop: 32 }}
      loading={fetching}
    >
      <Alert
        message="Calcul kilométrage multi-clients"
        description="Ce paramètre définit le nombre de km ajoutés pour chaque client supplémentaire dans une mission multi-clients."
        type="info"
        showIcon
        style={{ marginBottom: 16 }}
      />
      <Form layout="inline">
        <Form.Item label={<strong>Km supplémentaires par client</strong>}>
          <InputNumber
            min={0}
            max={100}
            value={kmSupp}
            onChange={setKmSupp}
            addonAfter="km"
            style={{ width: 150 }}
          />
        </Form.Item>
        <Form.Item>
          <Button
            type="primary"
            icon={<SaveOutlined />}
            onClick={handleSave}
            loading={loading}
          >
            Sauvegarder
          </Button>
        </Form.Item>
      </Form>
      <Text type="secondary" style={{ display: 'block', marginTop: 8 }}>
        Exemple: 3 clients (50km, 60km, 80km) → 80 + (2 × {kmSupp}) = {80 + (2 * kmSupp)} km total
      </Text>
    </Card>
  );
}

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

      {/* ⭐ v3.6.0: Paramètres Missions */}
      <MissionsParametres />

      {/* Logistics Types Section */}
      <div style={{ marginTop: 32 }}>
        <LogisticsTypesManager />
      </div>
    </div>
  );
}

export default ParametresPage;

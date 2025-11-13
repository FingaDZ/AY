import { useState, useEffect } from 'react';
import { Form, Input, DatePicker, Select, InputNumber, Button, Card, message, Spin } from 'antd';
import { useNavigate, useParams } from 'react-router-dom';
import { employeService } from '../../services';
import dayjs from 'dayjs';

const { Option } = Select;

function EmployeForm() {
  const navigate = useNavigate();
  const { id } = useParams();
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const isEdit = !!id;

  useEffect(() => {
    if (isEdit) {
      loadEmploye();
    }
  }, [id]);

  const loadEmploye = async () => {
    try {
      setLoading(true);
      const response = await employeService.getById(id);
      const data = response.data;
      
      form.setFieldsValue({
        ...data,
        date_naissance: dayjs(data.date_naissance),
        date_recrutement: dayjs(data.date_recrutement),
        date_fin_contrat: data.date_fin_contrat ? dayjs(data.date_fin_contrat) : null,
      });
    } catch (error) {
      message.error('Erreur lors du chargement de l\'employé');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (values) => {
    try {
      setSubmitting(true);
      
      // Convertir les dates en string seulement si ce sont des objets dayjs
      const data = {
        ...values,
        date_naissance: values.date_naissance?.format ? values.date_naissance.format('YYYY-MM-DD') : values.date_naissance,
        date_recrutement: values.date_recrutement?.format ? values.date_recrutement.format('YYYY-MM-DD') : values.date_recrutement,
        date_fin_contrat: values.date_fin_contrat?.format ? values.date_fin_contrat.format('YYYY-MM-DD') : values.date_fin_contrat,
      };

      if (isEdit) {
        await employeService.update(id, data);
        message.success('Employé modifié avec succès');
        navigate('/employes');
      } else {
        await employeService.create(data);
        message.success('Employé créé avec succès');
        // Rediriger vers la liste après création
        navigate('/employes');
      }

      // Ne naviguer QUE si on est en mode édition
      // navigate('/employes');
    } catch (error) {
      const errorMsg = error.response?.data?.detail || error.message || 'Erreur inconnue';
      message.error(`Erreur lors de ${isEdit ? 'la modification' : 'la création'}: ${errorMsg}`);
      console.error('Error details:', error.response?.data || error);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', padding: 50 }}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div>
      <h2>{isEdit ? 'Modifier' : 'Nouvel'} Employé</h2>
      
      <Card style={{ maxWidth: 800, margin: '0 auto' }}>
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          initialValues={{
            situation_familiale: 'Célibataire',
            femme_au_foyer: false,
            prime_nuit_agent_securite: false,
            statut_contrat: 'Actif',
          }}
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
            label="Date de Naissance"
            name="date_naissance"
            rules={[{ required: true, message: 'Veuillez sélectionner la date' }]}
          >
            <DatePicker style={{ width: '100%' }} format="DD/MM/YYYY" />
          </Form.Item>

          <Form.Item
            label="Lieu de Naissance"
            name="lieu_naissance"
            rules={[{ required: true, message: 'Veuillez saisir le lieu' }]}
          >
            <Input />
          </Form.Item>

          <Form.Item
            label="Adresse"
            name="adresse"
            rules={[{ required: true, message: 'Veuillez saisir l\'adresse' }]}
          >
            <Input.TextArea rows={2} />
          </Form.Item>

          <Form.Item
            label="Mobile"
            name="mobile"
            rules={[{ required: true, message: 'Veuillez saisir le mobile' }]}
          >
            <Input />
          </Form.Item>

          <Form.Item
            label="N° Sécurité Sociale"
            name="numero_secu_sociale"
            rules={[{ required: true, message: 'Veuillez saisir le numéro' }]}
          >
            <Input />
          </Form.Item>

          <Form.Item
            label="N° Compte Bancaire"
            name="numero_compte_bancaire"
            rules={[{ required: true, message: 'Veuillez saisir le numéro' }]}
          >
            <Input />
          </Form.Item>

          <Form.Item
            label="N° ANEM"
            name="numero_anem"
            rules={[{ required: false }]}
          >
            <Input placeholder="N° ANEM (optionnel)" />
          </Form.Item>

          <Form.Item
            label="Situation Familiale"
            name="situation_familiale"
            rules={[{ required: true }]}
          >
            <Select>
              <Option value="Célibataire">Célibataire</Option>
              <Option value="Marié">Marié</Option>
            </Select>
          </Form.Item>

          <Form.Item
            label="Femme au Foyer"
            name="femme_au_foyer"
            valuePropName="checked"
          >
            <Select>
              <Option value={true}>Oui</Option>
              <Option value={false}>Non</Option>
            </Select>
          </Form.Item>

          <Form.Item
            label="Date de Recrutement"
            name="date_recrutement"
            rules={[{ required: true, message: 'Veuillez sélectionner la date' }]}
          >
            <DatePicker style={{ width: '100%' }} format="DD/MM/YYYY" />
          </Form.Item>

          <Form.Item
            label="Date de Fin de Contrat"
            name="date_fin_contrat"
          >
            <DatePicker style={{ width: '100%' }} format="DD/MM/YYYY" />
          </Form.Item>

          <Form.Item
            label="Poste de Travail"
            name="poste_travail"
            rules={[{ required: true, message: 'Veuillez saisir le poste' }]}
          >
            <Input />
          </Form.Item>

          <Form.Item
            label="Salaire de Base (DA)"
            name="salaire_base"
            rules={[
              { required: true, message: 'Veuillez saisir le salaire' },
              { 
                type: 'number', 
                min: 20000, 
                message: 'Le salaire minimum légal est de 20 000 DA' 
              }
            ]}
          >
            <InputNumber
              style={{ width: '100%' }}
              min={20000}
              step={1000}
              formatter={value => `${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ' ')}
              parser={value => value.replace(/\s?/g, '')}
            />
          </Form.Item>

          <Form.Item
            label="Prime de Nuit Agent Sécurité (750 DA/mois)"
            name="prime_nuit_agent_securite"
            valuePropName="checked"
          >
            <Select>
              <Option value={true}>Oui</Option>
              <Option value={false}>Non</Option>
            </Select>
          </Form.Item>

          <Form.Item
            label="Statut du Contrat"
            name="statut_contrat"
            rules={[{ required: true, message: 'Veuillez sélectionner le statut' }]}
          >
            <Select>
              <Select.Option value="Actif">Actif</Select.Option>
              <Select.Option value="Inactif">Inactif</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" loading={submitting} style={{ marginRight: 8 }}>
              {isEdit ? 'Modifier' : 'Créer'}
            </Button>
            <Button onClick={() => navigate('/employes')}>
              Annuler
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
}

export default EmployeForm;

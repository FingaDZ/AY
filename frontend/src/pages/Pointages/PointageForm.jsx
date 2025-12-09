import { useState, useEffect } from 'react';
import { Form, Select, Button, Card, message, Spin, Table, Tag } from 'antd';
import { useNavigate, useParams } from 'react-router-dom';
import { pointageService, employeService } from '../../services';

const { Option } = Select;

const TYPE_JOUR = {
  TRAVAILLE: { label: 'Tr', color: 'green', value: 'Travaillé' },
  ABSENT: { label: 'Ab', color: 'red', value: 'Absent' },
  CONGE: { label: 'Co', color: 'blue', value: 'Congé' },
  MALADIE: { label: 'Ma', color: 'orange', value: 'Maladie' },
  FERIE: { label: 'Fe', color: 'purple', value: 'Férié' },
  ARRET: { label: 'Ar', color: 'volcano', value: 'Arrêt' },
};

const currentYear = new Date().getFullYear();
const currentMonth = new Date().getMonth() + 1;

function PointageForm() {
  const navigate = useNavigate();
  const { id } = useParams();
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [employes, setEmployes] = useState([]);
  const [jours, setJours] = useState({});

  const isEdit = !!id;

  useEffect(() => {
    loadEmployes();
    if (isEdit) {
      loadPointage();
    } else {
      // Initialiser avec des valeurs par défaut
      initializeJours();
    }
  }, [id]);

  const loadEmployes = async () => {
    try {
      const response = await employeService.getAll({ statut: 'Actif' });
      setEmployes(response.data.employes || []);
    } catch (error) {
      message.error('Erreur lors du chargement des employés');
    }
  };

  const loadPointage = async () => {
    try {
      setLoading(true);
      const response = await pointageService.getById(id);
      const data = response.data;
      
      form.setFieldsValue({
        employe_id: data.employe_id,
        annee: data.annee,
        mois: data.mois,
      });

      const joursData = {};
      for (let i = 1; i <= 31; i++) {
        const key = `jour_${i.toString().padStart(2, '0')}`;
        joursData[key] = data[key] || null;
      }
      setJours(joursData);
    } catch (error) {
      message.error('Erreur lors du chargement du pointage');
    } finally {
      setLoading(false);
    }
  };

  const initializeJours = () => {
    const joursData = {};
    for (let i = 1; i <= 31; i++) {
      const key = `jour_${i.toString().padStart(2, '0')}`;
      joursData[key] = 'Travaillé'; // Par défaut tous travaillés
    }
    setJours(joursData);
    form.setFieldsValue({
      annee: currentYear,
      mois: currentMonth,
    });
  };

  const handleJourChange = (jour, value) => {
    const newJours = { ...jours, [jour]: value };
    setJours(newJours);
    
    // Auto-save en mode édition
    if (isEdit) {
      autoSave(newJours);
    }
  };

  const autoSave = async (joursData) => {
    try {
      const values = form.getFieldsValue();
      const data = {
        ...values,
        ...joursData,
      };
      await pointageService.update(id, data);
      message.success('Modification sauvegardée', 1);
    } catch (error) {
      message.error('Erreur lors de la sauvegarde automatique');
      console.error(error);
    }
  };

  const remplirTous = (type) => {
    const newJours = {};
    for (let i = 1; i <= 31; i++) {
      const key = `jour_${i.toString().padStart(2, '0')}`;
      newJours[key] = type;
    }
    setJours(newJours);
  };

  const calculateTotals = () => {
    let travailles = 0, absents = 0, conges = 0, maladies = 0, feries = 0, arrets = 0;
    
    Object.values(jours).forEach(jour => {
      if (jour === 'Travaillé') travailles++;
      else if (jour === 'Absent') absents++;
      else if (jour === 'Congé') conges++;
      else if (jour === 'Maladie') maladies++;
      else if (jour === 'Férié') feries++;
      else if (jour === 'Arrêt') arrets++;
    });

    return { travailles, absents, conges, maladies, feries, arrets };
  };

  const handleSubmit = async (values) => {
    try {
      setSubmitting(true);
      const data = {
        ...values,
        ...jours,
      };

      if (isEdit) {
        await pointageService.update(id, data);
        message.success('Pointage modifié avec succès');
      } else {
        await pointageService.create(data);
        message.success('Pointage créé avec succès');
      }

      navigate('/pointages');
    } catch (error) {
      message.error(`Erreur lors de ${isEdit ? 'la modification' : 'la création'}`);
      console.error(error);
    } finally {
      setSubmitting(false);
    }
  };

  const renderGrille = () => {
    const days = [];
    for (let i = 1; i <= 31; i++) {
      const key = `jour_${i.toString().padStart(2, '0')}`;
      days.push({
        jour: i,
        key: key,
        value: jours[key],
      });
    }

    // Grouper par semaine (7 jours)
    const weeks = [];
    for (let i = 0; i < days.length; i += 7) {
      weeks.push(days.slice(i, i + 7));
    }

    return (
      <div>
        {weeks.map((week, weekIndex) => (
          <div key={weekIndex} style={{ display: 'flex', marginBottom: 8 }}>
            {week.map(day => (
              <div key={day.jour} style={{ flex: 1, marginRight: 4 }}>
                <div style={{ textAlign: 'center', fontSize: 12, marginBottom: 4 }}>
                  J{day.jour}
                </div>
                <Select
                  value={day.value}
                  style={{ width: '100%' }}
                  onChange={(value) => handleJourChange(day.key, value)}
                >
                  {Object.entries(TYPE_JOUR).map(([key, type]) => (
                    <Option key={key} value={type.value}>
                      <Tag color={type.color}>{type.label}</Tag>
                    </Option>
                  ))}
                </Select>
              </div>
            ))}
          </div>
        ))}
      </div>
    );
  };

  const totals = calculateTotals();

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', padding: 50 }}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div>
      <h2>{isEdit ? 'Modifier' : 'Nouveau'} Pointage</h2>
      
      <Card style={{ maxWidth: 1200, margin: '0 auto' }}>
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
        >
          <div style={{ display: 'flex', gap: 16, marginBottom: 24 }}>
            <Form.Item
              label="Employé"
              name="employe_id"
              rules={[{ required: true, message: 'Veuillez sélectionner un employé' }]}
              style={{ flex: 1 }}
            >
              <Select
                showSearch
                placeholder="Sélectionner un employé"
                optionFilterProp="children"
                disabled={isEdit}
              >
                {employes.map(emp => (
                  <Option key={emp.id} value={emp.id}>
                    {emp.prenom} {emp.nom} ({emp.poste_travail})
                  </Option>
                ))}
              </Select>
            </Form.Item>

            <Form.Item
              label="Mois"
              name="mois"
              rules={[{ required: true }]}
              style={{ width: 150 }}
            >
              <Select disabled={isEdit}>
                {[...Array(12)].map((_, i) => (
                  <Option key={i + 1} value={i + 1}>
                    {new Date(2000, i).toLocaleString('fr-FR', { month: 'long' })}
                  </Option>
                ))}
              </Select>
            </Form.Item>

            <Form.Item
              label="Année"
              name="annee"
              rules={[{ required: true }]}
              style={{ width: 120 }}
            >
              <Select disabled={isEdit}>
                {[currentYear - 1, currentYear, currentYear + 1].map(year => (
                  <Option key={year} value={year}>{year}</Option>
                ))}
              </Select>
            </Form.Item>
          </div>

          <Card title="Grille de Pointage (31 jours)" size="small">
            <div style={{ marginBottom: 16 }}>
              <span style={{ marginRight: 8 }}>Remplir tout avec:</span>
              {Object.entries(TYPE_JOUR).map(([key, type]) => (
                <Button
                  key={key}
                  size="small"
                  style={{ marginRight: 4 }}
                  onClick={() => remplirTous(type.value)}
                >
                  <Tag color={type.color}>{type.label}</Tag>
                </Button>
              ))}
            </div>

            {renderGrille()}

            <div style={{ marginTop: 16, padding: 16, background: '#f0f2f5', borderRadius: 4 }}>
              <h4>Totaux</h4>
              <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
                <Tag color="green">Travaillés: {totals.travailles}</Tag>
                <Tag color="red">Absents: {totals.absents}</Tag>
                <Tag color="blue">Congés: {totals.conges}</Tag>
                <Tag color="orange">Maladies: {totals.maladies}</Tag>
                <Tag color="purple">Fériés: {totals.feries}</Tag>
                <Tag color="volcano">Arrêts: {totals.arrets}</Tag>
              </div>
            </div>
          </Card>

          <Form.Item style={{ marginTop: 24 }}>
            <Button type="primary" htmlType="submit" loading={submitting} style={{ marginRight: 8 }}>
              {isEdit ? 'Modifier' : 'Créer'}
            </Button>
            <Button onClick={() => navigate('/pointages')}>
              Annuler
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
}

export default PointageForm;

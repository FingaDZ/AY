import { useState, useEffect } from 'react';
import { Card, Select, Button, Table, message, Spin, Descriptions, InputNumber, Tag, Space, Dropdown, Menu, Modal } from 'antd';
import { CalculatorOutlined, EyeOutlined, FilePdfOutlined, FileZipOutlined, SaveOutlined, DownOutlined, CheckCircleOutlined, DollarCircleOutlined, EditOutlined, StopOutlined, WarningOutlined } from '@ant-design/icons';
import { salaireService, employeService } from '../../services';
import { useNavigate } from 'react-router-dom';
import api from '../../services/api';

const { Option } = Select;

const currentYear = new Date().getFullYear();
const currentMonth = new Date().getMonth() + 1;

function SalaireCalcul() {
  const [loading, setLoading] = useState(false);
  const [calculating, setCalculating] = useState(false);
  const [saving, setSaving] = useState(false);
  const [employes, setEmployes] = useState([]);
  const [salaires, setSalaires] = useState([]);
  const [totaux, setTotaux] = useState(null);
  const [filters, setFilters] = useState({
    annee: currentYear,
    mois: currentMonth,
    jours_supplementaires: 0,
  });

  useEffect(() => {
    loadEmployes();
  }, []);

  const loadEmployes = async () => {
    try {
      const response = await employeService.getAll({ statut: 'Actif' });
      setEmployes(response.data.employes || []);
    } catch (error) {
      message.error('Erreur lors du chargement des employés');
    }
  };

  const handleCalculer = async () => {
    if (!filters.annee || !filters.mois) {
      message.warning('Veuillez sélectionner une année et un mois');
      return;
    }

    try {
      setCalculating(true);
      const response = await salaireService.calculerTous(filters);
      setSalaires(response.data.salaires || []);
      setTotaux(response.data.totaux || null);
      message.success(`${response.data.calcules || 0} salaire(s) calculé(s) avec succès`);
    } catch (error) {
      message.error('Erreur lors du calcul des salaires');
      console.error(error);
    } finally {
      setCalculating(false);
    }
  };

  const handleSauvegarder = async () => {
    if (!filters.annee || !filters.mois) {
      message.warning('Veuillez sélectionner une année et un mois');
      return;
    }

    if (salaires.length === 0) {
      message.warning('Veuillez d\'abord calculer les salaires');
      return;
    }

    try {
      setSaving(true);
      const response = await salaireService.sauvegarderBatch(filters.annee, filters.mois);

      message.success(
        `${response.data.succes} salaire(s) sauvegardé(s) avec succès`,
        5
      );

      if (response.data.erreurs > 0) {
        message.warning(
          `${response.data.erreurs} erreur(s) lors de la sauvegarde`,
          5
        );
      }

      console.log('Détails de sauvegarde:', response.data.details);
    } catch (error) {
      message.error('Erreur lors de la sauvegarde des salaires');
      console.error(error);
    } finally {
      setSaving(false);
    }
  };

  const navigate = useNavigate();

  const verifierCongesAvantGeneration = async () => {
    try {
      const response = await api.get(`/conges/verifier-saisie/${filters.annee}/${filters.mois}`);
      return response.data;
    } catch (error) {
      console.error('Erreur vérification congés:', error);
      return { a_verifier: false, count: 0, conges_non_saisis: [] };
    }
  };

  const handleGenererBulletins = async () => {
    if (!filters.annee || !filters.mois) {
      message.warning('Veuillez sélectionner une année et un mois');
      return;
    }

    if (salaires.length === 0) {
      message.warning('Veuillez d\'abord calculer les salaires');
      return;
    }

    // Vérifier si des congés doivent être saisis
    const verif = await verifierCongesAvantGeneration();
    
    if (verif.a_verifier && verif.count > 0) {
      Modal.confirm({
        title: 'Attention : Congés non saisis',
        icon: <WarningOutlined style={{ color: '#faad14' }} />,
        content: (
          <div>
            <p>Il y a <b>{verif.count} employé(s)</b> avec des congés acquis mais non saisis pour {filters.mois}/{filters.annee}:</p>
            <ul style={{ maxHeight: '200px', overflowY: 'auto' }}>
              {verif.conges_non_saisis.map((c, i) => (
                <li key={i}>{c.employe_nom} - {c.jours_acquis} jour(s) acquis</li>
              ))}
            </ul>
            <p><b>Voulez-vous aller sur la page Congés pour les saisir maintenant ?</b></p>
          </div>
        ),
        okText: 'Oui, aller aux Congés',
        cancelText: 'Non, continuer quand même',
        width: 600,
        onOk: () => {
          navigate('/conges');
        },
        onCancel: () => {
          procederGenerationBulletins();
        }
      });
    } else {
      procederGenerationBulletins();
    }
  };

  const procederGenerationBulletins = async () => {
    try {
      setLoading(true);
      const response = await salaireService.genererBulletins(filters);

      // Créer un lien de téléchargement
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `bulletins_paie_${filters.mois.toString().padStart(2, '0')}_${filters.annee}.zip`);
      document.body.appendChild(link);
      link.click();
      link.remove();

      message.success('Bulletins de paie générés avec succès');
    } catch (error) {
      message.error('Erreur lors de la génération des bulletins');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleGenererBulletinsCombines = async () => {
    if (!filters.annee || !filters.mois) {
      message.warning('Veuillez sélectionner une année et un mois');
      return;
    }

    if (salaires.length === 0) {
      message.warning('Veuillez d\'abord calculer les salaires');
      return;
    }

    try {
      setLoading(true);
      const response = await salaireService.genererBulletinsCombines(filters);

      // Créer un lien de téléchargement
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `bulletins_combines_${filters.mois.toString().padStart(2, '0')}_${filters.annee}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();

      message.success('Bulletins combinés générés avec succès');
    } catch (error) {
      message.error('Erreur lors de la génération des bulletins combinés');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateStatut = async (salaireId, newStatut) => {
    try {
      await salaireService.updateStatut(salaireId, newStatut);
      message.success(`Statut mis à jour : ${newStatut.toUpperCase()}`);

      // Mise à jour locale
      setSalaires(prev => prev.map(s =>
        s.id === salaireId ? { ...s, statut: newStatut } : s
      ));
    } catch (error) {
      message.error("Erreur : " + (error.response?.data?.detail || error.message));
    }
  };

  const confirmStatusChange = (record, newStatut) => {
    Modal.confirm({
      title: 'Changement de statut',
      content: `Passer le salaire de ${employes.find(e => e.id === record.employe_id)?.prenom} au statut "${newStatut.toUpperCase()}" ?`,
      onOk: () => handleUpdateStatut(record.id, newStatut),
    });
  };

  const handleGenererRapport = async () => {
    if (!filters.annee || !filters.mois) {
      message.warning('Veuillez sélectionner une année et un mois');
      return;
    }

    if (salaires.length === 0) {
      message.warning('Veuillez d\'abord calculer les salaires');
      return;
    }

    try {
      setLoading(true);
      const response = await salaireService.genererRapport(filters);

      // Créer un lien de téléchargement
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `rapport_salaires_${filters.mois.toString().padStart(2, '0')}_${filters.annee}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();

      message.success('Rapport PDF généré avec succès');
    } catch (error) {
      message.error('Erreur lors de la génération du rapport');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const columns = [
    {
      title: 'N°',
      key: 'index',
      width: 50,
      render: (_, __, index) => index + 1,
      fixed: 'left',
    },
    {
      title: 'Employé',
      key: 'employe',
      width: 180,
      fixed: 'left',
      render: (_, record) => {
        const emp = employes.find(e => e.id === record.employe_id);
        return emp ? (
          <div>
            <div style={{ fontWeight: 'bold' }}>{emp.prenom} {emp.nom}</div>
            <div style={{ fontSize: '12px', color: '#888' }}>{emp.poste_travail}</div>
          </div>
        ) : record.employe_id;
      }
    },
    {
      title: 'Statut',
      dataIndex: 'statut',
      key: 'statut',
      width: 100,
      render: (val) => {
        let color = 'default';
        if (val === 'valide') color = 'blue';
        if (val === 'paye') color = 'green';
        return <Tag color={color}>{(val || 'brouillon').toUpperCase()}</Tag>;
      }
    },
    {
      title: 'Salaire Base Contrat',
      key: 'salaire_base_contrat',
      width: 130,
      align: 'right',
      render: (_, record) => {
        const emp = employes.find(e => e.id === record.employe_id);
        return emp ? `${parseFloat(emp.salaire_base || 0).toLocaleString('fr-FR', { minimumFractionDigits: 2 })} DA` : '-';
      }
    },
    {
      title: 'Jours Trav.',
      dataIndex: 'jours_travailles',
      key: 'jours',
      width: 80,
      align: 'center',
    },
    {
      title: 'Salaire Base Proratisé',
      dataIndex: 'salaire_base_proratis',
      key: 'salaire_base',
      width: 130,
      align: 'right',
      render: (val) => `${parseFloat(val || 0).toLocaleString('fr-FR', { minimumFractionDigits: 2 })}`
    },
    {
      title: 'H. Supp. (1.33h/j)',
      dataIndex: 'heures_supplementaires',
      key: 'heures_supp',
      width: 120,
      align: 'right',
      render: (val) => `${parseFloat(val || 0).toLocaleString('fr-FR', { minimumFractionDigits: 2 })}`
    },
    {
      title: 'Indemnités',
      children: [
        {
          title: 'IN (5%)',
          dataIndex: 'indemnite_nuisance',
          key: 'in',
          width: 100,
          align: 'right',
          render: (val) => `${parseFloat(val || 0).toLocaleString('fr-FR', { minimumFractionDigits: 2 })}`
        },
        {
          title: 'IFSP (5%)',
          dataIndex: 'ifsp',
          key: 'ifsp',
          width: 100,
          align: 'right',
          render: (val) => `${parseFloat(val || 0).toLocaleString('fr-FR', { minimumFractionDigits: 2 })}`
        },
        {
          title: 'IEP (1%/an)',
          dataIndex: 'iep',
          key: 'iep',
          width: 100,
          align: 'right',
          render: (val) => `${parseFloat(val || 0).toLocaleString('fr-FR', { minimumFractionDigits: 2 })}`
        },
      ]
    },
    {
      title: 'Primes',
      children: [
        {
          title: 'Encouragement (10%)',
          dataIndex: 'prime_encouragement',
          key: 'prime_encouragement',
          width: 130,
          align: 'right',
          render: (val) => `${parseFloat(val || 0).toLocaleString('fr-FR', { minimumFractionDigits: 2 })}`
        },
        {
          title: 'Chauffeur (100DA/j)',
          dataIndex: 'prime_chauffeur',
          key: 'prime_chauffeur',
          width: 130,
          align: 'right',
          render: (val) => `${parseFloat(val || 0).toLocaleString('fr-FR', { minimumFractionDigits: 2 })}`
        },
        {
          title: 'Nuit Séc. (750DA/m)',
          dataIndex: 'prime_nuit_agent_securite',
          key: 'prime_nuit',
          width: 130,
          align: 'right',
          render: (val) => `${parseFloat(val || 0).toLocaleString('fr-FR', { minimumFractionDigits: 2 })}`
        },
        {
          title: 'Déplacement',
          dataIndex: 'prime_deplacement',
          key: 'prime_deplacement',
          width: 110,
          align: 'right',
          render: (val) => `${parseFloat(val || 0).toLocaleString('fr-FR', { minimumFractionDigits: 2 })}`
        },
      ]
    },
    {
      title: 'Panier (100DA/j)',
      dataIndex: 'panier',
      key: 'panier',
      width: 110,
      align: 'right',
      render: (val) => `${parseFloat(val || 0).toLocaleString('fr-FR', { minimumFractionDigits: 2 })}`
    },
    {
      title: 'Transport (100DA/j)',
      dataIndex: 'prime_transport',
      key: 'transport',
      width: 130,
      align: 'right',
      render: (val) => `${parseFloat(val || 0).toLocaleString('fr-FR', { minimumFractionDigits: 2 })}`
    },
    {
      title: 'Retenues',
      children: [
        {
          title: 'SS (9%)',
          dataIndex: 'retenue_securite_sociale',
          key: 'retenue_ss',
          width: 110,
          align: 'right',
          render: (val) => (
            <span style={{ color: '#ff4d4f' }}>
              {parseFloat(val || 0).toLocaleString('fr-FR', { minimumFractionDigits: 2 })}
            </span>
          )
        },
        {
          title: 'IRG',
          dataIndex: 'irg',
          key: 'irg',
          width: 110,
          align: 'right',
          render: (val) => (
            <span style={{ color: '#ff4d4f' }}>
              {parseFloat(val || 0).toLocaleString('fr-FR', { minimumFractionDigits: 2 })}
            </span>
          )
        },
        {
          title: 'Avances',
          dataIndex: 'total_avances',
          key: 'avances',
          width: 100,
          align: 'right',
          render: (val) => (
            <span style={{ color: '#ff4d4f' }}>
              {parseFloat(val || 0).toLocaleString('fr-FR', { minimumFractionDigits: 2 })}
            </span>
          )
        },
        {
          title: 'Crédits',
          dataIndex: 'retenue_credit',
          key: 'credits',
          width: 100,
          align: 'right',
          render: (val) => (
            <span style={{ color: '#ff4d4f' }}>
              {parseFloat(val || 0).toLocaleString('fr-FR', { minimumFractionDigits: 2 })}
            </span>
          )
        },
      ]
    },
    {
      title: 'Salaire Net',
      dataIndex: 'salaire_net',
      key: 'salaire_net',
      width: 150,
      align: 'right',
      fixed: 'right',
      render: (val) => (
        <span style={{ fontWeight: 'bold', color: '#52c41a', fontSize: '15px' }}>
          {parseFloat(val || 0).toLocaleString('fr-FR', { minimumFractionDigits: 2 })} DA
        </span>
      )
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 80,
      fixed: 'right',
      render: (_, record) => {
        const items = [
          {
            key: 'valide',
            label: 'Valider',
            icon: <CheckCircleOutlined />,
            disabled: record.statut === 'valide' || record.statut === 'paye',
            onClick: () => confirmStatusChange(record, 'valide')
          },
          {
            key: 'paye',
            label: 'Payer',
            icon: <DollarCircleOutlined />,
            disabled: record.statut !== 'valide',
            onClick: () => confirmStatusChange(record, 'paye')
          },
          { type: 'divider' },
          {
            key: 'brouillon',
            label: 'Modif. (Brouillon)',
            icon: <EditOutlined />,
            disabled: record.statut === 'paye',
            onClick: () => confirmStatusChange(record, 'brouillon')
          }
        ];
        return (
          <Dropdown menu={{ items }} trigger={['click']}>
            <Button icon={<DownOutlined />} size="small" />
          </Dropdown>
        );
      }
    },
  ];

  return (
    <div>
      <h2>Calcul des Salaires</h2>

      <Card style={{ marginBottom: 16 }}>
        <Space size="middle" wrap>
          <div>
            <label style={{ marginRight: 8, fontWeight: 'bold' }}>Mois:</label>
            <Select
              value={filters.mois}
              style={{ width: 150 }}
              onChange={(value) => setFilters({ ...filters, mois: value })}
            >
              {[...Array(12)].map((_, i) => (
                <Option key={i + 1} value={i + 1}>
                  {new Date(2000, i).toLocaleString('fr-FR', { month: 'long' })}
                </Option>
              ))}
            </Select>
          </div>

          <div>
            <label style={{ marginRight: 8, fontWeight: 'bold' }}>Année:</label>
            <InputNumber
              value={filters.annee}
              min={2000}
              max={2100}
              style={{ width: 120 }}
              onChange={(value) => setFilters({ ...filters, annee: value })}
            />
          </div>

          <div>
            <label style={{ marginRight: 8, fontWeight: 'bold' }}>Jours Supplémentaires:</label>
            <InputNumber
              value={filters.jours_supplementaires}
              min={0}
              max={31}
              style={{ width: 100 }}
              onChange={(value) => setFilters({ ...filters, jours_supplementaires: value || 0 })}
            />
          </div>

          <Button
            type="primary"
            size="large"
            icon={<CalculatorOutlined />}
            onClick={handleCalculer}
            loading={calculating}
          >
            Calculer Tous les Salaires
          </Button>

          {salaires.length > 0 && (
            <>
              <Button
                type="primary"
                size="large"
                icon={<SaveOutlined />}
                onClick={handleSauvegarder}
                loading={saving}
                style={{ backgroundColor: '#1890ff', borderColor: '#1890ff' }}
              >
                Sauvegarder dans la Base
              </Button>

              <Button
                type="default"
                size="large"
                icon={<FileZipOutlined />}
                onClick={handleGenererBulletins}
                loading={loading}
                style={{ backgroundColor: '#52c41a', color: 'white', borderColor: '#52c41a' }}
              >
                Générer Bulletins de Paie (ZIP)
              </Button>

              <Button
                type="default"
                size="large"
                icon={<FilePdfOutlined />}
                onClick={handleGenererBulletinsCombines}
                loading={loading}
                style={{ backgroundColor: '#722ed1', color: 'white', borderColor: '#722ed1' }}
              >
                Bulletins Combinés (PDF)
              </Button>

              <Button
                type="primary"
                size="large"
                icon={<FilePdfOutlined />}
                onClick={handleGenererRapport}
                loading={loading}
              >
                Rapport PDF Complet
              </Button>
            </>
          )}
        </Space>
      </Card>

      {/* Résumé des totaux */}
      {totaux && (
        <Card style={{ marginBottom: 16, backgroundColor: '#f0f7ff' }}>
          <div style={{ display: 'flex', justifyContent: 'space-around', flexWrap: 'wrap', gap: 16 }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '14px', color: '#666' }}>Employés</div>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#1890ff' }}>
                {salaires.length}
              </div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '14px', color: '#666' }}>Salaire Cotisable Total</div>
              <div style={{ fontSize: '20px', fontWeight: 'bold' }}>
                {parseFloat(totaux.salaire_cotisable || 0).toLocaleString('fr-FR', { minimumFractionDigits: 2 })} DA
              </div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '14px', color: '#666' }}>Total Retenues SS</div>
              <div style={{ fontSize: '20px', fontWeight: 'bold', color: '#ff4d4f' }}>
                {parseFloat(totaux.retenue_securite_sociale || 0).toLocaleString('fr-FR', { minimumFractionDigits: 2 })} DA
              </div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '14px', color: '#666' }}>Total IRG</div>
              <div style={{ fontSize: '20px', fontWeight: 'bold', color: '#ff4d4f' }}>
                {parseFloat(totaux.irg || 0).toLocaleString('fr-FR', { minimumFractionDigits: 2 })} DA
              </div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '14px', color: '#666' }}>Total Avances</div>
              <div style={{ fontSize: '20px', fontWeight: 'bold', color: '#ff4d4f' }}>
                {parseFloat(totaux.total_avances || 0).toLocaleString('fr-FR', { minimumFractionDigits: 2 })} DA
              </div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '14px', color: '#666' }}>Total Crédits</div>
              <div style={{ fontSize: '20px', fontWeight: 'bold', color: '#ff4d4f' }}>
                {parseFloat(totaux.retenue_credit || 0).toLocaleString('fr-FR', { minimumFractionDigits: 2 })} DA
              </div>
            </div>
            <div style={{ textAlign: 'center', padding: '0 20px', borderLeft: '2px solid #52c41a' }}>
              <div style={{ fontSize: '14px', color: '#666' }}>SALAIRE NET TOTAL</div>
              <div style={{ fontSize: '28px', fontWeight: 'bold', color: '#52c41a' }}>
                {parseFloat(totaux.salaire_net || 0).toLocaleString('fr-FR', { minimumFractionDigits: 2 })} DA
              </div>
            </div>
          </div>
        </Card>
      )}

      {calculating ? (
        <div style={{ textAlign: 'center', padding: 50 }}>
          <Spin size="large" />
          <p>Calcul des salaires en cours...</p>
        </div>
      ) : (
        <Card>
          <Table
            columns={columns}
            dataSource={salaires}
            rowKey={(record) => record.employe_id}
            pagination={{
              pageSize: 50,
              showTotal: (total) => `Total: ${total} employé(s)`,
              showSizeChanger: true,
              pageSizeOptions: ['10', '20', '50', '100'],
            }}
            scroll={{ x: 2400, y: 600 }}
            size="small"
            bordered
            expandable={{
              expandedRowRender: (record) => (
                <Card style={{ backgroundColor: '#fafafa' }}>
                  <h4>Détails du calcul - {employes.find(e => e.id === record.employe_id)?.prenom} {employes.find(e => e.id === record.employe_id)?.nom}</h4>
                  <Descriptions bordered size="small" column={3}>
                    <Descriptions.Item label="Jours Travaillés">
                      {record.jours_travailles} / {record.jours_ouvrables}
                    </Descriptions.Item>
                    <Descriptions.Item label="Salaire Base Proratisé" span={2}>
                      {parseFloat(record.salaire_base_proratis || 0).toLocaleString('fr-FR', { minimumFractionDigits: 2 })} DA
                    </Descriptions.Item>

                    <Descriptions.Item label="Heures Supplémentaires">
                      {parseFloat(record.heures_supplementaires || 0).toLocaleString('fr-FR', { minimumFractionDigits: 2 })} DA
                    </Descriptions.Item>
                    <Descriptions.Item label="IN (5%)">
                      {parseFloat(record.indemnite_nuisance || 0).toLocaleString('fr-FR', { minimumFractionDigits: 2 })} DA
                    </Descriptions.Item>
                    <Descriptions.Item label="IFSP (5%)">
                      {parseFloat(record.ifsp || 0).toLocaleString('fr-FR', { minimumFractionDigits: 2 })} DA
                    </Descriptions.Item>

                    <Descriptions.Item label="IEP (Ancienneté)">
                      {parseFloat(record.iep || 0).toLocaleString('fr-FR', { minimumFractionDigits: 2 })} DA
                    </Descriptions.Item>
                    <Descriptions.Item label="Prime Encouragement (10%)">
                      {parseFloat(record.prime_encouragement || 0).toLocaleString('fr-FR', { minimumFractionDigits: 2 })} DA
                    </Descriptions.Item>
                    <Descriptions.Item label="Prime Chauffeur">
                      {parseFloat(record.prime_chauffeur || 0).toLocaleString('fr-FR', { minimumFractionDigits: 2 })} DA
                    </Descriptions.Item>

                    <Descriptions.Item label="Prime Déplacement (Missions)">
                      {parseFloat(record.prime_deplacement || 0).toLocaleString('fr-FR', { minimumFractionDigits: 2 })} DA
                    </Descriptions.Item>
                    <Descriptions.Item label="Prime Objectif">
                      {parseFloat(record.prime_objectif || 0).toLocaleString('fr-FR', { minimumFractionDigits: 2 })} DA
                    </Descriptions.Item>
                    <Descriptions.Item label="Prime Variable">
                      {parseFloat(record.prime_variable || 0).toLocaleString('fr-FR', { minimumFractionDigits: 2 })} DA
                    </Descriptions.Item>

                    <Descriptions.Item label="Salaire Cotisable" span={3}>
                      <Tag color="blue" style={{ fontSize: '14px', padding: '4px 12px' }}>
                        {parseFloat(record.salaire_cotisable || 0).toLocaleString('fr-FR', { minimumFractionDigits: 2 })} DA
                      </Tag>
                    </Descriptions.Item>

                    <Descriptions.Item label="Panier (100 DA/jour)">
                      {parseFloat(record.panier || 0).toLocaleString('fr-FR', { minimumFractionDigits: 2 })} DA
                    </Descriptions.Item>
                    <Descriptions.Item label="Prime Transport (100 DA/jour)">
                      {parseFloat(record.prime_transport || 0).toLocaleString('fr-FR', { minimumFractionDigits: 2 })} DA
                    </Descriptions.Item>
                    <Descriptions.Item label="Prime Femme au Foyer">
                      {parseFloat(record.prime_femme_foyer || 0).toLocaleString('fr-FR', { minimumFractionDigits: 2 })} DA
                    </Descriptions.Item>

                    <Descriptions.Item label="Retenue Sécurité Sociale (9%)">
                      <span style={{ color: '#ff4d4f', fontWeight: 'bold' }}>
                        - {parseFloat(record.retenue_securite_sociale || 0).toLocaleString('fr-FR', { minimumFractionDigits: 2 })} DA
                      </span>
                    </Descriptions.Item>
                    <Descriptions.Item label="IRG">
                      <span style={{ color: '#ff4d4f', fontWeight: 'bold' }}>
                        - {parseFloat(record.irg || 0).toLocaleString('fr-FR', { minimumFractionDigits: 2 })} DA
                      </span>
                    </Descriptions.Item>
                    <Descriptions.Item label="Salaire Imposable">
                      <Tag color="cyan" style={{ fontSize: '14px', padding: '4px 12px' }}>
                        {parseFloat(record.salaire_imposable || 0).toLocaleString('fr-FR', { minimumFractionDigits: 2 })} DA
                      </Tag>
                    </Descriptions.Item>

                    <Descriptions.Item label="Avances du Mois">
                      <span style={{ color: '#ff4d4f', fontWeight: 'bold' }}>
                        - {parseFloat(record.total_avances || 0).toLocaleString('fr-FR', { minimumFractionDigits: 2 })} DA
                      </span>
                    </Descriptions.Item>
                    <Descriptions.Item label="Retenue Crédit">
                      <span style={{ color: '#ff4d4f', fontWeight: 'bold' }}>
                        - {parseFloat(record.retenue_credit || 0).toLocaleString('fr-FR', { minimumFractionDigits: 2 })} DA
                      </span>
                    </Descriptions.Item>
                    <Descriptions.Item label="SALAIRE NET">
                      <Tag color="success" style={{ fontSize: '16px', padding: '6px 16px', fontWeight: 'bold' }}>
                        {parseFloat(record.salaire_net || 0).toLocaleString('fr-FR', { minimumFractionDigits: 2 })} DA
                      </Tag>
                    </Descriptions.Item>
                  </Descriptions>
                </Card>
              ),
            }}
          />
        </Card>
      )}
    </div>
  );
}

export default SalaireCalcul;

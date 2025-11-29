import { useState, useEffect } from 'react';
import { Table, Select, Button, message, Tag, Space, Modal, Radio, Input } from 'antd';
import { SaveOutlined, ReloadOutlined, ThunderboltOutlined, LockOutlined, UnlockOutlined, FilePdfOutlined } from '@ant-design/icons';
import { pointageService, employeService } from '../../services';

const { Option } = Select;

const currentYear = new Date().getFullYear();
const currentMonth = new Date().getMonth() + 1;

// Types de journée avec mappage vers valeurs numériques
const TYPE_JOUR = {
  'Tr': { label: 'Travaillé', color: 'green', short: 'T', value: 1 },
  'Ab': { label: 'Absent', color: 'red', short: 'A', value: 0 },
  'Co': { label: 'Congé', color: 'blue', short: 'C', value: 0 },
  'Ma': { label: 'Maladie', color: 'orange', short: 'M', value: 0 },
  'Fe': { label: 'Férié', color: 'purple', short: 'F', value: 1 },
  'Ar': { label: 'Arrêt', color: 'gray', short: 'R', value: 0 },
};

// Mappage inverse: valeur numérique vers code (pour l'affichage)
const VALUE_TO_TYPE = {
  1: 'Tr',  // Par défaut, 1 = Travaillé
  0: 'Ab',  // Par défaut, 0 = Absent
};

// Fonction pour convertir code vers valeur numérique
const codeToValue = (code) => {
  return TYPE_JOUR[code]?.value ?? null;
};

// Fonction pour convertir valeur numérique vers code (pour affichage)
//const valueToCode = (value) => {
//  if (value === null || value === undefined) return null;
//  return VALUE_TO_TYPE[value] || null;
//};
const valueToCode = (value) => {
  if (value === null || value === undefined) return null;
  const numValue = typeof value === 'string' ? parseInt(value, 10) : value;
  return VALUE_TO_TYPE[numValue] || null;
};

function GrillePointage() {
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [employes, setEmployes] = useState([]);
  const [pointages, setPointages] = useState({});
  const [filteredEmployes, setFilteredEmployes] = useState([]);
  const [filters, setFilters] = useState({
    annee: currentYear,
    mois: currentMonth,
    poste: 'tous',
    statut: 'Actif',
  });
  const [editCell, setEditCell] = useState(null);
  const [selectedType, setSelectedType] = useState('Tr');
  const [remplissageModal, setRemplissageModal] = useState(null);
  const [selectedEmployeFilter, setSelectedEmployeFilter] = useState(null);
  const [remplissageTousModal, setRemplissageTousModal] = useState(false);
  const [searchId, setSearchId] = useState('');
  const [vendredis, setVendredis] = useState([]);

  // Fonction pour calculer les vendredis du mois
  const getVendredis = (annee, mois) => {
    const nbJours = getDaysInMonth(annee, mois);
    const vendredisArray = [];
    for (let jour = 1; jour <= nbJours; jour++) {
      const date = new Date(annee, mois - 1, jour);
      if (date.getDay() === 5) { // 5 = Vendredi
        vendredisArray.push(jour);
      }
    }
    return vendredisArray;
  };

  useEffect(() => {
    loadData();
  }, [filters.annee, filters.mois, filters.statut]);

  useEffect(() => {
    filterEmployes();
  }, [employes, filters.poste, selectedEmployeFilter, searchId]);

  const loadData = async () => {
    try {
      setLoading(true);

      // Calculer les vendredis du mois
      const vendredisArray = getVendredis(filters.annee, filters.mois);
      setVendredis(vendredisArray);

      // Charger tous les employés
      const empResponse = await employeService.getAll({ statut: filters.statut });
      const emps = empResponse.data.employes || [];
      setEmployes(emps);

      // Charger tous les pointages pour la période
      const ptgResponse = await pointageService.getAll({
        annee: filters.annee,
        mois: filters.mois,
      });

      console.log('Pointages response:', ptgResponse.data);

      // Organiser les pointages par employé
      const ptgMap = {};
      const pointagesArray = ptgResponse.data.pointages || ptgResponse.data || [];

      if (Array.isArray(pointagesArray)) {
        pointagesArray.forEach(ptg => {
          ptgMap[ptg.employe_id] = ptg;
        });
      }

      // Ne PAS créer automatiquement - charger seulement ce qui existe
      // L'utilisateur créera manuellement avec le bouton "Auto" ou en cliquant
      setPointages(ptgMap);

    } catch (error) {
      message.error('Erreur lors du chargement des données');
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const filterEmployes = () => {
    let filtered = employes;

    // Filtrer par ID
    if (searchId) {
      const id = parseInt(searchId);
      if (!isNaN(id)) {
        filtered = filtered.filter(emp => emp.id === id);
      }
    }

    // Filtrer par poste
    if (filters.poste !== 'tous') {
      filtered = filtered.filter(emp => emp.poste_travail === filters.poste);
    }

    // Filtrer par employé spécifique
    if (selectedEmployeFilter) {
      filtered = filtered.filter(emp => emp.id === selectedEmployeFilter);
    }

    setFilteredEmployes(filtered);
  };

  const getPostes = () => {
    const postes = [...new Set(employes.map(emp => emp.poste_travail))];
    return postes.sort();
  };

  const getDaysInMonth = (year, month) => {
    return new Date(year, month, 0).getDate();
  };

  const handleToggleVerrouillage = async (employeId) => {
    const pointage = pointages[employeId];

    if (!pointage || !pointage.id) {
      message.warning('Veuillez d\'abord sauvegarder le pointage avant de le verrouiller');
      return;
    }

    const estVerrouille = pointage.verrouille;
    const action = estVerrouille ? 'déverrouiller' : 'verrouiller';

    Modal.confirm({
      title: `Confirmer le ${action === 'verrouiller' ? 'verrouillage' : 'déverrouillage'}`,
      content: estVerrouille
        ? 'Êtes-vous sûr de vouloir déverrouiller ce pointage ? Il pourra être modifié à nouveau.'
        : 'Êtes-vous sûr de vouloir verrouiller ce pointage ? Il ne pourra plus être modifié et sera utilisé pour le calcul des salaires.',
      okText: 'Oui',
      cancelText: 'Annuler',
      onOk: async () => {
        try {
          const response = estVerrouille
            ? await pointageService.deverrouiller(pointage.id)
            : await pointageService.verrouiller(pointage.id);

          // Mettre à jour l'état local
          setPointages(prev => ({
            ...prev,
            [employeId]: {
              ...prev[employeId],
              verrouille: !estVerrouille,
            },
          }));

          message.success(`Pointage ${estVerrouille ? 'déverrouillé' : 'verrouillé'} avec succès`);
        } catch (error) {
          console.error(`Erreur lors du ${action}:`, error);
          message.error(`Erreur lors du ${action}: ${error.response?.data?.detail || error.message}`);
        }
      },
    });
  };

  const handleVerrouillageTout = async () => {
    // Vérifier que tous les employés ont un pointage
    const employesSansPointage = [];
    const employesNonRemplis = [];
    const employesDejaNonVerrouilles = [];

    for (const emp of filteredEmployes) {
      const pointage = pointages[emp.id];

      if (!pointage || !pointage.id) {
        employesSansPointage.push(`${emp.prenom} ${emp.nom}`);
      } else if (pointage.verrouille) {
        // Déjà verrouillé, ignorer
      } else {
        // Vérifier que le pointage est rempli (au moins un jour avec une valeur)
        const nbJours = getDaysInMonth(filters.annee, filters.mois);
        let hasData = false;
        for (let i = 1; i <= nbJours; i++) {
          const jourKey = `jour_${i.toString().padStart(2, '0')}`;
          if (pointage[jourKey] !== undefined && pointage[jourKey] !== null) {
            hasData = true;
            break;
          }
        }

        if (!hasData) {
          employesNonRemplis.push(`${emp.prenom} ${emp.nom}`);
        } else {
          employesDejaNonVerrouilles.push(emp.id);
        }
      }
    }

    // Afficher les erreurs si nécessaire
    if (employesSansPointage.length > 0) {
      Modal.error({
        title: 'Pointages manquants',
        content: (
          <div>
            <p>Les employés suivants n'ont pas de pointage créé :</p>
            <ul>
              {employesSansPointage.map((nom, i) => <li key={i}>{nom}</li>)}
            </ul>
            <p>Veuillez créer leurs pointages avant de verrouiller.</p>
          </div>
        ),
      });
      return;
    }

    if (employesNonRemplis.length > 0) {
      Modal.error({
        title: 'Pointages non remplis',
        content: (
          <div>
            <p>Les employés suivants ont un pointage vide :</p>
            <ul>
              {employesNonRemplis.map((nom, i) => <li key={i}>{nom}</li>)}
            </ul>
            <p>Veuillez remplir leurs pointages avant de verrouiller.</p>
          </div>
        ),
      });
      return;
    }

    if (employesDejaNonVerrouilles.length === 0) {
      message.info('Tous les pointages sont déjà verrouillés');
      return;
    }

    // Confirmation
    Modal.confirm({
      title: 'Verrouiller tous les pointages',
      content: (
        <div>
          <p>⚠️ Vous êtes sur le point de verrouiller <strong>{employesDejaNonVerrouilles.length} pointage(s)</strong>.</p>
          <p>Une fois verrouillés, ils ne pourront plus être modifiés et seront utilisés pour le calcul des salaires.</p>
          <p>Êtes-vous sûr de vouloir continuer ?</p>
        </div>
      ),
      okText: 'Oui, verrouiller tout',
      okType: 'danger',
      cancelText: 'Annuler',
      onOk: async () => {
        let successCount = 0;
        let errorCount = 0;

        message.loading('Verrouillage en cours...', 0);

        for (const empId of employesDejaNonVerrouilles) {
          try {
            const pointage = pointages[empId];
            await pointageService.verrouiller(pointage.id);

            setPointages(prev => ({
              ...prev,
              [empId]: {
                ...prev[empId],
                verrouille: true,
              },
            }));

            successCount++;
          } catch (error) {
            console.error(`Erreur verrouillage employé ${empId}:`, error);
            errorCount++;
          }
        }

        message.destroy();
        if (errorCount === 0) {
          message.success(`✅ ${successCount} pointage(s) verrouillé(s) avec succès`);
        } else {
          message.warning(`${successCount} verrouillés, ${errorCount} erreur(s)`);
        }
      },
    });
  };

  const handleCellClick = (employeId, jour) => {
    const pointage = pointages[employeId];
    if (pointage?.verrouille) {
      message.warning('Ce pointage est verrouillé et ne peut pas être modifié');
      return;
    }
    setEditCell({ employeId, jour });
  };

  const handleTypeSelect = async () => {
    if (!editCell) return;

    try {
      const { employeId, jour } = editCell;
      const jourKey = `jour_${jour.toString().padStart(2, '0')}`;

      // Récupérer ou créer le pointage
      let pointage = pointages[employeId];

      if (!pointage) {
        // Créer un nouveau pointage localement
        pointage = {
          employe_id: employeId,
          annee: filters.annee,
          mois: filters.mois,
        };
      }

      // Mettre à jour localement avec la valeur numérique
      pointage[jourKey] = codeToValue(selectedType);

      // Mettre à jour l'état local
      setPointages(prev => ({
        ...prev,
        [employeId]: pointage,
      }));

      setEditCell(null);

    } catch (error) {
      message.error('Erreur lors de la modification');
      console.error(error);
    }
  };

  const handleRemplirEmploye = async (employeId, typeJour) => {
    try {
      const pointage = pointages[employeId];

      // Vérifier si verrouillé
      if (pointage?.verrouille) {
        message.warning('Ce pointage est verrouillé et ne peut pas être modifié');
        return;
      }

      const nbJours = getDaysInMonth(filters.annee, filters.mois);
      const employe = employes.find(e => e.id === employeId);
      const dateRecrutement = new Date(employe.date_recrutement);

      const updatedData = pointage ? { ...pointage } : {
        employe_id: employeId,
        annee: filters.annee,
        mois: filters.mois,
      };

      // Remplir tous les jours selon les règles avec valeurs numériques
      for (let jour = 1; jour <= nbJours; jour++) {
        const dateJour = new Date(filters.annee, filters.mois - 1, jour);
        const jourSemaine = dateJour.getDay();
        const jourKey = `jour_${jour.toString().padStart(2, '0')}`;

        // Avant la date de recrutement = Absent (0)
        if (dateJour < dateRecrutement) {
          updatedData[jourKey] = 0;
        }
        // Vendredi = Férié (1)
        else if (jourSemaine === 5) {
          updatedData[jourKey] = 1;
        }
        // Sinon appliquer le type demandé (convertir en valeur numérique)
        else {
          updatedData[jourKey] = codeToValue(typeJour);
        }
      }

      if (pointage && pointage.id) {
        await pointageService.update(pointage.id, updatedData);
      } else {
        const response = await pointageService.create(updatedData);
        updatedData.id = response.data.id;
      }

      setPointages(prev => ({
        ...prev,
        [employeId]: updatedData,
      }));

      message.success('Remplissage automatique effectué');
      setRemplissageModal(null);

    } catch (error) {
      message.error('Erreur lors du remplissage');
      console.error(error);
    }
  };

  const handleRemplirTous = async (typeJour) => {
    try {
      const nbJours = getDaysInMonth(filters.annee, filters.mois);
      const updates = {};
      let successCount = 0;
      let errorCount = 0;
      let skippedCount = 0;

      setRemplissageTousModal(false);
      message.loading('Remplissage en cours...', 0);

      for (const employe of filteredEmployes) {
        try {
          let pointage = pointages[employe.id];

          // Ignorer les pointages verrouillés
          if (pointage?.verrouille) {
            skippedCount++;
            continue;
          }

          const dateRecrutement = new Date(employe.date_recrutement);
          const updatedData = pointage ? { ...pointage } : {
            employe_id: employe.id,
            annee: filters.annee,
            mois: filters.mois,
          };

          // Remplir tous les jours selon les règles
          for (let jour = 1; jour <= nbJours; jour++) {
            const dateJour = new Date(filters.annee, filters.mois - 1, jour);
            const jourSemaine = dateJour.getDay();
            const jourKey = `jour_${jour.toString().padStart(2, '0')}`;

            // Avant la date de recrutement = Absent (0)
            if (dateJour < dateRecrutement) {
              updatedData[jourKey] = 0;
            }
            // Vendredi = Férié (1)
            else if (jourSemaine === 5) {
              updatedData[jourKey] = 1;
            }
            // Sinon appliquer le type demandé
            else {
              updatedData[jourKey] = codeToValue(typeJour);
            }
          }

          if (pointage && pointage.id) {
            await pointageService.update(pointage.id, updatedData);
          } else {
            const response = await pointageService.create(updatedData);
            updatedData.id = response.data.id;
          }

          updates[employe.id] = updatedData;
          successCount++;

        } catch (error) {
          console.error(`Erreur pour employé ${employe.id}:`, error);
          errorCount++;
        }
      }

      setPointages(prev => ({
        ...prev,
        ...updates,
      }));

      message.destroy();
      if (errorCount === 0 && skippedCount === 0) {
        message.success(`${successCount} employé(s) rempli(s) avec succès`);
      } else if (errorCount === 0 && skippedCount > 0) {
        message.success(`${successCount} employé(s) rempli(s), ${skippedCount} verrouillé(s) ignoré(s)`);
      } else {
        message.warning(`${successCount} succès, ${errorCount} erreur(s), ${skippedCount} verrouillés`);
      }

    } catch (error) {
      message.destroy();
      message.error('Erreur lors du remplissage massif');
      console.error(error);
    }
  };

  const handleSaveAll = async () => {
    try {
      setSaving(true);

      let successCount = 0;
      let errorCount = 0;
      let skippedCount = 0;
      const errors = [];

      // Sauvegarder tous les pointages modifiés
      for (const [employeId, pointage] of Object.entries(pointages)) {
        // Ignorer les pointages verrouillés
        if (pointage.verrouille) {
          skippedCount++;
          continue;
        }

        try {
          // Préparer les données à envoyer avec valeurs numériques
          if (pointage.id) {
            // Update - Transformer en format {jours: {1: 1, 2: 0...}}
            const joursDict = {};
            for (let i = 1; i <= 31; i++) {
              const jourKey = `jour_${i.toString().padStart(2, '0')}`;
              if (pointage[jourKey] !== undefined && pointage[jourKey] !== null) {
                joursDict[i] = pointage[jourKey]; // Déjà en format numérique
              }
            }

            const updateData = {
              jours: joursDict
            };

            console.log('Updating pointage', pointage.id, 'for employee', employeId, ':', updateData);
            await pointageService.update(pointage.id, updateData);
          } else {
            // Create - Format {employe_id, annee, mois, jour_01: 1...}
            const jourData = {};
            for (let i = 1; i <= 31; i++) {
              const jourKey = `jour_${i.toString().padStart(2, '0')}`;
              if (pointage[jourKey] !== undefined && pointage[jourKey] !== null) {
                jourData[jourKey] = pointage[jourKey]; // Déjà en format numérique
              }
            }

            const createData = {
              employe_id: parseInt(employeId),
              annee: filters.annee,
              mois: filters.mois,
              ...jourData,
            };

            console.log('Creating pointage for employee', employeId, ':', createData);
            const response = await pointageService.create(createData);
            // Mettre à jour avec l'ID reçu
            setPointages(prev => ({
              ...prev,
              [employeId]: { ...pointage, id: response.data.id },
            }));
          }
          successCount++;
        } catch (error) {
          console.error(`Erreur pour employé ${employeId}:`, error);
          console.error('Error details:', error.response?.data);
          errors.push({
            employeId,
            message: error.response?.data?.detail || error.message
          });
          errorCount++;
        }
      }

      if (errorCount === 0 && skippedCount === 0) {
        message.success(`${successCount} pointage(s) sauvegardé(s) avec succès`);
      } else if (errorCount === 0 && skippedCount > 0) {
        message.success(`${successCount} pointage(s) sauvegardé(s), ${skippedCount} verrouillé(s) ignoré(s)`);
      } else {
        const errorMsg = errors.map(e => `Employé ${e.employeId}: ${e.message}`).join('\n');
        message.error(`${successCount} sauvegardés, ${errorCount} erreur(s), ${skippedCount} verrouillés. Voir console pour détails.`);
        console.error('Errors:', errorMsg);
      }

    } catch (error) {
      message.error('Erreur lors de la sauvegarde');
      console.error(error);
    } finally {
      setSaving(false);
    }
  };

  const handleGenererRapport = async () => {
    try {
      setSaving(true);
      const response = await pointageService.getRapportMensuel(filters.annee, filters.mois);

      // Télécharger le PDF
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `pointages_${filters.mois.toString().padStart(2, '0')}_${filters.annee}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();

      message.success('Rapport généré avec succès');
    } catch (error) {
      message.error(error.response?.data?.detail || 'Erreur lors de la génération du rapport');
      console.error(error);
    } finally {
      setSaving(false);
    }
  };

  const nbJours = getDaysInMonth(filters.annee, filters.mois);

  // Colonnes du tableau
  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      fixed: 'left',
      width: 60,
      align: 'center',
    },
    {
      title: 'Employé',
      key: 'employe',
      fixed: 'left',
      width: 200,
      render: (_, record) => (
        <div>
          <div style={{ fontWeight: 'bold' }}>{record.prenom} {record.nom}</div>
          <div style={{ fontSize: '12px', color: '#666' }}>{record.poste_travail}</div>
        </div>
      ),
    },
    {
      title: 'Action',
      key: 'action',
      fixed: 'left',
      width: 80,
      render: (_, record) => {
        const pointage = pointages[record.id];
        const estVerrouille = pointage?.verrouille;

        return (
          <Button
            size="small"
            onClick={() => setRemplissageModal(record.id)}
            title="Remplissage rapide"
            disabled={estVerrouille}
          >
            Auto
          </Button>
        );
      },
    },
    {
      title: 'Statut',
      key: 'verrouille',
      fixed: 'left',
      width: 100,
      align: 'center',
      render: (_, record) => {
        const pointage = pointages[record.id];
        const estVerrouille = pointage?.verrouille;

        return (
          <Space direction="vertical" size="small" style={{ width: '100%' }}>
            <Tag
              color={estVerrouille ? 'red' : 'green'}
              icon={estVerrouille ? <LockOutlined /> : <UnlockOutlined />}
              style={{ width: '100%', textAlign: 'center' }}
            >
              {estVerrouille ? 'Verrouillé' : 'Modifiable'}
            </Tag>
            <Button
              size="small"
              type={estVerrouille ? 'default' : 'primary'}
              danger={estVerrouille}
              icon={estVerrouille ? <UnlockOutlined /> : <LockOutlined />}
              onClick={() => handleToggleVerrouillage(record.id)}
              style={{ width: '100%' }}
            >
              {estVerrouille ? 'Déverr.' : 'Verr.'}
            </Button>
          </Space>
        );
      },
    },
    ...Array.from({ length: nbJours }, (_, i) => i + 1).map(jour => {
      const estVendredi = vendredis.includes(jour);
      return {
        title: jour,
        key: `jour_${jour}`,
        width: 45,
        align: 'center',
        // Fond vert clair pour les vendredis
        onHeaderCell: () => ({
          style: { backgroundColor: estVendredi ? '#d4f4dd' : undefined }
        }),
        onCell: () => ({
          style: { backgroundColor: estVendredi ? '#f0fdf4' : undefined }
        }),
        render: (_, record) => {
          const jourKey = `jour_${jour.toString().padStart(2, '0')}`;
          const pointage = pointages[record.id];
          const valeurNum = pointage?.[jourKey];
          const estVerrouille = pointage?.verrouille;

          // Convertir valeur numérique en code pour l'affichage
          const typeJour = valueToCode(valeurNum);
          const config = TYPE_JOUR[typeJour] || { short: '-', color: 'default' };

          return (
            <Tag
              color={config.color}
              style={{
                cursor: estVerrouille ? 'not-allowed' : 'pointer',
                minWidth: '30px',
                margin: 0,
                opacity: estVerrouille ? 0.6 : 1,
              }}
              onClick={() => !estVerrouille && handleCellClick(record.id, jour)}
            >
              {config.short}
            </Tag>
          );
        },
      };
    }),
    {
      title: 'Total T',
      key: 'total_travailles',
      width: 70,
      align: 'center',
      render: (_, record) => {
        const pointage = pointages[record.id];
        if (!pointage) return 0;

        let count = 0;
        for (let i = 1; i <= 31; i++) {
          const jourKey = `jour_${i.toString().padStart(2, '0')}`;
          if (pointage[jourKey] === 1) count++;
        }
        return <Tag color="green">{count}</Tag>;
      },
    },
    {
      title: 'Total A',
      key: 'total_absents',
      width: 70,
      align: 'center',
      render: (_, record) => {
        const pointage = pointages[record.id];
        if (!pointage) return 0;

        let count = 0;
        for (let i = 1; i <= 31; i++) {
          const jourKey = `jour_${i.toString().padStart(2, '0')}`;
          if (pointage[jourKey] === 0) count++;
        }
        return <Tag color="red">{count}</Tag>;
      },
    },
  ];

  return (
    <div>
      <h2>Grille de Pointage - {filters.mois}/{filters.annee}</h2>

      <Space style={{ marginBottom: 16 }} wrap>
        <Select
          value={filters.mois}
          style={{ width: 150 }}
          onChange={(value) => setFilters({ ...filters, mois: value })}
        >
          {Array.from({ length: 12 }, (_, i) => i + 1).map(m => (
            <Option key={m} value={m}>
              {new Date(2000, m - 1).toLocaleString('fr-FR', { month: 'long' })}
            </Option>
          ))}
        </Select>

        <Select
          value={filters.annee}
          style={{ width: 120 }}
          onChange={(value) => setFilters({ ...filters, annee: value })}
        >
          {[currentYear - 1, currentYear, currentYear + 1].map(year => (
            <Option key={year} value={year}>{year}</Option>
          ))}
        </Select>

        <Input
          placeholder="Rechercher par ID"
          style={{ width: 150 }}
          value={searchId}
          onChange={(e) => setSearchId(e.target.value)}
          allowClear
        />

        <Select
          value={selectedEmployeFilter}
          style={{ width: 250 }}
          onChange={(value) => setSelectedEmployeFilter(value)}
          allowClear
          showSearch
          placeholder="Filtrer par employé"
          optionFilterProp="children"
        >
          {employes.map(emp => (
            <Option key={emp.id} value={emp.id}>
              #{emp.id} - {emp.prenom} {emp.nom}
            </Option>
          ))}
        </Select>

        <Select
          value={filters.poste}
          style={{ width: 200 }}
          onChange={(value) => setFilters({ ...filters, poste: value })}
        >
          <Option value="tous">Tous les postes</Option>
          {getPostes().map(poste => (
            <Option key={poste} value={poste}>{poste}</Option>
          ))}
        </Select>

        <Select
          value={filters.statut}
          style={{ width: 150 }}
          onChange={(value) => setFilters({ ...filters, statut: value })}
        >
          <Option value="Actif">Actifs uniquement</Option>
          <Option value="Inactif">Inactifs uniquement</Option>
          <Option value="">Tous</Option>
        </Select>

        <Button
          icon={<ReloadOutlined />}
          onClick={loadData}
        >
          Actualiser
        </Button>

        <Button
          type="default"
          icon={<ThunderboltOutlined />}
          onClick={() => setRemplissageTousModal(true)}
          style={{ background: '#52c41a', color: 'white', borderColor: '#52c41a' }}
        >
          Auto Tous
        </Button>

        <Button
          type="primary"
          icon={<SaveOutlined />}
          onClick={handleSaveAll}
          loading={saving}
        >
          Tout sauvegarder
        </Button>

        <Button
          type="primary"
          danger
          icon={<LockOutlined />}
          onClick={handleVerrouillageTout}
        >
          Verrouiller Tout
        </Button>

        <Button
          icon={<FilePdfOutlined />}
          onClick={handleGenererRapport}
          loading={saving}
        >
          Rapport PDF
        </Button>
      </Space>

      <div style={{ marginBottom: 16, padding: 8, background: '#f5f5f5', borderRadius: 4 }}>
        <Space wrap>
          <span style={{ fontWeight: 'bold' }}>Légende:</span>
          {Object.entries(TYPE_JOUR).map(([key, config]) => (
            <Tag key={key} color={config.color}>
              {config.short} = {config.label}
            </Tag>
          ))}
        </Space>
      </div>

      <Table
        loading={loading}
        columns={columns}
        dataSource={filteredEmployes}
        rowKey="id"
        scroll={{ x: 'max-content' }}
        pagination={{
          pageSize: 50,
          showSizeChanger: true,
          pageSizeOptions: ['10', '20', '50', '100'],
          showTotal: (total) => `Total: ${total} employés`,
        }}
        bordered
        size="small"
      />

      <Modal
        title="Sélectionner le type de journée"
        open={!!editCell}
        onOk={handleTypeSelect}
        onCancel={() => setEditCell(null)}
        okText="Valider"
        cancelText="Annuler"
      >
        {editCell && (
          <div>
            <p>
              Jour {editCell.jour} - {
                employes.find(e => e.id === editCell.employeId)?.prenom
              } {
                employes.find(e => e.id === editCell.employeId)?.nom
              }
            </p>
            <Radio.Group
              value={selectedType}
              onChange={(e) => setSelectedType(e.target.value)}
              style={{ width: '100%' }}
            >
              <Space direction="vertical" style={{ width: '100%' }}>
                {Object.entries(TYPE_JOUR).map(([key, config]) => (
                  <Radio key={key} value={key}>
                    <Tag color={config.color}>{config.label}</Tag>
                  </Radio>
                ))}
              </Space>
            </Radio.Group>
          </div>
        )}
      </Modal>

      <Modal
        title="Remplissage automatique"
        open={!!remplissageModal}
        onCancel={() => setRemplissageModal(null)}
        footer={null}
      >
        {remplissageModal && (
          <div>
            <p style={{ marginBottom: 16 }}>
              <strong>
                {employes.find(e => e.id === remplissageModal)?.prenom}{' '}
                {employes.find(e => e.id === remplissageModal)?.nom}
              </strong>
            </p>
            <p style={{ fontSize: '12px', color: '#666', marginBottom: 16 }}>
              Remplir automatiquement avec les règles suivantes :
              <br />• Jours avant recrutement : Absent
              <br />• Vendredis : Férié (Travaillé)
              <br />• Jour de recrutement et après : Type sélectionné
            </p>
            <Space direction="vertical" style={{ width: '100%' }}>
              <Button
                type="primary"
                block
                onClick={() => handleRemplirEmploye(remplissageModal, 'Tr')}
              >
                <Tag color="green">Travaillé</Tag> Remplir en "Travaillé"
              </Button>
              <Button
                block
                onClick={() => handleRemplirEmploye(remplissageModal, 'Ab')}
              >
                <Tag color="red">Absent</Tag> Remplir en "Absent"
              </Button>
              <Button
                block
                onClick={() => handleRemplirEmploye(remplissageModal, 'Co')}
              >
                <Tag color="blue">Congé</Tag> Remplir en "Congé"
              </Button>
            </Space>
          </div>
        )}
      </Modal>

      <Modal
        title="Remplissage automatique - Tous les employés"
        open={remplissageTousModal}
        onCancel={() => setRemplissageTousModal(false)}
        footer={null}
        width={500}
      >
        <div>
          <p style={{ marginBottom: 16 }}>
            <strong>
              Vous allez remplir automatiquement {filteredEmployes.length} employé(s)
            </strong>
          </p>
          <p style={{ fontSize: '12px', color: '#666', marginBottom: 16 }}>
            Remplir automatiquement avec les règles suivantes :
            <br />• Jours avant recrutement : Absent
            <br />• Vendredis : Férié (Travaillé)
            <br />• Jour de recrutement et après : Type sélectionné
            <br /><br />
            <span style={{ color: '#ff4d4f', fontWeight: 'bold' }}>
              ⚠️ Cette opération va remplacer tous les pointages existants pour la période sélectionnée.
            </span>
          </p>
          <Space direction="vertical" style={{ width: '100%' }}>
            <Button
              type="primary"
              block
              onClick={() => handleRemplirTous('Tr')}
              icon={<ThunderboltOutlined />}
            >
              <Tag color="green">Travaillé</Tag> Remplir tous en "Travaillé"
            </Button>
            <Button
              block
              onClick={() => handleRemplirTous('Ab')}
              icon={<ThunderboltOutlined />}
            >
              <Tag color="red">Absent</Tag> Remplir tous en "Absent"
            </Button>
            <Button
              block
              onClick={() => handleRemplirTous('Co')}
              icon={<ThunderboltOutlined />}
            >
              <Tag color="blue">Congé</Tag> Remplir tous en "Congé"
            </Button>
          </Space>
        </div>
      </Modal>
    </div>
  );
}

export default GrillePointage;

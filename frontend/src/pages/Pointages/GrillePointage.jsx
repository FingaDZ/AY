import { useState, useEffect } from 'react';
import { Table, Select, Button, message, Tag, Space, Modal, Radio } from 'antd';
import { SaveOutlined, ReloadOutlined } from '@ant-design/icons';
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
const valueToCode = (value) => {
  if (value === null || value === undefined) return null;
  return VALUE_TO_TYPE[value] || null;
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

  useEffect(() => {
    loadData();
  }, [filters.annee, filters.mois, filters.statut]);

  useEffect(() => {
    filterEmployes();
  }, [employes, filters.poste, selectedEmployeFilter]);

  const loadData = async () => {
    try {
      setLoading(true);
      
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
      
      // Créer automatiquement les pointages manquants avec jours pré-remplis
      for (const emp of emps) {
        if (!ptgMap[emp.id]) {
          // Créer un pointage avec valeurs par défaut
          const newPointage = await creerPointageAutomatique(emp);
          ptgMap[emp.id] = newPointage;
        }
      }
      
      setPointages(ptgMap);
      
    } catch (error) {
      message.error('Erreur lors du chargement des données');
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const creerPointageAutomatique = async (employe) => {
    const nbJours = getDaysInMonth(filters.annee, filters.mois);
    const dateRecrutement = new Date(employe.date_recrutement);
    const moisCourant = new Date(filters.annee, filters.mois - 1, 1);
    
    const pointageData = {
      employe_id: employe.id,
      annee: filters.annee,
      mois: filters.mois,
    };
    
    // Remplir les jours automatiquement avec valeurs numériques
    for (let jour = 1; jour <= nbJours; jour++) {
      const dateJour = new Date(filters.annee, filters.mois - 1, jour);
      const jourSemaine = dateJour.getDay(); // 0=Dimanche, 5=Vendredi
      const jourKey = `jour_${jour.toString().padStart(2, '0')}`;
      
      // Avant la date de recrutement = Absent (0)
      if (dateJour < dateRecrutement) {
        pointageData[jourKey] = 0;
      }
      // Vendredi = Férié (1)
      else if (jourSemaine === 5) {
        pointageData[jourKey] = 1;
      }
      // Jour de recrutement et après = Travaillé (1)
      else {
        pointageData[jourKey] = 1;
      }
    }
    
    try {
      const response = await pointageService.create(pointageData);
      return response.data;
    } catch (error) {
      console.error('Erreur création pointage auto:', error);
      return pointageData;
    }
  };

  const filterEmployes = () => {
    let filtered = employes;
    
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

  const handleCellClick = (employeId, jour) => {
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
      const nbJours = getDaysInMonth(filters.annee, filters.mois);
      const employe = employes.find(e => e.id === employeId);
      const dateRecrutement = new Date(employe.date_recrutement);
      
      let pointage = pointages[employeId];
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

  const handleSaveAll = async () => {
    try {
      setSaving(true);
      
      let successCount = 0;
      let errorCount = 0;
      const errors = [];
      
      // Sauvegarder tous les pointages modifiés
      for (const [employeId, pointage] of Object.entries(pointages)) {
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
      
      if (errorCount === 0) {
        message.success(`${successCount} pointage(s) sauvegardé(s) avec succès`);
      } else {
        const errorMsg = errors.map(e => `Employé ${e.employeId}: ${e.message}`).join('\n');
        message.error(`${successCount} sauvegardés, ${errorCount} erreur(s). Voir console pour détails.`);
        console.error('Errors:', errorMsg);
      }
      
    } catch (error) {
      message.error('Erreur lors de la sauvegarde');
      console.error(error);
    } finally {
      setSaving(false);
    }
  };

  const nbJours = getDaysInMonth(filters.annee, filters.mois);

  // Colonnes du tableau
  const columns = [
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
      render: (_, record) => (
        <Button
          size="small"
          onClick={() => setRemplissageModal(record.id)}
          title="Remplissage rapide"
        >
          Auto
        </Button>
      ),
    },
    ...Array.from({ length: nbJours }, (_, i) => i + 1).map(jour => ({
      title: jour,
      key: `jour_${jour}`,
      width: 45,
      align: 'center',
      render: (_, record) => {
        const jourKey = `jour_${jour.toString().padStart(2, '0')}`;
        const pointage = pointages[record.id];
        const valeurNum = pointage?.[jourKey];
        
        // Convertir valeur numérique en code pour l'affichage
        const typeJour = valueToCode(valeurNum);
        const config = TYPE_JOUR[typeJour] || { short: '-', color: 'default' };
        
        return (
          <Tag
            color={config.color}
            style={{ 
              cursor: 'pointer', 
              minWidth: '30px',
              margin: 0,
            }}
            onClick={() => handleCellClick(record.id, jour)}
          >
            {config.short}
          </Tag>
        );
      },
    })),
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
              {emp.prenom} {emp.nom} - {emp.poste_travail}
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
          type="primary"
          icon={<SaveOutlined />}
          onClick={handleSaveAll}
          loading={saving}
        >
          Tout sauvegarder
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
          pageSize: 20,
          showSizeChanger: true,
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
              <br />• Vendredis : Férié
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
    </div>
  );
}

export default GrillePointage;

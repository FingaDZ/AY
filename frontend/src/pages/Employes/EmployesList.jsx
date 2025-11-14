import { useState, useEffect } from 'react';
import { Table, Button, Space, Input, Select, Tag, message, Modal, Tooltip } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, SearchOutlined, FilePdfOutlined, ExclamationCircleOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { employeService } from '../../services';
import { format } from 'date-fns';

const { Search } = Input;
const { Option } = Select;

function EmployesList() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [employes, setEmployes] = useState([]);
  const [filters, setFilters] = useState({
    statut: '',
    recherche: '',
  });

  useEffect(() => {
    loadEmployes();
  }, [filters]);

  const loadEmployes = async () => {
    try {
      setLoading(true);
      const params = {};
      if (filters.statut) params.statut = filters.statut;
      if (filters.recherche) params.search = filters.recherche;

      const response = await employeService.getAll(params);
      setEmployes(response.data.employes || []);
    } catch (error) {
      message.error('Erreur lors du chargement des employés');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteClick = async (employe) => {
    try {
      // Vérifier si l'employé peut être supprimé
      const checkResponse = await employeService.checkCanDelete(employe.id);
      const { can_delete, has_data } = checkResponse.data;

      if (can_delete) {
        // Aucun enregistrement - suppression directe
        Modal.confirm({
          title: 'Supprimer cet employé ?',
          icon: <ExclamationCircleOutlined />,
          content: `Êtes-vous sûr de vouloir supprimer définitivement ${employe.nom} ${employe.prenom} ?`,
          okText: 'Supprimer',
          okType: 'danger',
          cancelText: 'Annuler',
          onOk: async () => {
            try {
              await employeService.delete(employe.id);
              message.success('Employé supprimé avec succès');
              loadEmployes();
            } catch (error) {
              message.error('Erreur lors de la suppression');
              console.error(error);
            }
          },
        });
      } else {
        // L'employé a des enregistrements - afficher modal avec option de désactivation
        const hasPointages = has_data.pointages;
        
        let detailsMessage = `${employe.nom} ${employe.prenom} possède des pointages enregistrés dans la base de données.\n\n`;
        detailsMessage += 'Cet employé ne peut pas être supprimé pour préserver l\'intégrité du système.';

        Modal.confirm({
          title: 'Impossible de supprimer',
          icon: <ExclamationCircleOutlined style={{ color: '#faad14' }} />,
          content: (
            <div>
              <p style={{ whiteSpace: 'pre-line', marginBottom: 16 }}>{detailsMessage}</p>
              <p style={{ fontWeight: 'bold' }}>
                Voulez-vous désactiver cet employé à la place ?
              </p>
              <p style={{ fontSize: 12, color: '#666' }}>
                La désactivation permettra de conserver l'historique tout en masquant l'employé des listes actives.
              </p>
            </div>
          ),
          okText: 'Désactiver',
          okType: 'primary',
          cancelText: 'Annuler',
          onOk: async () => {
            try {
              await employeService.deactivate(employe.id);
              message.success('Employé désactivé avec succès');
              loadEmployes();
            } catch (error) {
              if (error.response?.status === 400) {
                message.warning(error.response.data.detail);
              } else {
                message.error('Erreur lors de la désactivation');
              }
              console.error(error);
            }
          },
        });
      }
    } catch (error) {
      message.error('Erreur lors de la vérification');
      console.error(error);
    }
  };

  const handleGenererRapport = async () => {
    try {
      setLoading(true);
      const now = new Date();
      const annee = now.getFullYear();
      const mois = now.getMonth() + 1;
      
      const response = await employeService.getRapportActifs(annee, mois);
      
      // Télécharger le PDF
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `employes_actifs_${mois.toString().padStart(2, '0')}_${annee}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      message.success('Rapport généré avec succès');
    } catch (error) {
      message.error('Erreur lors de la génération du rapport');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 60,
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
      title: 'N° ANEM',
      dataIndex: 'numero_anem',
      key: 'numero_anem',
      render: (value) => value || '-',
    },
    {
      title: 'Poste',
      dataIndex: 'poste_travail',
      key: 'poste_travail',
    },
    {
      title: 'Salaire Base',
      dataIndex: 'salaire_base',
      key: 'salaire_base',
      render: (value) => `${parseFloat(value).toLocaleString('fr-FR')} DA`,
    },
    {
      title: 'Date Recrutement',
      dataIndex: 'date_recrutement',
      key: 'date_recrutement',
      render: (date) => format(new Date(date), 'dd/MM/yyyy'),
    },
    {
      title: 'Statut',
      dataIndex: 'statut_contrat',
      key: 'statut_contrat',
      render: (statut) => (
        <Tag color={statut === 'Actif' ? 'green' : 'red'}>
          {statut}
        </Tag>
      ),
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => navigate(`/employes/${record.id}`)}
          >
            Modifier
          </Button>
          <Tooltip title="Supprimer">
            <Button
              type="link"
              danger
              icon={<DeleteOutlined />}
              onClick={() => handleDeleteClick(record)}
            />
          </Tooltip>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <h2>Liste des Employés</h2>
        <Space>
          <Button
            icon={<FilePdfOutlined />}
            onClick={handleGenererRapport}
            loading={loading}
          >
            Rapport PDF
          </Button>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => navigate('/employes/nouveau')}
          >
            Nouvel Employé
          </Button>
        </Space>
      </div>

      <Space style={{ marginBottom: 16 }} size="middle">
        <Search
          placeholder="Rechercher par nom, prénom..."
          allowClear
          style={{ width: 300 }}
          onChange={(e) => setFilters({ ...filters, recherche: e.target.value })}
          onSearch={(value) => setFilters({ ...filters, recherche: value })}
        />
        <Select
          placeholder="Filtrer par statut"
          style={{ width: 200 }}
          allowClear
          onChange={(value) => setFilters({ ...filters, statut: value || '' })}
        >
          <Option value="Actif">Actif</Option>
          <Option value="Inactif">Inactif</Option>
        </Select>
      </Space>

      <Table
        loading={loading}
        columns={columns}
        dataSource={employes}
        rowKey="id"
        pagination={{
          pageSize: 10,
          showSizeChanger: true,
          showTotal: (total) => `Total: ${total} employés`,
        }}
      />
    </div>
  );
}

export default EmployesList;

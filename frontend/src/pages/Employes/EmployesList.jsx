import { useState, useEffect } from 'react';
import { Table, Button, Space, Input, Select, Tag, message, Popconfirm } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, SearchOutlined, FilePdfOutlined } from '@ant-design/icons';
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
      if (filters.recherche) params.recherche = filters.recherche;

      const response = await employeService.getAll(params);
      setEmployes(response.data.employes || []);
    } catch (error) {
      message.error('Erreur lors du chargement des employés');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    try {
      await employeService.delete(id);
      message.success('Employé supprimé avec succès');
      loadEmployes();
    } catch (error) {
      message.error('Erreur lors de la suppression');
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
          <Popconfirm
            title="Êtes-vous sûr de vouloir supprimer cet employé ?"
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

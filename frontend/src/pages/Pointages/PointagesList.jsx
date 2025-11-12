import { useState, useEffect } from 'react';
import { Table, Button, Select, InputNumber, message, Space, Tag } from 'antd';
import { PlusOutlined, EditOutlined, LockOutlined, CopyOutlined, TableOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { pointageService } from '../../services';

const { Option } = Select;

const currentYear = new Date().getFullYear();
const currentMonth = new Date().getMonth() + 1;

function PointagesList() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [pointages, setPointages] = useState([]);
  const [filters, setFilters] = useState({
    annee: currentYear,
    mois: currentMonth,
  });

  useEffect(() => {
    loadPointages();
  }, [filters]);

  const loadPointages = async () => {
    try {
      setLoading(true);
      const response = await pointageService.getAll(filters);
      console.log('Pointages loaded:', response.data);
      setPointages(Array.isArray(response.data) ? response.data : []);
    } catch (error) {
      message.error('Erreur lors du chargement des pointages');
      console.error('Error loading pointages:', error);
      setPointages([]);
    } finally {
      setLoading(false);
    }
  };

  const calculateTotals = (pointage) => {
    let travailles = 0, absents = 0, conges = 0, maladies = 0, feries = 0, arrets = 0;
    
    for (let i = 1; i <= 31; i++) {
      const jour = pointage[`jour_${i.toString().padStart(2, '0')}`];
      if (jour === 'Tr') travailles++;
      else if (jour === 'Ab') absents++;
      else if (jour === 'Co') conges++;
      else if (jour === 'Ma') maladies++;
      else if (jour === 'Fe') feries++;
      else if (jour === 'Ar') arrets++;
    }

    return { travailles, absents, conges, maladies, feries, arrets };
  };

  const columns = [
    {
      title: 'Employé ID',
      dataIndex: 'employe_id',
      key: 'employe_id',
      width: 100,
    },
    {
      title: 'Mois/Année',
      key: 'periode',
      render: (_, record) => `${record.mois}/${record.annee}`,
      width: 120,
    },
    {
      title: 'Travaillés',
      key: 'travailles',
      render: (_, record) => {
        const totals = calculateTotals(record);
        return <Tag color="green">{totals.travailles}</Tag>;
      },
      width: 100,
    },
    {
      title: 'Absents',
      key: 'absents',
      render: (_, record) => {
        const totals = calculateTotals(record);
        return <Tag color="red">{totals.absents}</Tag>;
      },
      width: 100,
    },
    {
      title: 'Congés',
      key: 'conges',
      render: (_, record) => {
        const totals = calculateTotals(record);
        return <Tag color="blue">{totals.conges}</Tag>;
      },
      width: 100,
    },
    {
      title: 'Statut',
      key: 'verrouille',
      render: (_, record) => (
        record.verrouille ? 
          <Tag icon={<LockOutlined />} color="warning">Verrouillé</Tag> : 
          <Tag color="default">Modifiable</Tag>
      ),
      width: 120,
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => navigate(`/pointages/${record.id}`)}
          >
            Modifier
          </Button>
        </Space>
      ),
    },
  ];

  const monthOptions = [
    { value: 1, label: 'Janvier' },
    { value: 2, label: 'Février' },
    { value: 3, label: 'Mars' },
    { value: 4, label: 'Avril' },
    { value: 5, label: 'Mai' },
    { value: 6, label: 'Juin' },
    { value: 7, label: 'Juillet' },
    { value: 8, label: 'Août' },
    { value: 9, label: 'Septembre' },
    { value: 10, label: 'Octobre' },
    { value: 11, label: 'Novembre' },
    { value: 12, label: 'Décembre' },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <h2>Pointages Mensuels</h2>
        <Space>
          <Button
            icon={<TableOutlined />}
            onClick={() => navigate('/pointages/grille')}
          >
            Vue Grille
          </Button>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => navigate('/pointages/nouveau')}
          >
            Nouveau Pointage
          </Button>
        </Space>
      </div>

      <Space style={{ marginBottom: 16 }} size="middle">
        <Select
          value={filters.mois}
          style={{ width: 150 }}
          onChange={(value) => setFilters({ ...filters, mois: value })}
        >
          {monthOptions.map(month => (
            <Option key={month.value} value={month.value}>{month.label}</Option>
          ))}
        </Select>
        <InputNumber
          value={filters.annee}
          style={{ width: 120 }}
          min={2000}
          max={2100}
          placeholder="Année"
          onChange={(value) => setFilters({ ...filters, annee: value || currentYear })}
        />
      </Space>

      <Table
        loading={loading}
        columns={columns}
        dataSource={pointages}
        rowKey="id"
        pagination={{
          pageSize: 10,
          showSizeChanger: true,
          showTotal: (total) => `Total: ${total} pointages`,
        }}
      />
    </div>
  );
}

export default PointagesList;

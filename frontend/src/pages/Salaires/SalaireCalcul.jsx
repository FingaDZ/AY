import { useState, useEffect } from 'react';
import { Card, Select, Button, Table, message, Spin, Descriptions } from 'antd';
import { CalculatorOutlined } from '@ant-design/icons';
import { salaireService, employeService } from '../../services';

const { Option } = Select;

const currentYear = new Date().getFullYear();
const currentMonth = new Date().getMonth() + 1;

function SalaireCalcul() {
  const [loading, setLoading] = useState(false);
  const [calculating, setCalculating] = useState(false);
  const [employes, setEmployes] = useState([]);
  const [salaires, setSalaires] = useState([]);
  const [filters, setFilters] = useState({
    annee: currentYear,
    mois: currentMonth,
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
    try {
      setCalculating(true);
      const response = await salaireService.calculerTous(filters);
      setSalaires(response.data.salaires || []);
      message.success('Salaires calculés avec succès');
    } catch (error) {
      message.error('Erreur lors du calcul des salaires');
      console.error(error);
    } finally {
      setCalculating(false);
    }
  };

  const columns = [
    {
      title: 'Employé',
      key: 'employe',
      render: (_, record) => {
        const emp = employes.find(e => e.id === record.employe_id);
        return emp ? `${emp.prenom} ${emp.nom}` : record.employe_id;
      }
    },
    {
      title: 'Salaire Base',
      dataIndex: 'salaire_base_proratis',
      key: 'salaire_base',
      render: (val) => `${parseFloat(val || 0).toLocaleString('fr-FR')} DA`
    },
    {
      title: 'Total Indemnités',
      key: 'indemnites',
      render: (_, record) => {
        const total = (parseFloat(record.in || 0) + 
                      parseFloat(record.ifsp || 0) + 
                      parseFloat(record.iep || 0) +
                      parseFloat(record.prime_encouragement || 0));
        return `${total.toLocaleString('fr-FR')} DA`;
      }
    },
    {
      title: 'IRG',
      dataIndex: 'irg',
      key: 'irg',
      render: (val) => `${parseFloat(val || 0).toLocaleString('fr-FR')} DA`
    },
    {
      title: 'Retenue SS',
      dataIndex: 'retenue_secu_sociale',
      key: 'retenue_ss',
      render: (val) => `${parseFloat(val || 0).toLocaleString('fr-FR')} DA`
    },
    {
      title: 'Salaire Net',
      dataIndex: 'salaire_net',
      key: 'salaire_net',
      render: (val) => (
        <span style={{ fontWeight: 'bold', color: '#52c41a' }}>
          {parseFloat(val || 0).toLocaleString('fr-FR')} DA
        </span>
      )
    },
  ];

  return (
    <div>
      <h2>Calcul des Salaires</h2>

      <Card style={{ marginBottom: 16 }}>
        <div style={{ display: 'flex', gap: 16, alignItems: 'center' }}>
          <span>Période:</span>
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
          <Select
            value={filters.annee}
            style={{ width: 120 }}
            onChange={(value) => setFilters({ ...filters, annee: value })}
          >
            {[currentYear - 1, currentYear, currentYear + 1].map(year => (
              <Option key={year} value={year}>{year}</Option>
            ))}
          </Select>
          <Button
            type="primary"
            icon={<CalculatorOutlined />}
            onClick={handleCalculer}
            loading={calculating}
          >
            Calculer Tous les Salaires
          </Button>
        </div>
      </Card>

      {calculating ? (
        <div style={{ textAlign: 'center', padding: 50 }}>
          <Spin size="large" />
          <p>Calcul en cours...</p>
        </div>
      ) : (
        <Table
          columns={columns}
          dataSource={salaires}
          rowKey={(record) => record.employe_id}
          pagination={false}
          expandable={{
            expandedRowRender: (record) => (
              <Descriptions bordered size="small" column={2}>
                <Descriptions.Item label="Salaire Base Proratisé">
                  {parseFloat(record.salaire_base_proratis || 0).toLocaleString('fr-FR')} DA
                </Descriptions.Item>
                <Descriptions.Item label="Heures Supplémentaires">
                  {parseFloat(record.heures_supplementaires || 0).toLocaleString('fr-FR')} DA
                </Descriptions.Item>
                <Descriptions.Item label="IN (5%)">
                  {parseFloat(record.in || 0).toLocaleString('fr-FR')} DA
                </Descriptions.Item>
                <Descriptions.Item label="IFSP (5%)">
                  {parseFloat(record.ifsp || 0).toLocaleString('fr-FR')} DA
                </Descriptions.Item>
                <Descriptions.Item label="IEP">
                  {parseFloat(record.iep || 0).toLocaleString('fr-FR')} DA
                </Descriptions.Item>
                <Descriptions.Item label="Prime Encouragement">
                  {parseFloat(record.prime_encouragement || 0).toLocaleString('fr-FR')} DA
                </Descriptions.Item>
                <Descriptions.Item label="Prime Chauffeur">
                  {parseFloat(record.prime_chauffeur || 0).toLocaleString('fr-FR')} DA
                </Descriptions.Item>
                <Descriptions.Item label="Prime Déplacement">
                  {parseFloat(record.prime_deplacement || 0).toLocaleString('fr-FR')} DA
                </Descriptions.Item>
                <Descriptions.Item label="Panier">
                  {parseFloat(record.panier || 0).toLocaleString('fr-FR')} DA
                </Descriptions.Item>
                <Descriptions.Item label="Prime Transport">
                  {parseFloat(record.prime_transport || 0).toLocaleString('fr-FR')} DA
                </Descriptions.Item>
                <Descriptions.Item label="Retenue Sécurité Sociale">
                  {parseFloat(record.retenue_secu_sociale || 0).toLocaleString('fr-FR')} DA
                </Descriptions.Item>
                <Descriptions.Item label="IRG">
                  {parseFloat(record.irg || 0).toLocaleString('fr-FR')} DA
                </Descriptions.Item>
                <Descriptions.Item label="Avances">
                  {parseFloat(record.total_avances || 0).toLocaleString('fr-FR')} DA
                </Descriptions.Item>
                <Descriptions.Item label="Crédits">
                  {parseFloat(record.total_credits || 0).toLocaleString('fr-FR')} DA
                </Descriptions.Item>
                <Descriptions.Item label="Salaire Brut" span={2}>
                  <span style={{ fontWeight: 'bold' }}>
                    {parseFloat(record.salaire_brut || 0).toLocaleString('fr-FR')} DA
                  </span>
                </Descriptions.Item>
                <Descriptions.Item label="Salaire Net" span={2}>
                  <span style={{ fontWeight: 'bold', color: '#52c41a', fontSize: 16 }}>
                    {parseFloat(record.salaire_net || 0).toLocaleString('fr-FR')} DA
                  </span>
                </Descriptions.Item>
              </Descriptions>
            ),
          }}
        />
      )}
    </div>
  );
}

export default SalaireCalcul;

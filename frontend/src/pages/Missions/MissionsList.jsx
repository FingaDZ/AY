import { useState, useEffect } from 'react';
import { Table, Button, DatePicker, Select, message, Modal, Form, InputNumber, Space, Popconfirm, Card } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, PrinterOutlined, FilterOutlined } from '@ant-design/icons';
import { missionService, employeService, clientService } from '../../services';
import MissionFormEnhanced from '../../components/MissionFormEnhanced';
import dayjs from 'dayjs';

const { Option } = Select;
const { RangePicker } = DatePicker;

function MissionsList() {
  const [loading, setLoading] = useState(false);
  const [missions, setMissions] = useState([]);
  const [employes, setEmployes] = useState([]);
  const [clients, setClients] = useState([]);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingMission, setEditingMission] = useState(null);
  const [tarifKm, setTarifKm] = useState(15.5);
  const [filters, setFilters] = useState({});
  const [totaux, setTotaux] = useState([]);
  const [form] = Form.useForm();

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [missionsRes, employesRes, clientsRes, tarifRes, totauxRes] = await Promise.all([
        missionService.getAll(filters),
        employeService.getAll({ statut: 'Actif' }),
        clientService.getAll(),
        missionService.getTarifKm(),
        missionService.getTotauxChauffeur(filters),
      ]);

      setMissions(missionsRes.data.missions || []);
      setEmployes(employesRes.data.employes || []);
      setClients(clientsRes.data.clients || []);
      setTarifKm(tarifRes.data.valeur);
      setTotaux(totauxRes.data.totaux || []);
    } catch (error) {
      message.error('Erreur lors du chargement');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (values) => {
    try {
      const missionData = {
        ...values,
        date_mission: values.date_mission.format('YYYY-MM-DD'),
      };

      if (editingMission) {
        await missionService.update(editingMission.id, missionData);
        message.success('Mission modifiée avec succès');
      } else {
        await missionService.create(missionData);
        message.success('Mission créée avec succès');
      }

      setModalVisible(false);
      setEditingMission(null);
      form.resetFields();
      loadData();
    } catch (error) {
      message.error(editingMission ? 'Erreur lors de la modification' : 'Erreur lors de la création');
    }
  };

  const handleEdit = (record) => {
    setEditingMission(record);
    form.setFieldsValue({
      date_mission: dayjs(record.date_mission),
      chauffeur_id: record.chauffeur_id,
      client_id: record.client_id,
    });
    setModalVisible(true);
  };

  const handleDelete = async (id) => {
    try {
      await missionService.delete(id);
      message.success('Mission supprimée avec succès');
      loadData();
    } catch (error) {
      message.error('Erreur lors de la suppression');
    }
  };

  const handleDownloadOrdreMission = async (missionId) => {
    try {
      const response = await missionService.getOrdreMissionPdf(missionId);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `ordre_mission_${missionId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      message.success('Ordre de mission téléchargé');
    } catch (error) {
      message.error('Erreur lors du téléchargement');
    }
  };

  const handleDownloadRapport = async () => {
    try {
      const response = await missionService.getRapportPdf(filters);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'rapport_missions.pdf');
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      message.success('Rapport téléchargé');
    } catch (error) {
      message.error('Erreur lors du téléchargement du rapport');
    }
  };

  const columns = [
    { title: 'Date', dataIndex: 'date_mission', key: 'date_mission' },
    {
      title: 'Chauffeur',
      dataIndex: 'chauffeur_id',
      key: 'chauffeur_id',
      render: (id) => {
        const emp = employes.find(e => e.id === id);
        return emp ? `${emp.prenom} ${emp.nom}` : id;
      }
    },
    {
      title: 'Client',
      dataIndex: 'client_id',
      key: 'client_id',
      render: (id) => {
        const cli = clients.find(c => c.id === id);
        return cli ? `${cli.prenom} ${cli.nom}` : id;
      }
    },
    {
      title: 'Distance (km)',
      dataIndex: 'distance',
      key: 'distance',
      render: (val) => `${parseFloat(val).toFixed(2)} km`
    },
    {
      title: 'Tarif/km',
      dataIndex: 'tarif_km',
      key: 'tarif_km',
      render: (val) => `${parseFloat(val).toFixed(2)} DA`
    },
    {
      title: 'Prime',
      dataIndex: 'prime_calculee',
      key: 'prime_calculee',
      render: (val) => `${parseFloat(val).toLocaleString('fr-FR')} DA`
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            Modifier
          </Button>
          <Popconfirm
            title="Êtes-vous sûr de vouloir supprimer cette mission ?"
            onConfirm={() => handleDelete(record.id)}
            okText="Oui"
            cancelText="Non"
          >
            <Button type="link" danger icon={<DeleteOutlined />}>
              Supprimer
            </Button>
          </Popconfirm>
          <Button
            type="link"
            icon={<PrinterOutlined />}
            onClick={() => handleDownloadOrdreMission(record.id)}
          >
            Ordre
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <h2>Ordres de Mission</h2>
        <div>
          <span style={{ marginRight: 16 }}>Tarif/km: {tarifKm} DA</span>
          {missions.length > 0 && (
            <Button
              icon={<PrinterOutlined />}
              onClick={handleDownloadRapport}
              style={{ marginRight: 8 }}
            >
              Rapport PDF
            </Button>
          )}
          <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalVisible(true)}>
            Nouvelle Mission
          </Button>
        </div>
      </div>

      <Card style={{ marginBottom: 16 }}>
        <Space wrap style={{ width: '100%' }}>
          <RangePicker
            format="DD/MM/YYYY"
            placeholder={['Date début', 'Date fin']}
            onChange={(dates) => {
              if (dates) {
                setFilters({
                  ...filters,
                  date_debut: dates[0].format('YYYY-MM-DD'),
                  date_fin: dates[1].format('YYYY-MM-DD')
                });
              } else {
                const { date_debut, date_fin, ...rest } = filters;
                setFilters(rest);
              }
            }}
          />
          <Select
            placeholder="Tous les chauffeurs"
            style={{ width: 200 }}
            allowClear
            onChange={(value) => {
              if (value) {
                setFilters({ ...filters, chauffeur_id: value });
              } else {
                const { chauffeur_id, ...rest } = filters;
                setFilters(rest);
              }
            }}
          >
            {employes
              .filter(e => e.poste_travail.toLowerCase().includes('chauffeur'))
              .map(emp => (
                <Option key={emp.id} value={emp.id}>
                  {emp.prenom} {emp.nom}
                </Option>
              ))}
          </Select>
          <Select
            placeholder="Tous les clients"
            style={{ width: 200 }}
            allowClear
            onChange={(value) => {
              if (value) {
                setFilters({ ...filters, client_id: value });
              } else {
                const { client_id, ...rest } = filters;
                setFilters(rest);
              }
            }}
          >
            {clients.map(cli => (
              <Option key={cli.id} value={cli.id}>
                {cli.prenom} {cli.nom}
              </Option>
            ))}
          </Select>
          <Button
            type="primary"
            icon={<FilterOutlined />}
            onClick={loadData}
          >
            Filtrer
          </Button>
          <Button
            onClick={() => {
              setFilters({});
              loadData();
            }}
          >
            Réinitialiser
          </Button>
        </Space>
      </Card>

      {totaux.length > 0 && (
        <Card title="Totaux par Chauffeur" style={{ marginBottom: 16 }}>
          <Table
            dataSource={totaux}
            rowKey="chauffeur_id"
            pagination={false}
            size="small"
            columns={[
              {
                title: 'Chauffeur',
                dataIndex: 'nom_complet',
                key: 'nom_complet',
              },
              {
                title: 'Nombre de missions',
                dataIndex: 'nombre_missions',
                key: 'nombre_missions',
              },
              {
                title: 'Distance totale (km)',
                dataIndex: 'total_distance',
                key: 'total_distance',
                render: (val) => val.toFixed(2),
              },
              {
                title: 'Primes totales (DA)',
                dataIndex: 'total_primes',
                key: 'total_primes',
                render: (val) => val.toFixed(2),
              },
            ]}
          />
        </Card>
      )}

      <Table
        loading={loading}
        columns={columns}
        dataSource={missions}
        rowKey="id"
        pagination={{ pageSize: 10 }}
      />

      <Modal
        title={editingMission ? "Modifier Mission" : "Nouvelle Mission"}
        open={modalVisible}
        onCancel={() => {
          setModalVisible(false);
          setEditingMission(null);
          form.resetFields();
        }}
        footer={null}
        width={800}
      >
        <MissionFormEnhanced
          visible={modalVisible}
          onCancel={() => {
            setModalVisible(false);
            setEditingMission(null);
            form.resetFields();
          }}
          onSuccess={() => {
            setModalVisible(false);
            setEditingMission(null);
            form.resetFields();
            loadData();
          }}
          editingMission={editingMission}
          employes={employes}
          clients={clients}
        />
      </Modal>
    </div>
  );
}

export default MissionsList;

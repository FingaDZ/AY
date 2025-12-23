import { useState, useEffect } from 'react';
import { Table, Button, Space, Input, Select, Tag, message, Modal, Tooltip, Avatar, Card, Typography } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, SearchOutlined, FilePdfOutlined, ExclamationCircleOutlined, CheckCircleOutlined, FileTextOutlined, SafetyCertificateOutlined, FileProtectOutlined, UserOutlined, CloudSyncOutlined, FileExcelOutlined, DownloadOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { employeService, attendanceService } from '../../services';
import { format } from 'date-fns';
import ResponsiveTable from '../../components/Common/ResponsiveTable';
import useResponsive from '../../hooks/useResponsive';

const { Search } = Input;
const { Option } = Select;
const { Text } = Typography;

function EmployesList() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [employes, setEmployes] = useState([]);
  const [syncingAll, setSyncingAll] = useState(false);
  const [filters, setFilters] = useState({
    statut: 'Actif',
    recherche: '',
  });
  const { isMobile } = useResponsive();

  useEffect(() => {
    loadEmployes();
  }, [filters]);

  const loadEmployes = async () => {
    try {
      setLoading(true);
      const params = {};
      if (filters.statut) params.statut = filters.statut;
      if (filters.recherche) params.search = filters.recherche;

      // Inclure les inactifs si le filtre "Inactif" ou "Tous" est sélectionné
      if (filters.statut === 'Inactif' || filters.statut === '') {
        params.inclure_inactifs = true;
      }

      const response = await employeService.getAll(params);
      setEmployes(response.data.employes || []);
    } catch (error) {
      message.error('Erreur lors du chargement des employés');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  // Calculer le statut d'expiration du contrat
  const getContractStatus = (dateFin) => {
    if (!dateFin) return { status: 'none', daysRemaining: null, color: '' };
    
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const contractEnd = new Date(dateFin);
    contractEnd.setHours(0, 0, 0, 0);
    
    const diffTime = contractEnd - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays < 0) {
      return { status: 'expired', daysRemaining: diffDays, color: 'red' };
    } else if (diffDays <= 30) {
      return { status: 'expiring', daysRemaining: diffDays, color: 'orange' };
    } else {
      return { status: 'valid', daysRemaining: diffDays, color: 'green' };
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

  const handleReactivateClick = async (employe) => {
    Modal.confirm({
      title: 'Réactiver cet employé ?',
      icon: <CheckCircleOutlined style={{ color: '#52c41a' }} />,
      content: (
        <div>
          <p>Êtes-vous sûr de vouloir réactiver <strong>{employe.nom} {employe.prenom}</strong> ?</p>
          <p style={{ fontSize: 12, color: '#666', marginTop: 8 }}>
            L'employé redeviendra actif et visible dans les listes.
          </p>
        </div>
      ),
      okText: 'Réactiver',
      okType: 'primary',
      cancelText: 'Annuler',
      onOk: async () => {
        try {
          await employeService.reactivate(employe.id);
          message.success('Employé réactivé avec succès');
          loadEmployes();
        } catch (error) {
          if (error.response?.status === 400) {
            message.warning(error.response.data.detail);
          } else {
            message.error('Erreur lors de la réactivation');
          }
          console.error(error);
        }
      },
    });
  };

  const handleExportExcel = async () => {
    try {
      setLoading(true);
      const response = await employeService.exportExcel();

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      const today = new Date();
      const dateStr = `${today.getDate().toString().padStart(2, '0')}${(today.getMonth() + 1).toString().padStart(2, '0')}${today.getFullYear()}`;
      link.setAttribute('download', `employes_export_${dateStr}.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.remove();

      message.success('Export Excel réussi');
    } catch (error) {
      message.error('Erreur lors de l\'export Excel');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleExportCsv = async () => {
    try {
      setLoading(true);
      const response = await employeService.exportCsv();

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      const today = new Date();
      const dateStr = `${today.getDate().toString().padStart(2, '0')}${(today.getMonth() + 1).toString().padStart(2, '0')}${today.getFullYear()}`;
      link.setAttribute('download', `employes_export_${dateStr}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();

      message.success('Export CSV réussi');
    } catch (error) {
      message.error('Erreur lors de l\'export CSV');
      console.error(error);
    } finally {
      setLoading(false);
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

  const handleGenerateAttestation = async (employe) => {
    try {
      setLoading(true);
      const response = await employeService.generateAttestation(employe.id);

      // Télécharger le PDF
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      const today = new Date();
      const dateStr = `${today.getDate().toString().padStart(2, '0')}${(today.getMonth() + 1).toString().padStart(2, '0')}${today.getFullYear()}`;
      link.setAttribute('download', `attestation_travail_${employe.nom}_${employe.prenom}_${dateStr}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();

      message.success('Attestation de travail générée avec succès');
    } catch (error) {
      const errorMsg = error.response?.data?.detail || 'Erreur lors de la génération de l\'attestation';
      message.error(errorMsg);
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateCertificat = async (employe) => {
    try {
      setLoading(true);
      const response = await employeService.generateCertificat(employe.id);

      // Télécharger le PDF
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      const today = new Date();
      const dateStr = `${today.getDate().toString().padStart(2, '0')}${(today.getMonth() + 1).toString().padStart(2, '0')}${today.getFullYear()}`;
      link.setAttribute('download', `certificat_travail_${employe.nom}_${employe.prenom}_${dateStr}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();

      message.success('Certificat de travail généré avec succès');
    } catch (error) {
      const errorMsg = error.response?.data?.detail || 'Erreur lors de la génération du certificat';
      message.error(errorMsg);
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateContrat = async (employe) => {
    try {
      setLoading(true);
      const response = await employeService.generateContrat(employe.id);

      // Télécharger le PDF
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      const today = new Date();
      const dateStr = `${today.getDate().toString().padStart(2, '0')}${(today.getMonth() + 1).toString().padStart(2, '0')}${today.getFullYear()}`;
      link.setAttribute('download', `contrat_travail_${employe.nom}_${employe.prenom}_${dateStr}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();

      message.success('Contrat de travail généré avec succès');
    } catch (error) {
      const errorMsg = error.response?.data?.detail || 'Erreur lors de la génération du contrat';
      message.error(errorMsg);
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
      render: (text, record, index) => index + 1,
      responsive: ['md'],
    },
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 60,
      responsive: ['lg'],
    },
    {
      title: 'Nom',
      dataIndex: 'nom',
      key: 'nom',
      sorter: (a, b) => a.nom.localeCompare(b.nom),
      responsive: ['md'],
    },
    {
      title: 'Prénom',
      dataIndex: 'prenom',
      key: 'prenom',
      sorter: (a, b) => a.prenom.localeCompare(b.prenom),
      responsive: ['md'],
    },
    {
      title: 'Employé',
      key: 'fullname',
      responsive: ['xs', 'sm'],
      render: (_, record) => (
        <Space direction="vertical" size={0}>
          <Text strong>{record.nom} {record.prenom}</Text>
          <Text type="secondary" style={{ fontSize: 12 }}>{record.poste_travail}</Text>
        </Space>
      ),
    },
    {
      title: 'N° ANEM',
      dataIndex: 'numero_anem',
      key: 'numero_anem',
      render: (value) => value || '-',
      responsive: ['lg'],
    },
    {
      title: 'Poste',
      dataIndex: 'poste_travail',
      key: 'poste_travail',
      responsive: ['md'],
    },
    {
      title: 'Salaire Base',
      dataIndex: 'salaire_base',
      key: 'salaire_base',
      render: (value) => `${parseFloat(value).toLocaleString('fr-FR')} DA`,
      responsive: ['lg'],
    },
    {
      title: 'Date Recrutement',
      dataIndex: 'date_recrutement',
      key: 'date_recrutement',
      render: (date) => format(new Date(date), 'dd/MM/yyyy'),
      responsive: ['lg'],
    },
    {
      title: 'Fin Contrat',
      dataIndex: 'date_fin_contrat',
      key: 'date_fin_contrat',
      render: (date, record) => {
        if (!date) return '-';
        const contractStatus = getContractStatus(date);
        const formattedDate = format(new Date(date), 'dd/MM/yyyy');
        
        let tagColor = 'default';
        let statusText = '';
        
        if (contractStatus.status === 'expired') {
          tagColor = 'red';
          statusText = 'Expiré';
        } else if (contractStatus.status === 'expiring') {
          tagColor = 'orange';
          statusText = `${contractStatus.daysRemaining}j restants`;
        } else {
          tagColor = 'green';
          statusText = `${contractStatus.daysRemaining}j restants`;
        }
        
        return (
          <Space direction="vertical" size={0}>
            <Text style={{ fontSize: 12 }}>{formattedDate}</Text>
            <Tag color={tagColor} style={{ margin: 0, fontSize: 11 }}>
              {statusText}
            </Tag>
          </Space>
        );
      },
      responsive: ['lg'],
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
      width: isMobile ? undefined : 300,
      fixed: isMobile ? false : 'right',
      render: (_, record) => (
        <Space size="small" wrap>
          <Tooltip title="Modifier">
            <Button
              type="link"
              icon={<EditOutlined />}
              onClick={() => navigate(`/employes/${record.id}`)}
              size="small"
            >
              {isMobile && 'Modifier'}
            </Button>
          </Tooltip>

          {record.statut_contrat === 'Actif' ? (
            <>
              <Tooltip title="Attestation">
                <Button
                  type="link"
                  icon={<FileTextOutlined />}
                  onClick={() => handleGenerateAttestation(record)}
                  size="small"
                  style={{ color: '#1890ff' }}
                />
              </Tooltip>
              <Tooltip title="Contrat">
                <Button
                  type="link"
                  icon={<FileProtectOutlined />}
                  onClick={() => handleGenerateContrat(record)}
                  size="small"
                  style={{ color: '#722ed1' }}
                />
              </Tooltip>
              <Tooltip title="Supprimer">
                <Button
                  type="link"
                  danger
                  icon={<DeleteOutlined />}
                  onClick={() => handleDeleteClick(record)}
                  size="small"
                />
              </Tooltip>
            </>
          ) : (
            <>
              <Tooltip title="Certificat">
                <Button
                  type="link"
                  icon={<SafetyCertificateOutlined />}
                  onClick={() => handleGenerateCertificat(record)}
                  size="small"
                  style={{ color: '#52c41a' }}
                />
              </Tooltip>
              <Tooltip title="Contrat">
                <Button
                  type="link"
                  icon={<FileProtectOutlined />}
                  onClick={() => handleGenerateContrat(record)}
                  size="small"
                  style={{ color: '#722ed1' }}
                />
              </Tooltip>
              <Tooltip title="Réactiver">
                <Button
                  type="link"
                  style={{ color: '#52c41a' }}
                  icon={<CheckCircleOutlined />}
                  onClick={() => handleReactivateClick(record)}
                  size="small"
                />
              </Tooltip>
            </>
          )}
        </Space>
      ),
    },
  ];

  // Rendu mobile personnalisé
  const mobileRenderItem = (employe) => (
    <Card
      size="small"
      style={{ marginBottom: 12 }}
      hoverable
    >
      <Space direction="vertical" style={{ width: '100%' }} size="small">
        <Space>
          <Avatar size={48} icon={<UserOutlined />} />
          <div>
            <Text strong>{employe.nom} {employe.prenom}</Text>
            <br />
            <Text type="secondary" style={{ fontSize: 12 }}>{employe.poste_travail}</Text>
          </div>
          <Tag color={employe.statut_contrat === 'Actif' ? 'green' : 'red'}>
            {employe.statut_contrat}
          </Tag>
        </Space>

        <Space wrap size="small" style={{ width: '100%', justifyContent: 'flex-start' }}>
          <Button
            type="primary"
            size="small"
            icon={<EditOutlined />}
            onClick={() => navigate(`/employes/${employe.id}`)}
          >
            Modifier
          </Button>
          {employe.statut_contrat === 'Actif' ? (
            <>
              <Button
                size="small"
                icon={<FileTextOutlined />}
                onClick={() => handleGenerateAttestation(employe)}
                style={{ color: '#1890ff' }}
              >
                Attestation
              </Button>
              <Button
                size="small"
                icon={<FileProtectOutlined />}
                onClick={() => handleGenerateContrat(employe)}
                style={{ color: '#722ed1' }}
              >
                Contrat
              </Button>
              <Button
                size="small"
                danger
                icon={<DeleteOutlined />}
                onClick={() => handleDeleteClick(employe)}
              >
                Supprimer
              </Button>
            </>
          ) : (
            <>
              <Button
                size="small"
                icon={<SafetyCertificateOutlined />}
                onClick={() => handleGenerateCertificat(employe)}
                style={{ color: '#52c41a' }}
              >
                Certificat
              </Button>
              <Button
                size="small"
                icon={<FileProtectOutlined />}
                onClick={() => handleGenerateContrat(employe)}
                style={{ color: '#722ed1' }}
              >
                Contrat
              </Button>
              <Button
                size="small"
                icon={<CheckCircleOutlined />}
                onClick={() => handleReactivateClick(employe)}
                style={{ color: '#52c41a' }}
              >
                Réactiver
              </Button>
            </>
          )}
        </Space>
      </Space>
    </Card>
  );

  return (
    <div>
      <style>{`
        .contract-expired {
          background-color: #ffebee !important;
        }
        .contract-expired:hover {
          background-color: #ffcdd2 !important;
        }
        .contract-expiring {
          background-color: #fff3e0 !important;
        }
        .contract-expiring:hover {
          background-color: #ffe0b2 !important;
        }
      `}</style>
      <div style={{
        display: 'flex',
        flexDirection: isMobile ? 'column' : 'row',
        justifyContent: 'space-between',
        marginBottom: 16,
        gap: isMobile ? 12 : 0
      }}>
        <h2 style={{ margin: 0 }}>Liste des Employés</h2>
        <Space direction={isMobile ? 'vertical' : 'horizontal'} style={{ width: isMobile ? '100%' : 'auto' }}>
          <Button
            icon={<CloudSyncOutlined />}
            onClick={async () => {
              try {
                setSyncingAll(true);
                const response = await attendanceService.syncAllEmployees();
                message.success(`${response.data.synced} employés synchronisés`);
                if (response.data.not_found > 0) {
                  message.info(`${response.data.not_found} non trouvés`);
                }
              } catch (error) {
                message.error('Erreur sync');
              } finally {
                setSyncingAll(false);
              }
            }}
            loading={syncingAll}
            block={isMobile}
          >
            Sync Attendance
          </Button>
          <Button
            icon={<FilePdfOutlined />}
            onClick={handleGenererRapport}
            loading={loading}
            block={isMobile}
          >
            Rapport PDF
          </Button>
          <Button
            icon={<FileExcelOutlined />}
            onClick={handleExportExcel}
            loading={loading}
            block={isMobile}
            style={{ color: '#217346', borderColor: '#217346' }}
          >
            Export Excel
          </Button>
          <Button
            icon={<DownloadOutlined />}
            onClick={handleExportCsv}
            loading={loading}
            block={isMobile}
          >
            Export CSV
          </Button>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => navigate('/employes/nouveau')}
            block={isMobile}
          >
            Nouvel Employé
          </Button>
        </Space>
      </div>

      <Space
        direction={isMobile ? 'vertical' : 'horizontal'}
        style={{ marginBottom: 16, width: isMobile ? '100%' : 'auto' }}
        size="middle"
      >
        <Search
          placeholder="Rechercher par nom, prénom..."
          allowClear
          style={{ width: isMobile ? '100%' : 300 }}
          onChange={(e) => setFilters({ ...filters, recherche: e.target.value })}
          onSearch={(value) => setFilters({ ...filters, recherche: value })}
        />
        <Select
          placeholder="Filtrer par statut"
          style={{ width: isMobile ? '100%' : 200 }}
          allowClear
          onChange={(value) => setFilters({ ...filters, statut: value || '' })}
          defaultValue="Actif"
        >
          <Option value="Actif">Actif</Option>
          <Option value="Inactif">Inactif</Option>
          <Option value="">Tous</Option>
        </Select>
      </Space>

      <ResponsiveTable
        loading={loading}
        columns={columns}
        dataSource={employes}
        rowKey="id"
        mobileRenderItem={mobileRenderItem}
        rowClassName={(record) => {
          if (!record.date_fin_contrat) return '';
          const contractStatus = getContractStatus(record.date_fin_contrat);
          if (contractStatus.status === 'expired') return 'contract-expired';
          if (contractStatus.status === 'expiring') return 'contract-expiring';
          return '';
        }}
        pagination={{
          pageSize: isMobile ? 10 : 10,
          showSizeChanger: !isMobile,
          showTotal: (total) => `Total: ${total} employés`,
        }}
      />
    </div>
  );
}

export default EmployesList;

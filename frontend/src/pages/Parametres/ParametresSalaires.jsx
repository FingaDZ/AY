import { useState, useEffect } from 'react';
import { Card, Form, InputNumber, Switch, Select, Button, message, Spin, Divider, Alert, Row, Col, Typography, Upload } from 'antd';
import { SaveOutlined, ReloadOutlined, UploadOutlined, FileExcelOutlined } from '@ant-design/icons';
import { parametresSalaireService } from '../../services';

const { Title, Text } = Typography;
const { Option } = Select;

function ParametresSalaires() {
    const [form] = Form.useForm();
    const [loading, setLoading] = useState(false);
    const [saving, setSaving] = useState(false);
    const [uploading, setUploading] = useState(false);
    const [parametres, setParametres] = useState(null);

    useEffect(() => {
        loadParametres();
    }, []);

    const loadParametres = async () => {
        try {
            setLoading(true);
            const response = await parametresSalaireService.getParametres();
            setParametres(response.data);
            form.setFieldsValue(response.data);
        } catch (error) {
            message.error('Erreur lors du chargement des paramètres');
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    const handleSave = async () => {
        try {
            setSaving(true);
            const values = await form.validateFields();

            const response = await parametresSalaireService.updateParametres(values);
            setParametres(response.data);

            message.success('Paramètres sauvegardés avec succès');
        } catch (error) {
            if (error.errorFields) {
                message.error('Veuillez corriger les erreurs dans le formulaire');
            } else {
                message.error('Erreur lors de la sauvegarde');
                console.error(error);
            }
        } finally {
            setSaving(false);
        }
    };

    const handleUploadIRG = async (file) => {
        const formData = new FormData();
        formData.append('file', file);

        try {
            setUploading(true);
            await parametresSalaireService.importerIRGBareme(formData);
            message.success('Barème IRG importé avec succès');
        } catch (error) {
            message.error("Erreur lors de l'import : " + (error.response?.data?.detail || error.message));
        } finally {
            setUploading(false);
        }
        return false; // Empêcher l'upload automatique par antd
    };

    const handleReset = () => {
        if (parametres) {
            form.setFieldsValue(parametres);
            message.info('Formulaire réinitialisé');
        }
    };

    if (loading) {
        return (
            <div style={{ textAlign: 'center', padding: 50 }}>
                <Spin size="large" />
                <p>Chargement des paramètres...</p>
            </div>
        );
    }

    return (
        <div>
            <Title level={2}>Paramètres de Calcul des Salaires</Title>

            <Alert
                message="Important"
                description="Ces paramètres affectent TOUS les calculs de salaire futurs. Modifiez-les avec précaution."
                type="warning"
                showIcon
                style={{ marginBottom: 24 }}
            />

            <Form
                form={form}
                layout="vertical"
                onFinish={handleSave}
            >
                {/* INDEMNITÉS */}
                <Card
                    title="Indemités (%)"
                    style={{ marginBottom: 16 }}
                    extra={
                        <Text type="secondary">Appliquées sur le salaire de base</Text>
                    }
                >
                    <Row gutter={16}>
                        <Col span={8}>
                            <Form.Item
                                label="IN - Indemité de Nuisance (%)"
                                name="taux_in"
                                rules={[
                                    { required: true, message: 'Requis' },
                                    { type: 'number', min: 0, max: 100, message: '0-100%' }
                                ]}
                            >
                                <InputNumber
                                    min={0}
                                    max={100}
                                    step={0.1}
                                    style={{ width: '100%' }}
                                    addonAfter="%"
                                />
                            </Form.Item>
                        </Col>
                        <Col span={8}>
                            <Form.Item
                                label="IFSP - Service Permanent (%)"
                                name="taux_ifsp"
                                rules={[
                                    { required: true, message: 'Requis' },
                                    { type: 'number', min: 0, max: 100, message: '0-100%' }
                                ]}
                            >
                                <InputNumber
                                    min={0}
                                    max={100}
                                    step={0.1}
                                    style={{ width: '100%' }}
                                    addonAfter="%"
                                />
                            </Form.Item>
                        </Col>
                        <Col span={8}>
                            <Form.Item
                                label="IEP - Expérience Prof. (% par an)"
                                name="taux_iep_par_an"
                                rules={[
                                    { required: true, message: 'Requis' },
                                    { type: 'number', min: 0, max: 100, message: '0-100%' }
                                ]}
                                tooltip="1% = 1% du salaire par année d'ancienneté"
                            >
                                <InputNumber
                                    min={0}
                                    max={100}
                                    step={0.1}
                                    style={{ width: '100%' }}
                                    addonAfter="%"
                                />
                            </Form.Item>
                        </Col>
                    </Row>

                    <Row gutter={16}>
                        <Col span={12}>
                            <Form.Item
                                label="Prime d'Encouragement (%)"
                                name="taux_prime_encouragement"
                                rules={[
                                    { required: true, message: 'Requis' },
                                    { type: 'number', min: 0, max: 100, message: '0-100%' }
                                ]}
                            >
                                <InputNumber
                                    min={0}
                                    max={100}
                                    step={0.1}
                                    style={{ width: '100%' }}
                                    addonAfter="%"
                                />
                            </Form.Item>
                        </Col>
                        <Col span={12}>
                            <Form.Item
                                label="Ancienneté minimum pour Prime Encouragement (années)"
                                name="anciennete_min_encouragement"
                                rules={[
                                    { required: true, message: 'Requis' },
                                    { type: 'number', min: 0, message: '≥ 0' }
                                ]}
                            >
                                <InputNumber
                                    min={0}
                                    style={{ width: '100%' }}
                                    addonAfter="ans"
                                />
                            </Form.Item>
                        </Col>
                    </Row>
                </Card>

                {/* PRIMES FIXES */}
                <Card title="Primes Fixes (DA)" style={{ marginBottom: 16 }}>
                    <Row gutter={16}>
                        <Col span={8}>
                            <Form.Item
                                label="Prime Chauffeur (par jour)"
                                name="prime_chauffeur_jour"
                                rules={[
                                    { required: true, message: 'Requis' },
                                    { type: 'number', min: 0, message: '≥ 0' }
                                ]}
                            >
                                <InputNumber
                                    min={0}
                                    step={10}
                                    style={{ width: '100%' }}
                                    addonAfter="DA/j"
                                />
                            </Form.Item>
                        </Col>
                        <Col span={8}>
                            <Form.Item
                                label="Prime Nuit Sécurité (mensuelle)"
                                name="prime_nuit_securite"
                                rules={[
                                    { required: true, message: 'Requis' },
                                    { type: 'number', min: 0, message: '≥ 0' }
                                ]}
                            >
                                <InputNumber
                                    min={0}
                                    step={50}
                                    style={{ width: '100%' }}
                                    addonAfter="DA/mois"
                                />
                            </Form.Item>
                        </Col>
                        <Col span={8}>
                            <Form.Item
                                label="Prime Femme au Foyer"
                                name="prime_femme_foyer"
                                rules={[
                                    { required: true, message: 'Requis' },
                                    { type: 'number', min: 0, message: '≥ 0' }
                                ]}
                            >
                                <InputNumber
                                    min={0}
                                    step={100}
                                    style={{ width: '100%' }}
                                    addonAfter="DA"
                                />
                            </Form.Item>
                        </Col>
                    </Row>

                    <Row gutter={16}>
                        <Col span={12}>
                            <Form.Item
                                label="Panier (par jour)"
                                name="panier_jour"
                                rules={[
                                    { required: true, message: 'Requis' },
                                    { type: 'number', min: 0, message: '≥ 0' }
                                ]}
                            >
                                <InputNumber
                                    min={0}
                                    step={10}
                                    style={{ width: '100%' }}
                                    addonAfter="DA/j"
                                />
                            </Form.Item>
                        </Col>
                        <Col span={12}>
                            <Form.Item
                                label="Transport (par jour)"
                                name="transport_jour"
                                rules={[
                                    { required: true, message: 'Requis' },
                                    { type: 'number', min: 0, message: '≥ 0' }
                                ]}
                            >
                                <InputNumber
                                    min={0}
                                    step={10}
                                    style={{ width: '100%' }}
                                    addonAfter="DA/j"
                                />
                            </Form.Item>
                        </Col>
                    </Row>
                </Card>

                {/* RETENUES */}
                <Card title="Retenues" style={{ marginBottom: 16 }}>
                    <Row gutter={16}>
                        <Col span={12}>
                            <Form.Item
                                label="Taux Sécurité Sociale (%)"
                                name="taux_securite_sociale"
                                rules={[
                                    { required: true, message: 'Requis' },
                                    { type: 'number', min: 0, max: 100, message: '0-100%' }
                                ]}
                            >
                                <InputNumber
                                    min={0}
                                    max={100}
                                    step={0.1}
                                    style={{ width: '100%' }}
                                    addonAfter="%"
                                />
                            </Form.Item>
                        </Col>
                    </Row>
                </Card>

                {/* OPTIONS DE CALCUL */}
                <Card title="Options de Calcul" style={{ marginBottom: 16 }}>
                    <Row gutter={16}>
                        <Col span={8}>
                            <Form.Item
                                label="Mode de Calcul des Congés"
                                name="mode_calcul_conges"
                                rules={[{ required: true, message: 'Requis' }]}
                                tooltip="Complet = Salaire complet même avec congés | Proratiser = 2 parts séparées | Hybride = Base 26j"
                            >
                                <Select>
                                    <Option value="complet">Complet (Salaire total)</Option>
                                    <Option value="proratise">Proratiser</Option>
                                    <Option value="hybride">Hybride</Option>
                                </Select>
                            </Form.Item>
                        </Col>
                        <Col span={8}>
                            <Form.Item
                                label="Jours Ouvrables par Mois"
                                name="jours_ouvrables_base"
                                rules={[
                                    { required: true, message: 'Requis' },
                                    { type: 'number', min: 1, max: 31, message: '1-31' }
                                ]}
                            >
                                <InputNumber
                                    min={1}
                                    max={31}
                                    style={{ width: '100%' }}
                                    addonAfter="jours"
                                />
                            </Form.Item>
                        </Col>
                    </Row>

                    <Divider />

                    <Row gutter={16}>
                        <Col span={12}>
                            <Form.Item
                                label="Calculer Heures Supplémentaires"
                                name="calculer_heures_supp"
                                valuePropName="checked"
                                tooltip="Si désactivé, les heures supplémentaires ne seront pas calculées"
                            >
                                <Switch />
                            </Form.Item>
                        </Col>
                        <Col span={12}>
                            <Form.Item
                                label="IRG Proratiser selon Jours Travaillés"
                                name="irg_proratise"
                                valuePropName="checked"
                                tooltip="Recommandé : Adapter l'IRG au nombre de jours réellement travaillés"
                            >
                                <Switch />
                            </Form.Item>
                        </Col>
                    </Row>
                </Card>

                {/* BARÈME IRG */}
                <Card title="Barème IRG" style={{ marginBottom: 16 }}>
                    <div style={{ textAlign: 'center', marginBottom: 16 }}>
                        <Text type="secondary">
                            Importez le fichier irg.xlsx (colonnes : MONTANT, IRG) pour mettre à jour le barème de calcul.
                        </Text>
                    </div>
                    <Upload.Dragger
                        name="file"
                        multiple={false}
                        beforeUpload={handleUploadIRG}
                        showUploadList={false}
                        accept=".xlsx,.xls"
                    >
                        <p className="ant-upload-drag-icon">
                            <FileExcelOutlined style={{ color: '#52c41a' }} />
                        </p>
                        <p className="ant-upload-text">Cliquez ou glissez le fichier IRG ici</p>
                        <p className="ant-upload-hint">
                            Supporte uniquement les fichiers Excel (.xlsx)
                        </p>
                    </Upload.Dragger>

                    {uploading && (
                        <div style={{ marginTop: 16, textAlign: 'center' }}>
                            <Spin /> Importation en cours...
                        </div>
                    )}
                </Card>

                {/* BOUTONS */}
                <Card>
                    <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 16 }}>
                        <Button
                            icon={<ReloadOutlined />}
                            onClick={handleReset}
                            disabled={saving}
                        >
                            Réinitialiser
                        </Button>
                        <Button
                            type="primary"
                            icon={<SaveOutlined />}
                            htmlType="submit"
                            loading={saving}
                            size="large"
                        >
                            Sauvegarder les Paramètres
                        </Button>
                    </div>
                </Card>
            </Form>
        </div>
    );
}

export default ParametresSalaires;


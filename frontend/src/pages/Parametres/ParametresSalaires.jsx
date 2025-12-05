import { useState, useEffect } from 'react';
import { Card, Form, InputNumber, Switch, Select, Button, message, Spin, Divider, Alert, Row, Col, Typography } from 'antd';
import { SaveOutlined, ReloadOutlined } from '@ant-design/icons';
import { parametresSalaireService } from '../../services';

const { Title, Text } = Typography;
const { Option } = Select;

function ParametresSalaires() {
    const [form] = Form.useForm();
    const [loading, setLoading] = useState(false);
    const [saving, setSaving] = useState(false);
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

            message.success('Paramètres sauvegard\u00e9s avec succ\u00e8s');
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

    const handleReset = () => {
        if (parametres) {
            form.setFieldsValue(parametres);
            message.info('Formulaire r\u00e9initialis\u00e9');
        }
    };

    if (loading) {
        return (
            <div style={{ textAlign: 'center', padding: 50 }}>
                <Spin size="large" />
                <p>Chargement des param\u00e8tres...</p>
            </div>
        );
    }

    return (
        <div>
            <Title level={2}>Param\u00e8tres de Calcul des Salaires</Title>

            <Alert
                message="Important"
                description="Ces param\u00e8tres affectent TOUS les calculs de salaire futurs. Modifiez-les avec pr\u00e9caution."
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
                    title="Indemit\u00e9s (%)"
                    style={{ marginBottom: 16 }}
                    extra={
                        <Text type="secondary">Appliqu\u00e9es sur le salaire de base</Text>
                    }
                >
                    <Row gutter={16}>
                        <Col span={8}>
                            <Form.Item
                                label="IN - Indemit\u00e9 de Nuisance (%)"
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
                                label="IEP - Exp\u00e9rience Prof. (% par an)"
                                name="taux_iep_par_an"
                                rules={[
                                    { required: true, message: 'Requis' },
                                    { type: 'number', min: 0, max: 100, message: '0-100%' }
                                ]}
                                tooltip="1% = 1% du salaire par ann\u00e9e d'anciennet\u00e9"
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
                                label="Anciennet\u00e9 minimum pour Prime Encouragement (ann\u00e9es)"
                                name="anciennete_min_encouragement"
                                rules={[
                                    { required: true, message: 'Requis' },
                                    { type: 'number', min: 0, message: '\u2265 0' }
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
                                    { type: 'number', min: 0, message: '\u2265 0' }
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
                                label="Prime Nuit S\u00e9curit\u00e9 (mensuelle)"
                                name="prime_nuit_securite"
                                rules={[
                                    { required: true, message: 'Requis' },
                                    { type: 'number', min: 0, message: '\u2265 0' }
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
                                    { type: 'number', min: 0, message: '\u2265 0' }
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
                                    { type: 'number', min: 0, message: '\u2265 0' }
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
                                    { type: 'number', min: 0, message: '\u2265 0' }
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
                                label="Taux S\u00e9curit\u00e9 Sociale (%)"
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
                                label="Mode de Calcul des Cong\u00e9s"
                                name="mode_calcul_conges"
                                rules={[{ required: true, message: 'Requis' }]}
                                tooltip="Complet = Salaire complet m\u00eame avec cong\u00e9s | Proratiser = 2 parts s\u00e9par\u00e9es | Hybride = Base 26j"
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
                                label="Calculer Heures Suppl\u00e9mentaires"
                                name="calculer_heures_supp"
                                valuePropName="checked"
                                tooltip="Si d\u00e9sactiv\u00e9, les heures suppl\u00e9mentaires ne seront pas calcul\u00e9es"
                            >
                                <Switch />
                            </Form.Item>
                        </Col>
                        <Col span={12}>
                            <Form.Item
                                label="IRG Proratiser selon Jours Travaill\u00e9s"
                                name="irg_proratise"
                                valuePropName="checked"
                                tooltip="Recommand\u00e9 : Adapter l'IRG au nombre de jours r\u00e9ellement travaill\u00e9s"
                            >
                                <Switch />
                            </Form.Item>
                        </Col>
                    </Row>
                </Card>

                {/* BOUTONS */}
                <Card>
                    <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 16 }}>
                        <Button
                            icon={<ReloadOutlined />}
                            onClick={handleReset}
                            disabled={saving}
                        >
                            R\u00e9initialiser
                        </Button>
                        <Button
                            type="primary"
                            icon={<SaveOutlined />}
                            htmlType="submit"
                            loading={saving}
                            size="large"
                        >
                            Sauvegarder les Param\u00e8tres
                        </Button>
                    </div>
                </Card>
            </Form>
        </div>
    );
}

export default ParametresSalaires;

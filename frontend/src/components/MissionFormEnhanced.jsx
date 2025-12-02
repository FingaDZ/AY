import React, { useState, useEffect } from 'react';
import { Form, DatePicker, Select, Button, Card, InputNumber, Input, Space, Divider, message } from 'antd';
import { PlusOutlined, MinusCircleOutlined } from '@ant-design/icons';
import axios from 'axios';
import dayjs from 'dayjs';

const { Option } = Select;
const { TextArea } = Input;

const MissionFormEnhanced = ({ visible, onCancel, onSuccess, editingMission, employes, clients }) => {
    const [form] = Form.useForm();
    const [logisticsTypes, setLogisticsTypes] = useState([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        fetchLogisticsTypes();
    }, []);

    useEffect(() => {
        if (editingMission) {
            form.setFieldsValue({
                date_mission: dayjs(editingMission.date_mission),
                chauffeur_id: editingMission.chauffeur_id,
                clients: editingMission.client_details?.map(detail => ({
                    client_id: detail.client_id,
                    montant_encaisse: detail.montant_encaisse,
                    statut_versement: detail.statut_versement,
                    observations: detail.observations,
                    logistics: detail.logistics_movements?.map(mov => ({
                        logistics_type_id: mov.logistics_type_id,
                        quantity_out: mov.quantity_out,
                        quantity_in: mov.quantity_in
                    })) || []
                })) || []
            });
        } else {
            form.resetFields();
        }
    }, [editingMission, form]);

    const fetchLogisticsTypes = async () => {
        try {
            const response = await axios.get('/api/logistics-types');
            setLogisticsTypes(response.data);
        } catch (error) {
            message.error('Erreur lors du chargement des types logistiques');
        }
    };

    const handleSubmit = async (values) => {
        try {
            setLoading(true);
            const missionData = {
                date_mission: values.date_mission.format('YYYY-MM-DD'),
                chauffeur_id: values.chauffeur_id,
                client_id: values.clients?.[0]?.client_id || null, // Legacy support
                clients: values.clients || []
            };

            const url = editingMission
                ? `/api/missions/${editingMission.id}`
                : '/api/missions';

            const method = editingMission ? 'put' : 'post';

            await axios[method](url, missionData);

            message.success(editingMission ? 'Mission modifiée avec succès' : 'Mission créée avec succès');
            form.resetFields();
            onSuccess();
        } catch (error) {
            message.error('Erreur lors de l\'enregistrement');
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <Form
            form={form}
            layout="vertical"
            onFinish={handleSubmit}
            initialValues={{
                date_mission: dayjs(),
                clients: [{ logistics: [] }]
            }}
        >
            <Form.Item
                label="Date de Mission"
                name="date_mission"
                rules={[{ required: true, message: 'La date est requise' }]}
            >
                <DatePicker style={{ width: '100%' }} format="DD/MM/YYYY" />
            </Form.Item>

            <Form.Item
                label="Chauffeur"
                name="chauffeur_id"
                rules={[{ required: true, message: 'Le chauffeur est requis' }]}
            >
                <Select placeholder="Sélectionner un chauffeur">
                    {employes
                        .filter(e => e.poste_travail.toLowerCase().includes('chauffeur'))
                        .map(emp => (
                            <Option key={emp.id} value={emp.id}>
                                {emp.prenom} {emp.nom}
                            </Option>
                        ))}
                </Select>
            </Form.Item>

            <Divider>Clients et Logistique</Divider>

            <Form.List name="clients">
                {(fields, { add, remove }) => (
                    <>
                        {fields.map(({ key, name, ...restField }, index) => (
                            <Card
                                key={key}
                                title={`Client ${index + 1}`}
                                size="small"
                                style={{ marginBottom: 16 }}
                                extra={
                                    fields.length > 1 ? (
                                        <MinusCircleOutlined
                                            onClick={() => remove(name)}
                                            style={{ color: 'red' }}
                                        />
                                    ) : null
                                }
                            >
                                <Form.Item
                                    {...restField}
                                    label="Client"
                                    name={[name, 'client_id']}
                                    rules={[{ required: true, message: 'Client requis' }]}
                                >
                                    <Select placeholder="Sélectionner un client">
                                        {clients.map(cli => (
                                            <Option key={cli.id} value={cli.id}>
                                                {cli.prenom} {cli.nom} ({cli.distance} km)
                                            </Option>
                                        ))}
                                    </Select>
                                </Form.Item>

                                {/* Logistics Section */}
                                <Form.Item label="Logistique (Palettes, Caisses, etc.)">
                                    <Form.List name={[name, 'logistics']}>
                                        {(logFields, { add: addLog, remove: removeLog }) => (
                                            <>
                                                {logFields.map(({ key: logKey, name: logName, ...logRestField }) => (
                                                    <Space key={logKey} style={{ display: 'flex', marginBottom: 8 }} align="baseline">
                                                        <Form.Item
                                                            {...logRestField}
                                                            name={[logName, 'logistics_type_id']}
                                                            rules={[{ required: true, message: 'Type requis' }]}
                                                            style={{ marginBottom: 0 }}
                                                        >
                                                            <Select placeholder="Type" style={{ width: 150 }}>
                                                                {logisticsTypes.map(type => (
                                                                    <Option key={type.id} value={type.id}>
                                                                        {type.name}
                                                                    </Option>
                                                                ))}
                                                            </Select>
                                                        </Form.Item>
                                                        <Form.Item
                                                            {...logRestField}
                                                            name={[logName, 'quantity_out']}
                                                            style={{ marginBottom: 0 }}
                                                        >
                                                            <InputNumber placeholder="Qté Livrée" min={0} />
                                                        </Form.Item>
                                                        <Form.Item
                                                            {...logRestField}
                                                            name={[logName, 'quantity_in']}
                                                            style={{ marginBottom: 0 }}
                                                        >
                                                            <InputNumber placeholder="Qté Récupérée" min={0} />
                                                        </Form.Item>
                                                        <MinusCircleOutlined onClick={() => removeLog(logName)} />
                                                    </Space>
                                                ))}
                                                <Button
                                                    type="dashed"
                                                    onClick={() => addLog()}
                                                    block
                                                    icon={<PlusOutlined />}
                                                    size="small"
                                                >
                                                    Ajouter Logistique
                                                </Button>
                                            </>
                                        )}
                                    </Form.List>
                                </Form.Item>

                                {/* Treasury Section */}
                                <Form.Item
                                    {...restField}
                                    label="Montant Espèce (DA)"
                                    name={[name, 'montant_encaisse']}
                                >
                                    <InputNumber style={{ width: '100%' }} min={0} step={100} />
                                </Form.Item>

                                <Form.Item
                                    {...restField}
                                    label="Statut Versement"
                                    name={[name, 'statut_versement']}
                                    initialValue="EN_ATTENTE"
                                >
                                    <Select>
                                        <Option value="EN_ATTENTE">En Attente</Option>
                                        <Option value="VERSE">Versé</Option>
                                        <Option value="VALIDE">Validé</Option>
                                    </Select>
                                </Form.Item>

                                {/* Observations */}
                                <Form.Item
                                    {...restField}
                                    label="Observations"
                                    name={[name, 'observations']}
                                >
                                    <TextArea rows={2} placeholder="Observations du client..." />
                                </Form.Item>
                            </Card>
                        ))}
                        <Button
                            type="dashed"
                            onClick={() => add()}
                            block
                            icon={<PlusOutlined />}
                        >
                            Ajouter un Client
                        </Button>
                    </>
                )}
            </Form.List>

            <Form.Item style={{ marginTop: 24 }}>
                <Space>
                    <Button type="primary" htmlType="submit" loading={loading}>
                        {editingMission ? 'Modifier' : 'Créer'}
                    </Button>
                    <Button onClick={onCancel}>
                        Annuler
                    </Button>
                </Space>
            </Form.Item>
        </Form>
    );
};

export default MissionFormEnhanced;

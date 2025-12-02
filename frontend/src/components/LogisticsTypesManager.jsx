import React, { useState, useEffect } from 'react';
import { Card, Table, Button, Modal, Form, Input, message, Popconfirm, Tag } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import axios from 'axios';

const LogisticsTypesManager = () => {
    const [types, setTypes] = useState([]);
    const [loading, setLoading] = useState(false);
    const [modalVisible, setModalVisible] = useState(false);
    const [editingType, setEditingType] = useState(null);
    const [form] = Form.useForm();

    const API_URL = '/api/logistics-types';

    useEffect(() => {
        fetchTypes();
    }, []);

    const fetchTypes = async () => {
        setLoading(true);
        try {
            const response = await axios.get(API_URL);
            setTypes(response.data);
        } catch (error) {
            message.error('Erreur lors du chargement des types logistiques');
        } finally {
            setLoading(false);
        }
    };

    const handleAdd = () => {
        setEditingType(null);
        form.resetFields();
        setModalVisible(true);
    };

    const handleEdit = (record) => {
        setEditingType(record);
        form.setFieldsValue(record);
        setModalVisible(true);
    };

    const handleDelete = async (id) => {
        try {
            await axios.delete(`${API_URL}/${id}`);
            message.success('Type supprimé avec succès');
            fetchTypes();
        } catch (error) {
            message.error('Erreur lors de la suppression');
        }
    };

    const handleSubmit = async (values) => {
        try {
            if (editingType) {
                await axios.put(`${API_URL}/${editingType.id}`, values);
                message.success('Type modifié avec succès');
            } else {
                await axios.post(API_URL, values);
                message.success('Type créé avec succès');
            }
            setModalVisible(false);
            fetchTypes();
        } catch (error) {
            message.error('Erreur lors de l\'enregistrement');
        }
    };

    const columns = [
        {
            title: 'Nom',
            dataIndex: 'name',
            key: 'name',
        },
        {
            title: 'Statut',
            dataIndex: 'is_active',
            key: 'is_active',
            render: (active) => (
                <Tag color={active ? 'green' : 'red'}>
                    {active ? 'Actif' : 'Inactif'}
                </Tag>
            ),
        },
        {
            title: 'Actions',
            key: 'actions',
            render: (_, record) => (
                <div className="flex gap-2">
                    <Button
                        type="link"
                        icon={<EditOutlined />}
                        onClick={() => handleEdit(record)}
                    >
                        Modifier
                    </Button>
                    <Popconfirm
                        title="Êtes-vous sûr de vouloir supprimer ce type ?"
                        onConfirm={() => handleDelete(record.id)}
                        okText="Oui"
                        cancelText="Non"
                    >
                        <Button type="link" danger icon={<DeleteOutlined />}>
                            Supprimer
                        </Button>
                    </Popconfirm>
                </div>
            ),
        },
    ];

    return (
        <Card
            title="Types Logistiques (Palettes, Caisses, etc.)"
            extra={
                <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
                    Nouveau Type
                </Button>
            }
        >
            <Table
                columns={columns}
                dataSource={types}
                rowKey="id"
                loading={loading}
                pagination={{ pageSize: 10 }}
            />

            <Modal
                title={editingType ? 'Modifier le Type' : 'Nouveau Type'}
                open={modalVisible}
                onCancel={() => setModalVisible(false)}
                onOk={() => form.submit()}
                okText="Enregistrer"
                cancelText="Annuler"
            >
                <Form form={form} layout="vertical" onFinish={handleSubmit}>
                    <Form.Item
                        name="name"
                        label="Nom du Type"
                        rules={[{ required: true, message: 'Le nom est requis' }]}
                    >
                        <Input placeholder="Ex: Palette Europe, Caisse Plastique" />
                    </Form.Item>
                    <Form.Item
                        name="is_active"
                        label="Actif"
                        valuePropName="checked"
                        initialValue={true}
                    >
                        <Input type="checkbox" />
                    </Form.Item>
                </Form>
            </Modal>
        </Card>
    );
};

export default LogisticsTypesManager;

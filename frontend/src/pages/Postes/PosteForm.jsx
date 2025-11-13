import React, { useEffect } from 'react';
import { Modal, Form, Input, Switch, message } from 'antd';
import axios from 'axios';

const PosteForm = ({ visible, onCancel, onSuccess, poste }) => {
  const [form] = Form.useForm();
  const isEdit = !!poste;

  useEffect(() => {
    if (visible && poste) {
      form.setFieldsValue(poste);
    } else if (visible) {
      form.resetFields();
    }
  }, [visible, poste, form]);

  const handleSubmit = async (values) => {
    try {
      const token = localStorage.getItem('token');
      const config = {
        headers: { Authorization: `Bearer ${token}` }
      };

      if (isEdit) {
        await axios.put(`http://localhost:8000/api/postes/${poste.id}`, values, config);
        message.success('Poste modifié avec succès');
      } else {
        await axios.post('http://localhost:8000/api/postes', values, config);
        message.success('Poste créé avec succès');
      }

      form.resetFields();
      onSuccess();
    } catch (error) {
      message.error(error.response?.data?.detail || 'Erreur lors de l\'enregistrement');
      console.error('Erreur:', error);
    }
  };

  return (
    <Modal
      title={isEdit ? `Modifier le poste: ${poste?.libelle}` : 'Créer un nouveau poste'}
      open={visible}
      onCancel={onCancel}
      onOk={() => form.submit()}
      okText="Enregistrer"
      cancelText="Annuler"
      width={600}
    >
      <Form
        form={form}
        layout="vertical"
        onFinish={handleSubmit}
        initialValues={{
          est_chauffeur: false,
          modifiable: true,
          actif: true,
        }}
      >
        <Form.Item
          label="Libellé du poste"
          name="libelle"
          rules={[
            { required: true, message: 'Veuillez saisir le libellé' },
            { min: 2, message: 'Le libellé doit contenir au moins 2 caractères' },
            { max: 100, message: 'Le libellé ne peut pas dépasser 100 caractères' }
          ]}
        >
          <Input placeholder="Ex: Chauffeur, Agent de sécurité, Gardien..." />
        </Form.Item>

        <Form.Item
          label="Poste de chauffeur"
          name="est_chauffeur"
          valuePropName="checked"
          tooltip="Les chauffeurs peuvent être assignés à des missions"
        >
          <Switch checkedChildren="Oui" unCheckedChildren="Non" />
        </Form.Item>

        <Form.Item
          label="Poste modifiable"
          name="modifiable"
          valuePropName="checked"
          tooltip="Si désactivé, le poste ne pourra plus être modifié ou supprimé (réservé aux postes système)"
        >
          <Switch checkedChildren="Oui" unCheckedChildren="Non" />
        </Form.Item>

        <Form.Item
          label="Poste actif"
          name="actif"
          valuePropName="checked"
          tooltip="Les postes inactifs ne sont plus visibles dans les listes"
        >
          <Switch checkedChildren="Oui" unCheckedChildren="Non" />
        </Form.Item>
      </Form>
    </Modal>
  );
};

export default PosteForm;

import { useState, useEffect } from 'react';
import api from '../../services/api';
import { toast } from 'react-hot-toast';
import { Truck, Plus, Edit2, Trash2, X, Check, AlertCircle, Calendar, Box } from 'lucide-react';

const Camions = () => {
  const [camions, setCamions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [filter, setFilter] = useState('all'); // all, actif, inactif
  const [stats, setStats] = useState({ total: 0, actifs: 0, inactifs: 0 });

  const [formData, setFormData] = useState({
    marque: '',
    modele: '',
    immatriculation: '',
    annee_fabrication: null,
    capacite_charge: null,
    actif: true,
    date_acquisition: '',
    date_revision: '',
    notes: ''
  });

  useEffect(() => {
    fetchCamions();
  }, [filter]);

  const fetchCamions = async () => {
    setLoading(true);
    try {
      const params = filter !== 'all' ? { actif: filter === 'actif' } : {};
      const response = await api.get('/camions', { params });
      
      setCamions(response.data.camions);
      setStats({
        total: response.data.total,
        actifs: response.data.actifs,
        inactifs: response.data.inactifs
      });
    } catch (error) {
      console.error('Erreur chargement camions:', error);
      toast.error('Erreur lors du chargement des camions');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Validation
    if (!formData.marque || !formData.modele || !formData.immatriculation) {
      toast.error('Marque, modèle et immatriculation sont obligatoires');
      return;
    }

    try {
      // Nettoyer les données : convertir chaînes vides en null pour les dates
      const data = {
        ...formData,
        immatriculation: formData.immatriculation.toUpperCase(),
        date_acquisition: formData.date_acquisition || null,
        date_revision: formData.date_revision || null
      };

      if (editingId) {
        await api.put(`/camions/${editingId}`, data);
        toast.success('Camion modifié avec succès');
      } else {
        await api.post('/camions', data);
        toast.success('Camion créé avec succès');
      }

      fetchCamions();
      resetForm();
    } catch (error) {
      console.error('Erreur sauvegarde camion:', error);
      toast.error(error.response?.data?.detail || 'Erreur lors de la sauvegarde');
    }
  };

  const handleEdit = (camion) => {
    setFormData({
      marque: camion.marque,
      modele: camion.modele,
      immatriculation: camion.immatriculation,
      annee_fabrication: camion.annee_fabrication,
      capacite_charge: camion.capacite_charge,
      actif: camion.actif,
      date_acquisition: camion.date_acquisition || '',
      date_revision: camion.date_revision || '',
      notes: camion.notes || ''
    });
    setEditingId(camion.id);
    setShowModal(true);
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Êtes-vous sûr de vouloir supprimer ce camion ?')) {
      return;
    }

    try {
      await api.delete(`/camions/${id}`);
      toast.success('Camion supprimé');
      fetchCamions();
    } catch (error) {
      console.error('Erreur suppression:', error);
      toast.error(error.response?.data?.detail || 'Erreur lors de la suppression');
    }
  };

  const resetForm = () => {
    setFormData({
      marque: '',
      modele: '',
      immatriculation: '',
      annee_fabrication: null,
      capacite_charge: null,
      actif: true,
      date_acquisition: '',
      date_revision: '',
      notes: ''
    });
    setEditingId(null);
    setShowModal(false);
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* En-tête */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <Truck className="w-8 h-8 text-blue-600" />
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Gestion des Camions</h1>
              <p className="text-gray-600">Parc de véhicules de l'entreprise</p>
            </div>
          </div>
          <button
            onClick={() => setShowModal(true)}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
          >
            <Plus className="w-5 h-5" />
            Nouveau Camion
          </button>
        </div>

        {/* Statistiques */}
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-white p-4 rounded-lg shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Total Camions</p>
                <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
              </div>
              <Truck className="w-10 h-10 text-gray-400" />
            </div>
          </div>
          
          <div className="bg-green-50 p-4 rounded-lg shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-green-700 text-sm">Actifs</p>
                <p className="text-2xl font-bold text-green-600">{stats.actifs}</p>
              </div>
              <Check className="w-10 h-10 text-green-400" />
            </div>
          </div>
          
          <div className="bg-red-50 p-4 rounded-lg shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-red-700 text-sm">Inactifs</p>
                <p className="text-2xl font-bold text-red-600">{stats.inactifs}</p>
              </div>
              <AlertCircle className="w-10 h-10 text-red-400" />
            </div>
          </div>
        </div>
      </div>

      {/* Filtres */}
      <div className="mb-4 flex gap-2">
        <button
          onClick={() => setFilter('all')}
          className={`px-4 py-2 rounded ${filter === 'all' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700'}`}
        >
          Tous ({stats.total})
        </button>
        <button
          onClick={() => setFilter('actif')}
          className={`px-4 py-2 rounded ${filter === 'actif' ? 'bg-green-600 text-white' : 'bg-gray-200 text-gray-700'}`}
        >
          Actifs ({stats.actifs})
        </button>
        <button
          onClick={() => setFilter('inactif')}
          className={`px-4 py-2 rounded ${filter === 'inactif' ? 'bg-red-600 text-white' : 'bg-gray-200 text-gray-700'}`}
        >
          Inactifs ({stats.inactifs})
        </button>
      </div>

      {/* Tableau */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        {loading ? (
          <div className="p-8 text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Chargement...</p>
          </div>
        ) : camions.length === 0 ? (
          <div className="p-8 text-center">
            <Truck className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-600">Aucun camion trouvé</p>
          </div>
        ) : (
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Marque</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Modèle</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Immatriculation</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Année</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Capacité</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Missions</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Statut</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {camions.map((camion) => (
                <tr key={camion.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <Truck className="w-5 h-5 text-gray-400 mr-2" />
                      <span className="font-medium text-gray-900">{camion.marque}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-gray-600">{camion.modele}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="font-mono text-sm bg-gray-100 px-2 py-1 rounded">{camion.immatriculation}</span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-gray-600">{camion.annee_fabrication || '-'}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-gray-600">
                    {camion.capacite_charge ? `${camion.capacite_charge} kg` : '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="text-blue-600 font-medium">{camion.nombre_missions}</span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {camion.actif ? (
                      <span className="px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">
                        Actif
                      </span>
                    ) : (
                      <span className="px-2 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800">
                        Inactif
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button
                      onClick={() => handleEdit(camion)}
                      className="text-blue-600 hover:text-blue-900 mr-3"
                    >
                      <Edit2 className="w-5 h-5 inline" />
                    </button>
                    <button
                      onClick={() => handleDelete(camion.id)}
                      className="text-red-600 hover:text-red-900"
                    >
                      <Trash2 className="w-5 h-5 inline" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Modal Formulaire */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b px-6 py-4 flex items-center justify-between">
              <h2 className="text-xl font-bold text-gray-900">
                {editingId ? 'Modifier Camion' : 'Nouveau Camion'}
              </h2>
              <button onClick={resetForm} className="text-gray-500 hover:text-gray-700">
                <X className="w-6 h-6" />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="p-6">
              <div className="grid grid-cols-2 gap-4">
                {/* Marque */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Marque <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={formData.marque}
                    onChange={(e) => setFormData({ ...formData, marque: e.target.value })}
                    className="w-full p-2 border rounded"
                    placeholder="HYUNDAI"
                    required
                  />
                </div>

                {/* Modèle */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Modèle <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={formData.modele}
                    onChange={(e) => setFormData({ ...formData, modele: e.target.value })}
                    className="w-full p-2 border rounded"
                    placeholder="HD35"
                    required
                  />
                </div>

                {/* Immatriculation */}
                <div className="col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Immatriculation <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={formData.immatriculation}
                    onChange={(e) => setFormData({ ...formData, immatriculation: e.target.value.toUpperCase() })}
                    className="w-full p-2 border rounded font-mono"
                    placeholder="152455-109-43"
                    required
                  />
                </div>

                {/* Année */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Année de fabrication
                  </label>
                  <input
                    type="number"
                    value={formData.annee_fabrication || ''}
                    onChange={(e) => setFormData({ ...formData, annee_fabrication: e.target.value ? parseInt(e.target.value) : null })}
                    className="w-full p-2 border rounded"
                    placeholder="2020"
                    min="1900"
                    max={new Date().getFullYear() + 1}
                  />
                </div>

                {/* Capacité */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Capacité de charge (kg)
                  </label>
                  <input
                    type="number"
                    value={formData.capacite_charge || ''}
                    onChange={(e) => setFormData({ ...formData, capacite_charge: e.target.value ? parseInt(e.target.value) : null })}
                    className="w-full p-2 border rounded"
                    placeholder="3500"
                    min="0"
                  />
                </div>

                {/* Date acquisition */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Date d'acquisition
                  </label>
                  <input
                    type="date"
                    value={formData.date_acquisition}
                    onChange={(e) => setFormData({ ...formData, date_acquisition: e.target.value })}
                    className="w-full p-2 border rounded"
                  />
                </div>

                {/* Date révision */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Prochaine révision
                  </label>
                  <input
                    type="date"
                    value={formData.date_revision}
                    onChange={(e) => setFormData({ ...formData, date_revision: e.target.value })}
                    className="w-full p-2 border rounded"
                  />
                </div>

                {/* Statut */}
                <div className="col-span-2">
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={formData.actif}
                      onChange={(e) => setFormData({ ...formData, actif: e.target.checked })}
                      className="w-4 h-4"
                    />
                    <span className="text-sm font-medium text-gray-700">Camion actif</span>
                  </label>
                </div>

                {/* Notes */}
                <div className="col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Notes
                  </label>
                  <textarea
                    value={formData.notes}
                    onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                    className="w-full p-2 border rounded"
                    rows="3"
                    placeholder="Notes diverses, historique, incidents..."
                  />
                </div>
              </div>

              {/* Boutons */}
              <div className="flex justify-end gap-3 mt-6">
                <button
                  type="button"
                  onClick={resetForm}
                  className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  {editingId ? 'Modifier' : 'Créer'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Camions;

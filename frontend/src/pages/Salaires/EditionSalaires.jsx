import React, { useState, useEffect } from 'react';
import Layout from '../../components/Layout';
import Card from '../../components/Card';
import Button from '../../components/Button';
import editionSalaireService from '../../services/editionSalaireService';
import { toast } from 'react-hot-toast';

const EditionSalaires = () => {
    const [loading, setLoading] = useState(false);
    const [data, setData] = useState([]);
    const [period, setPeriod] = useState({
        annee: new Date().getFullYear(),
        mois: new Date().getMonth() + 1
    });

    const months = [
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
        { value: 12, label: 'Décembre' }
    ];

    const fetchPreview = async () => {
        setLoading(true);
        try {
            const result = await editionSalaireService.getPreview(period.annee, period.mois);
            setData(result);
            toast.success(`${result.length} employés calculés`);
        } catch (error) {
            toast.error("Impossible de charger l'édition des salaires");
        } finally {
            setLoading(false);
        }
    };

    return (
        <Layout title="Edition des Salaires">
            <div className="space-y-6">

                {/* Filtres de Période */}
                <Card>
                    <div className="flex flex-wrap items-end gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Année</label>
                            <input
                                type="number"
                                value={period.annee}
                                onChange={(e) => setPeriod({ ...period, annee: parseInt(e.target.value) })}
                                className="block w-32 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Mois</label>
                            <select
                                value={period.mois}
                                onChange={(e) => setPeriod({ ...period, mois: parseInt(e.target.value) })}
                                className="block w-48 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                            >
                                {months.map((m) => (
                                    <option key={m.value} value={m.value}>{m.label}</option>
                                ))}
                            </select>
                        </div>

                        <Button onClick={fetchPreview} disabled={loading} variant="primary">
                            {loading ? 'Calcul en cours...' : 'Charger / Recalculer'}
                        </Button>
                    </div>
                </Card>

                {/* Tableau de résultats */}
                {data.length > 0 && (
                    <Card>
                        <div className="overflow-x-auto">
                            <table className="min-w-full divide-y divide-gray-200">
                                <thead className="bg-gray-50">
                                    <tr>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Matricule</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Employé</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Jours Trav.</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Base Prorata</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Primes</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Cotisable</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">IRG</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Net à Payer</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Statut</th>
                                    </tr>
                                </thead>
                                <tbody className="bg-white divide-y divide-gray-200">
                                    {data.map((row) => (
                                        <tr key={row.employe_id} className="hover:bg-gray-50">
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{row.employe_matricule}</td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                                {row.employe_nom} {row.employe_prenom}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{row.jours_travailles}</td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                                {new Intl.NumberFormat('fr-DZ', { style: 'currency', currency: 'DZD' }).format(row.salaire_base_proratis)}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                                {/* Somme des primes pour affichage simplifié */}
                                                {new Intl.NumberFormat('fr-DZ', { style: 'currency', currency: 'DZD' }).format(
                                                    (row.salaire_cotisable - row.salaire_base_proratis - row.heures_supplementaires) // Approximation primes
                                                )}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                                {new Intl.NumberFormat('fr-DZ', { style: 'currency', currency: 'DZD' }).format(row.salaire_cotisable)}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-red-600 font-medium">
                                                {new Intl.NumberFormat('fr-DZ', { style: 'currency', currency: 'DZD' }).format(row.irg)}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-green-600 font-bold">
                                                {new Intl.NumberFormat('fr-DZ', { style: 'currency', currency: 'DZD' }).format(row.salaire_net)}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap">
                                                <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
                          ${row.status === 'OK' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                                                    {row.status}
                                                </span>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                        {data.length === 0 && !loading && (
                            <div className="text-center py-10 text-gray-500">
                                Aucune donnée à afficher. Lancez le calcul.
                            </div>
                        )}
                    </Card>
                )}
            </div>
        </Layout>
    );
};

export default EditionSalaires;

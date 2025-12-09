import React, { useState, useEffect } from 'react';
import {
    Calculator,
    Download,
    Eye,
    Save,
    CheckCircle,
    AlertTriangle,
    RefreshCw,
    FileText,
    TrendingUp,
    Search,
    X
} from 'lucide-react';
import axios from 'axios';
import { toast } from 'react-hot-toast';

const MOIS = [
    'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
    'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'
];

const TraitementSalaires = () => {
    const currentYear = new Date().getFullYear();
    const currentMonth = new Date().getMonth() + 1;

    const [annee, setAnnee] = useState(currentYear);
    const [mois, setMois] = useState(currentMonth);
    const [loading, setLoading] = useState(false);
    const [salaires, setSalaires] = useState([]);
    const [statistiques, setStatistiques] = useState(null);
    const [selectedEmploye, setSelectedEmploye] = useState(null);
    const [showDetails, setShowDetails] = useState(false);
    
    // Filtres de recherche
    const [filtreNom, setFiltreNom] = useState('');
    const [filtreStatut, setFiltreStatut] = useState('TOUS');
    const [filtreSalaireMin, setFiltreSalaireMin] = useState('');
    const [filtreSalaireMax, setFiltreSalaireMax] = useState('');

    useEffect(() => {
        chargerSalaires();
    }, [annee, mois]);

    const chargerSalaires = async () => {
        setLoading(true);
        try {
            const response = await axios.get(`/api/traitement-salaires/preview`, {
                params: { annee, mois }
            });

            setSalaires(response.data.resultats || []);
            
            // Calculer statistiques depuis les résultats
            const resultatsOK = (response.data.resultats || []).filter(r => r.status === 'OK');
            
            if (resultatsOK.length > 0) {
                const stats = {
                    nombre_employes: resultatsOK.length,
                    masse_salariale_nette: resultatsOK.reduce((sum, r) => sum + parseFloat(r.salaire_net || 0), 0),
                    masse_cotisable: resultatsOK.reduce((sum, r) => sum + parseFloat(r.salaire_cotisable || 0), 0),
                    masse_imposable: resultatsOK.reduce((sum, r) => sum + parseFloat(r.salaire_imposable || 0), 0),
                    total_irg: resultatsOK.reduce((sum, r) => sum + parseFloat(r.irg || 0), 0)
                };
                setStatistiques(stats);
            } else {
                setStatistiques({
                    nombre_employes: 0,
                    masse_salariale_nette: 0,
                    masse_cotisable: 0,
                    masse_imposable: 0,
                    total_irg: 0
                });
            }

            if (response.data.error_count > 0) {
                toast.error(`${response.data.error_count} employé(s) avec erreur`);
            } else {
                toast.success(`${response.data.success_count} salaires calculés`);
            }
        } catch (error) {
            console.error('Erreur chargement salaires:', error);
            toast.error('Erreur lors du chargement des salaires');
        } finally {
            setLoading(false);
        }
    };

    const validerSalaire = async (employe_id) => {
        try {
            await axios.post(`/api/traitement-salaires/valider/${employe_id}`, null, {
                params: { annee, mois }
            });
            
            toast.success('Salaire validé et enregistré');
            chargerSalaires();
        } catch (error) {
            console.error('Erreur validation:', error);
            toast.error('Erreur lors de la validation');
        }
    };

    const validerTous = async () => {
        if (!window.confirm(`Valider TOUS les salaires de ${MOIS[mois - 1]} ${annee} ?`)) {
            return;
        }

        setLoading(true);
        try {
            const response = await axios.post(`/api/traitement-salaires/valider-tous`, null, {
                params: { annee, mois }
            });

            toast.success(response.data.message);
            chargerSalaires();
        } catch (error) {
            console.error('Erreur validation globale:', error);
            toast.error('Erreur lors de la validation globale');
        } finally {
            setLoading(false);
        }
    };

    const afficherDetails = (employe) => {
        setSelectedEmploye(employe);
        setShowDetails(true);
    };

    const formaterMontant = (montant) => {
        const valeur = parseFloat(montant) || 0;
        return new Intl.NumberFormat('fr-DZ', {
            style: 'currency',
            currency: 'DZD',
            minimumFractionDigits: 2
        }).format(valeur);
    };

    const getStatusBadge = (salaire) => {
        if (salaire.status === 'ERROR') {
            return (
                <span className="px-2 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800 flex items-center gap-1">
                    <AlertTriangle className="w-3 h-3" />
                    Erreur
                </span>
            );
        }

        if (salaire.alerte) {
            return (
                <span className="px-2 py-1 text-xs font-semibold rounded-full bg-yellow-100 text-yellow-800 flex items-center gap-1">
                    <AlertTriangle className="w-3 h-3" />
                    {salaire.alerte.replace(/_/g, ' ')}
                </span>
            );
        }

        return (
            <span className="px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800 flex items-center gap-1">
                <CheckCircle className="w-3 h-3" />
                OK
            </span>
        );
    };

    // Fonction de filtrage
    const salairesFiltres = salaires.filter(salaire => {
        // Filtre par nom
        const nomComplet = `${salaire.employe_nom} ${salaire.employe_prenom}`.toLowerCase();
        if (filtreNom && !nomComplet.includes(filtreNom.toLowerCase())) {
            return false;
        }

        // Filtre par statut
        if (filtreStatut !== 'TOUS') {
            if (filtreStatut === 'OK' && salaire.status !== 'OK') return false;
            if (filtreStatut === 'ERROR' && salaire.status !== 'ERROR') return false;
            if (filtreStatut === 'ALERTE' && !salaire.alerte) return false;
        }

        // Filtre par salaire net
        if (salaire.status === 'OK') {
            const salaireNet = parseFloat(salaire.salaire_net);
            if (filtreSalaireMin && salaireNet < parseFloat(filtreSalaireMin)) return false;
            if (filtreSalaireMax && salaireNet > parseFloat(filtreSalaireMax)) return false;
        }

        return true;
    });

    const reinitialiserFiltres = () => {
        setFiltreNom('');
        setFiltreStatut('TOUS');
        setFiltreSalaireMin('');
        setFiltreSalaireMax('');
    };

    return (
        <div className="p-6 max-w-7xl mx-auto">
            {/* En-tête */}
            <div className="mb-6">
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
                            <Calculator className="w-8 h-8 text-blue-600" />
                            Traitement des Salaires
                        </h1>
                        <p className="mt-1 text-sm text-gray-500">
                            Nouveau module v3.0 - Calcul automatique et traçable
                        </p>
                    </div>
                </div>
            </div>

            {/* Sélection période + Statistiques */}
            <div className="grid grid-cols-1 lg:grid-cols-6 gap-4 mb-6">
                {/* Sélection */}
                <div className="bg-white rounded-lg shadow p-4 lg:col-span-2">
                    <h3 className="text-lg font-semibold mb-4">Période</h3>
                    <div className="space-y-3">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Année
                            </label>
                            <select
                                value={annee}
                                onChange={(e) => setAnnee(parseInt(e.target.value))}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                            >
                                {[...Array(5)].map((_, i) => {
                                    const year = currentYear - 2 + i;
                                    return <option key={year} value={year}>{year}</option>;
                                })}
                            </select>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Mois
                            </label>
                            <select
                                value={mois}
                                onChange={(e) => setMois(parseInt(e.target.value))}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                            >
                                {MOIS.map((m, index) => (
                                    <option key={index + 1} value={index + 1}>{m}</option>
                                ))}
                            </select>
                        </div>

                        <button
                            onClick={chargerSalaires}
                            disabled={loading}
                            className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 text-sm"
                        >
                            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                            {loading ? 'Calcul...' : 'Recalculer'}
                        </button>

                        <button
                            onClick={validerTous}
                            disabled={loading || salaires.length === 0}
                            className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 text-sm"
                        >
                            <Save className="w-4 h-4" />
                            Valider Tous
                        </button>
                    </div>
                </div>

                {/* Statistiques - 4 cartes compactes */}
                {statistiques && (
                    <>
                        <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg shadow p-4 text-white">
                            <div className="flex items-center justify-between mb-1">
                                <h3 className="text-xs font-medium opacity-90">Masse Nette</h3>
                                <TrendingUp className="w-4 h-4 opacity-75" />
                            </div>
                            <p className="text-xl font-bold">{formaterMontant(statistiques.masse_salariale_nette)}</p>
                            <p className="text-xs opacity-75 mt-1">{statistiques.nombre_employes} employés</p>
                        </div>

                        <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-lg shadow p-4 text-white">
                            <div className="flex items-center justify-between mb-1">
                                <h3 className="text-xs font-medium opacity-90">Masse Cotisable</h3>
                                <Calculator className="w-4 h-4 opacity-75" />
                            </div>
                            <p className="text-xl font-bold">{formaterMontant(statistiques.masse_cotisable)}</p>
                            <p className="text-xs opacity-75 mt-1">Base Sécu Sociale</p>
                        </div>

                        <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-lg shadow p-4 text-white">
                            <div className="flex items-center justify-between mb-1">
                                <h3 className="text-xs font-medium opacity-90">Masse Imposable</h3>
                                <Calculator className="w-4 h-4 opacity-75" />
                            </div>
                            <p className="text-xl font-bold">{formaterMontant(statistiques.masse_imposable)}</p>
                            <p className="text-xs opacity-75 mt-1">Base IRG</p>
                        </div>

                        <div className="bg-gradient-to-br from-red-500 to-red-600 rounded-lg shadow p-4 text-white">
                            <div className="flex items-center justify-between mb-1">
                                <h3 className="text-xs font-medium opacity-90">Total IRG</h3>
                                <TrendingUp className="w-4 h-4 opacity-75" />
                            </div>
                            <p className="text-xl font-bold">{formaterMontant(statistiques.total_irg)}</p>
                            <p className="text-xs opacity-75 mt-1">Impôt global</p>
                        </div>
                    </>
                )}
            </div>

            {/* Filtres de recherche */}
            <div className="bg-white rounded-lg shadow p-4 mb-4">
                <div className="flex items-center justify-between mb-3">
                    <h3 className="text-sm font-semibold text-gray-700 flex items-center gap-2">
                        <Search className="w-4 h-4" />
                        Filtres de recherche
                    </h3>
                    <button
                        onClick={reinitialiserFiltres}
                        className="text-xs text-gray-500 hover:text-gray-700 flex items-center gap-1"
                    >
                        <X className="w-3 h-3" />
                        Réinitialiser
                    </button>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
                    <div>
                        <label className="block text-xs font-medium text-gray-700 mb-1">
                            Nom / Prénom
                        </label>
                        <input
                            type="text"
                            value={filtreNom}
                            onChange={(e) => setFiltreNom(e.target.value)}
                            placeholder="Rechercher..."
                            className="w-full px-3 py-1.5 border border-gray-300 rounded-md text-sm"
                        />
                    </div>
                    <div>
                        <label className="block text-xs font-medium text-gray-700 mb-1">
                            Statut
                        </label>
                        <select
                            value={filtreStatut}
                            onChange={(e) => setFiltreStatut(e.target.value)}
                            className="w-full px-3 py-1.5 border border-gray-300 rounded-md text-sm"
                        >
                            <option value="TOUS">Tous</option>
                            <option value="OK">OK</option>
                            <option value="ALERTE">Alerte</option>
                            <option value="ERROR">Erreur</option>
                        </select>
                    </div>
                    <div>
                        <label className="block text-xs font-medium text-gray-700 mb-1">
                            Salaire Min (DA)
                        </label>
                        <input
                            type="number"
                            value={filtreSalaireMin}
                            onChange={(e) => setFiltreSalaireMin(e.target.value)}
                            placeholder="0"
                            className="w-full px-3 py-1.5 border border-gray-300 rounded-md text-sm"
                        />
                    </div>
                    <div>
                        <label className="block text-xs font-medium text-gray-700 mb-1">
                            Salaire Max (DA)
                        </label>
                        <input
                            type="number"
                            value={filtreSalaireMax}
                            onChange={(e) => setFiltreSalaireMax(e.target.value)}
                            placeholder="999999"
                            className="w-full px-3 py-1.5 border border-gray-300 rounded-md text-sm"
                        />
                    </div>
                </div>
                <p className="text-xs text-gray-500 mt-2">
                    {salairesFiltres.length} résultat(s) sur {salaires.length} employé(s)
                </p>
            </div>

            {/* Liste des salaires */}
            <div className="bg-white rounded-lg shadow overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                            <tr>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Employé
                                </th>
                                <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    J. Travaillés
                                </th>
                                <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Absences
                                </th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Salaire Base
                                </th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Salaire Cotisable
                                </th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Salaire Imposable
                                </th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    IRG
                                </th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Salaire Net
                                </th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Statut
                                </th>
                                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Actions
                                </th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                            {loading ? (
                                <tr>
                                    <td colSpan="10" className="px-6 py-12 text-center">
                                        <RefreshCw className="w-8 h-8 animate-spin mx-auto text-blue-600 mb-2" />
                                        <p className="text-gray-500">Calcul des salaires en cours...</p>
                                    </td>
                                </tr>
                            ) : salairesFiltres.length === 0 ? (
                                <tr>
                                    <td colSpan="10" className="px-6 py-12 text-center text-gray-500">
                                        {salaires.length === 0 ? 'Aucun salaire calculé' : 'Aucun résultat trouvé'}
                                    </td>
                                </tr>
                            ) : (
                                salairesFiltres.map((salaire) => (
                                    <tr key={salaire.employe_id} className="hover:bg-gray-50">
                                        <td className="px-4 py-3 whitespace-nowrap">
                                            <div className="text-sm font-medium text-gray-900">
                                                {salaire.employe_nom} {salaire.employe_prenom}
                                            </div>
                                        </td>
                                        <td className="px-4 py-3 whitespace-nowrap text-center">
                                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                                                {salaire.status === 'OK' && salaire.jours_travailles ? salaire.jours_travailles : '-'}
                                            </span>
                                        </td>
                                        <td className="px-4 py-3 whitespace-nowrap text-center">
                                            {salaire.status === 'OK' && salaire.jours_ouvrables && salaire.jours_travailles ? (
                                                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                                                    {salaire.jours_ouvrables - salaire.jours_travailles}
                                                </span>
                                            ) : (
                                                <span className="text-gray-400">-</span>
                                            )}
                                        </td>
                                        <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                                            {salaire.status === 'OK' ? formaterMontant(salaire.salaire_base) : '-'}
                                        </td>
                                        <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-700 font-medium">
                                            {salaire.status === 'OK' ? formaterMontant(salaire.salaire_cotisable) : '-'}
                                        </td>
                                        <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-700 font-medium">
                                            {salaire.status === 'OK' ? formaterMontant(salaire.salaire_imposable) : '-'}
                                        </td>
                                        <td className="px-4 py-3 whitespace-nowrap text-sm text-red-600 font-semibold">
                                            {salaire.status === 'OK' ? formaterMontant(salaire.irg) : '-'}
                                        </td>
                                        <td className="px-4 py-3 whitespace-nowrap">
                                            <div className="text-sm font-bold text-green-700">
                                                {salaire.status === 'OK' ? formaterMontant(salaire.salaire_net) : '-'}
                                            </div>
                                        </td>
                                        <td className="px-4 py-3 whitespace-nowrap">
                                            {getStatusBadge(salaire)}
                                        </td>
                                        <td className="px-4 py-3 whitespace-nowrap text-right text-sm font-medium">
                                            <div className="flex items-center justify-end gap-2">
                                                {salaire.status === 'OK' && (
                                                    <>
                                                        <button
                                                            onClick={() => afficherDetails(salaire)}
                                                            className="text-blue-600 hover:text-blue-900"
                                                            title="Voir détails"
                                                        >
                                                            <Eye className="w-5 h-5" />
                                                        </button>
                                                        <button
                                                            onClick={() => validerSalaire(salaire.employe_id)}
                                                            className="text-green-600 hover:text-green-900"
                                                            title="Valider & Enregistrer"
                                                        >
                                                            <Save className="w-5 h-5" />
                                                        </button>
                                                    </>
                                                )}
                                                {salaire.status === 'ERROR' && (
                                                    <span className="text-red-600 text-xs">
                                                        {salaire.error}
                                                    </span>
                                                )}
                                            </div>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Modal Détails */}
            {showDetails && selectedEmploye && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
                    <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
                        <div className="sticky top-0 bg-white border-b px-6 py-4 flex items-center justify-between">
                            <h2 className="text-xl font-bold">
                                Détails Calcul - {selectedEmploye.employe_nom} {selectedEmploye.employe_prenom}
                            </h2>
                            <button
                                onClick={() => setShowDetails(false)}
                                className="text-gray-400 hover:text-gray-600"
                            >
                                ✕
                            </button>
                        </div>

                        <div className="p-6 space-y-6">
                            {/* Salaire de base */}
                            <div>
                                <h3 className="font-semibold text-lg mb-2">SALAIRE DE BASE</h3>
                                <div className="bg-gray-50 rounded p-3 space-y-1 text-sm">
                                    <div className="flex justify-between">
                                        <span>Salaire mensuel:</span>
                                        <span className="font-semibold">{formaterMontant(selectedEmploye.salaire_base)}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span>Jours travaillés:</span>
                                        <span>{selectedEmploye.jours_travailles} / {selectedEmploye.jours_ouvrables_travailles} jours</span>
                                    </div>
                                    <div className="flex justify-between border-t pt-1 mt-1">
                                        <span className="font-semibold">Salaire proratisé:</span>
                                        <span className="font-semibold text-blue-600">{formaterMontant(selectedEmploye.salaire_base_proratis)}</span>
                                    </div>
                                </div>
                            </div>

                            {/* Heures supplémentaires */}
                            {parseFloat(selectedEmploye.heures_supplementaires) > 0 && (
                                <div>
                                    <h3 className="font-semibold text-lg mb-2">HEURES SUPPLÉMENTAIRES</h3>
                                    <div className="bg-gray-50 rounded p-3 text-sm">
                                        <div className="flex justify-between">
                                            <span>Montant (taux 150%):</span>
                                            <span className="font-semibold text-blue-600">{formaterMontant(selectedEmploye.heures_supplementaires)}</span>
                                        </div>
                                    </div>
                                </div>
                            )}

                            {/* Primes cotisables */}
                            <div>
                                <h3 className="font-semibold text-lg mb-2">PRIMES COTISABLES</h3>
                                <div className="bg-gray-50 rounded p-3 space-y-1 text-sm">
                                    {parseFloat(selectedEmploye.indemnite_nuisance) > 0 && (
                                        <div className="flex justify-between">
                                            <span>Indemnité Nuisance:</span>
                                            <span>{formaterMontant(selectedEmploye.indemnite_nuisance)}</span>
                                        </div>
                                    )}
                                    {parseFloat(selectedEmploye.ifsp) > 0 && (
                                        <div className="flex justify-between">
                                            <span>IFSP:</span>
                                            <span>{formaterMontant(selectedEmploye.ifsp)}</span>
                                        </div>
                                    )}
                                    {parseFloat(selectedEmploye.iep) > 0 && (
                                        <div className="flex justify-between">
                                            <span>IEP:</span>
                                            <span>{formaterMontant(selectedEmploye.iep)}</span>
                                        </div>
                                    )}
                                    {parseFloat(selectedEmploye.prime_encouragement) > 0 && (
                                        <div className="flex justify-between">
                                            <span>Prime Encouragement:</span>
                                            <span>{formaterMontant(selectedEmploye.prime_encouragement)}</span>
                                        </div>
                                    )}
                                    {parseFloat(selectedEmploye.prime_chauffeur) > 0 && (
                                        <div className="flex justify-between">
                                            <span>Prime Chauffeur:</span>
                                            <span>{formaterMontant(selectedEmploye.prime_chauffeur)}</span>
                                        </div>
                                    )}
                                    {parseFloat(selectedEmploye.prime_nuit_agent_securite) > 0 && (
                                        <div className="flex justify-between">
                                            <span>Prime Nuit:</span>
                                            <span>{formaterMontant(selectedEmploye.prime_nuit_agent_securite)}</span>
                                        </div>
                                    )}
                                    <div className="flex justify-between border-t pt-1 mt-1 font-semibold">
                                        <span>TOTAL COTISABLE:</span>
                                        <span className="text-blue-600">{formaterMontant(selectedEmploye.salaire_cotisable)}</span>
                                    </div>
                                </div>
                            </div>

                            {/* Retenues */}
                            <div>
                                <h3 className="font-semibold text-lg mb-2">RETENUES</h3>
                                <div className="bg-gray-50 rounded p-3 space-y-1 text-sm">
                                    <div className="flex justify-between">
                                        <span>Sécurité Sociale (9%):</span>
                                        <span className="text-red-600">-{formaterMontant(selectedEmploye.retenue_securite_sociale)}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span>IRG:</span>
                                        <span className="text-red-600">-{formaterMontant(selectedEmploye.irg)}</span>
                                    </div>
                                    {parseFloat(selectedEmploye.total_avances) > 0 && (
                                        <div className="flex justify-between">
                                            <span>Avances:</span>
                                            <span className="text-red-600">-{formaterMontant(selectedEmploye.total_avances)}</span>
                                        </div>
                                    )}
                                    {parseFloat(selectedEmploye.retenue_credit) > 0 && (
                                        <div className="flex justify-between">
                                            <span>Crédit:</span>
                                            <span className="text-red-600">-{formaterMontant(selectedEmploye.retenue_credit)}</span>
                                        </div>
                                    )}
                                </div>
                            </div>

                            {/* Primes non cotisables */}
                            <div>
                                <h3 className="font-semibold text-lg mb-2">PRIMES NON COTISABLES</h3>
                                <div className="bg-gray-50 rounded p-3 space-y-1 text-sm">
                                    <div className="flex justify-between">
                                        <span>Panier:</span>
                                        <span>{formaterMontant(selectedEmploye.panier)}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span>Transport:</span>
                                        <span>{formaterMontant(selectedEmploye.prime_transport)}</span>
                                    </div>
                                    {parseFloat(selectedEmploye.prime_femme_foyer) > 0 && (
                                        <div className="flex justify-between">
                                            <span>Prime Femme Foyer:</span>
                                            <span>{formaterMontant(selectedEmploye.prime_femme_foyer)}</span>
                                        </div>
                                    )}
                                </div>
                            </div>

                            {/* Salaire net */}
                            <div className="border-t-2 pt-4">
                                <div className="flex justify-between items-center">
                                    <span className="text-2xl font-bold">SALAIRE NET À PAYER:</span>
                                    <span className="text-3xl font-bold text-green-600">
                                        {formaterMontant(selectedEmploye.salaire_net)}
                                    </span>
                                </div>
                            </div>

                            {/* Alertes */}
                            {selectedEmploye.alerte && (
                                <div className="bg-yellow-50 border border-yellow-200 rounded p-4">
                                    <div className="flex items-center gap-2 text-yellow-800">
                                        <AlertTriangle className="w-5 h-5" />
                                        <span className="font-semibold">Alerte: {selectedEmploye.alerte.replace(/_/g, ' ')}</span>
                                    </div>
                                    {parseFloat(selectedEmploye.avances_reportees) > 0 && (
                                        <p className="text-sm mt-2">Avances reportées: {formaterMontant(selectedEmploye.avances_reportees)}</p>
                                    )}
                                    {parseFloat(selectedEmploye.credits_reportes) > 0 && (
                                        <p className="text-sm">Crédits reportés: {formaterMontant(selectedEmploye.credits_reportes)}</p>
                                    )}
                                </div>
                            )}
                        </div>

                        <div className="sticky bottom-0 bg-gray-50 border-t px-6 py-4 flex justify-end gap-3">
                            <button
                                onClick={() => setShowDetails(false)}
                                className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-100"
                            >
                                Fermer
                            </button>
                            <button
                                onClick={() => {
                                    validerSalaire(selectedEmploye.employe_id);
                                    setShowDetails(false);
                                }}
                                className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 flex items-center gap-2"
                            >
                                <Save className="w-4 h-4" />
                                Valider & Enregistrer
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default TraitementSalaires;

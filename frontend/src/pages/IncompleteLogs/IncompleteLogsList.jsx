import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { format } from 'date-fns';
import { fr } from 'date-fns/locale';

const IncompleteLogsList = () => {
    const [logs, setLogs] = useState([]);
    const [stats, setStats] = useState({ total: 0, pending: 0, validated: 0, corrected: 0 });
    const [loading, setLoading] = useState(true);
    const [filterStatus, setFilterStatus] = useState('pending');
    const [selectedLog, setSelectedLog] = useState(null);
    const [validationAction, setValidationAction] = useState('validate');
    const [correctionMinutes, setCorrectionMinutes] = useState('');
    const [correctionNote, setCorrectionNote] = useState('');
    const [processing, setProcessing] = useState(false);

    useEffect(() => {
        fetchLogs();
        fetchStats();
    }, [filterStatus]);

    const fetchLogs = async () => {
        try {
            setLoading(true);
            let url = `http://192.168.20.53:8000/api/incomplete-logs/?limit=100`;
            if (filterStatus !== 'all') {
                url += `&status=${filterStatus}`;
            }

            const response = await fetch(url);
            if (response.ok) {
                const data = await response.json();
                setLogs(data);
            }
        } catch (error) {
            console.error("Error fetching logs:", error);
        } finally {
            setLoading(false);
        }
    };

    const fetchStats = async () => {
        try {
            const response = await fetch(`http://192.168.20.53:8000/api/incomplete-logs/stats`);
            if (response.ok) {
                const data = await response.json();
                setStats(data);
            }
        } catch (error) {
            console.error("Error fetching stats:", error);
        }
    };

    const handleValidate = async () => {
        if (!selectedLog) return;

        try {
            setProcessing(true);

            const payload = {
                action: validationAction,
                validated_by: "Admin", // TODO: Get from auth context
                note: correctionNote
            };

            if (validationAction === 'correct') {
                if (!correctionMinutes) {
                    alert("Veuillez saisir le nombre de minutes");
                    setProcessing(false);
                    return;
                }
                payload.corrected_minutes = parseInt(correctionMinutes);
            }

            const response = await fetch(`http://192.168.20.53:8000/api/incomplete-logs/${selectedLog.id}/validate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            if (response.ok) {
                // Refresh data
                fetchLogs();
                fetchStats();
                setSelectedLog(null);
                setCorrectionMinutes('');
                setCorrectionNote('');
            } else {
                alert("Erreur lors de la validation");
            }
        } catch (error) {
            console.error("Error validating log:", error);
            alert("Erreur technique");
        } finally {
            setProcessing(false);
        }
    };

    const formatMinutes = (minutes) => {
        const h = Math.floor(minutes / 60);
        const m = minutes % 60;
        return `${h}h${m.toString().padStart(2, '0')}`;
    };

    const getStatusBadge = (status) => {
        switch (status) {
            case 'pending': return <span className="badge bg-warning text-dark">En attente</span>;
            case 'validated': return <span className="badge bg-success">Validé (Auto)</span>;
            case 'corrected': return <span className="badge bg-info text-dark">Corrigé</span>;
            case 'rejected': return <span className="badge bg-danger">Rejeté</span>;
            default: return <span className="badge bg-secondary">{status}</span>;
        }
    };

    return (
        <div className="container-fluid p-4">
            <div className="d-flex justify-content-between align-items-center mb-4">
                <h2>📋 Logs de Pointage Incomplets</h2>
                <div className="btn-group">
                    <button
                        className={`btn ${filterStatus === 'pending' ? 'btn-primary' : 'btn-outline-primary'}`}
                        onClick={() => setFilterStatus('pending')}
                    >
                        En attente <span className="badge bg-light text-dark ms-1">{stats.pending}</span>
                    </button>
                    <button
                        className={`btn ${filterStatus === 'all' ? 'btn-primary' : 'btn-outline-primary'}`}
                        onClick={() => setFilterStatus('all')}
                    >
                        Tous <span className="badge bg-light text-dark ms-1">{stats.total}</span>
                    </button>
                </div>
            </div>

            <div className="card shadow-sm">
                <div className="card-body p-0">
                    <div className="table-responsive">
                        <table className="table table-hover mb-0">
                            <thead className="bg-light">
                                <tr>
                                    <th>Date</th>
                                    <th>Employé</th>
                                    <th>Type Log</th>
                                    <th>Heure</th>
                                    <th>Estimation</th>
                                    <th>Statut</th>
                                    <th>Action</th>
                                </tr>
                            </thead>
                            <tbody>
                                {loading ? (
                                    <tr>
                                        <td colSpan="7" className="text-center py-4">Chargement...</td>
                                    </tr>
                                ) : logs.length === 0 ? (
                                    <tr>
                                        <td colSpan="7" className="text-center py-4">Aucun log incomplet trouvé</td>
                                    </tr>
                                ) : (
                                    logs.map(log => (
                                        <tr key={log.id}>
                                            <td>{format(new Date(log.log_date), 'dd/MM/yyyy')}</td>
                                            <td className="fw-bold">{log.employee_name}</td>
                                            <td>
                                                <span className={`badge ${log.log_type === 'ENTRY' ? 'bg-success' : 'bg-warning text-dark'}`}>
                                                    {log.log_type}
                                                </span>
                                                {log.log_type === 'ENTRY' ? ' (Pas de sortie)' : ' (Pas d\'entrée)'}
                                            </td>
                                            <td>{format(new Date(log.log_timestamp), 'HH:mm')}</td>
                                            <td>
                                                {log.status === 'corrected' ? (
                                                    <span className="text-decoration-line-through text-muted me-2">
                                                        {formatMinutes(log.estimated_minutes)}
                                                    </span>
                                                ) : null}
                                                <span className="fw-bold">
                                                    {formatMinutes(log.status === 'corrected' ? log.corrected_minutes : log.estimated_minutes)}
                                                </span>
                                                <div className="small text-muted fst-italic">{log.estimation_rule}</div>
                                            </td>
                                            <td>{getStatusBadge(log.status)}</td>
                                            <td>
                                                {log.status === 'pending' && (
                                                    <button
                                                        className="btn btn-sm btn-outline-primary"
                                                        onClick={() => {
                                                            setSelectedLog(log);
                                                            setCorrectionMinutes(log.estimated_minutes);
                                                            setValidationAction('validate');
                                                        }}
                                                    >
                                                        ⚙️ Gérer
                                                    </button>
                                                )}
                                            </td>
                                        </tr>
                                    ))
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            {/* Modal de Validation */}
            {selectedLog && (
                <div className="modal d-block" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
                    <div className="modal-dialog">
                        <div className="modal-content">
                            <div className="modal-header">
                                <h5 className="modal-title">Valider Log Incomplet</h5>
                                <button type="button" className="btn-close" onClick={() => setSelectedLog(null)}></button>
                            </div>
                            <div className="modal-body">
                                <div className="alert alert-info">
                                    <strong>Employé :</strong> {selectedLog.employee_name}<br />
                                    <strong>Date :</strong> {format(new Date(selectedLog.log_date), 'dd MMMM yyyy', { locale: fr })}<br />
                                    <strong>Problème :</strong> {selectedLog.log_type} sans correspondance<br />
                                    <strong>Estimation Auto :</strong> {formatMinutes(selectedLog.estimated_minutes)}
                                </div>

                                <div className="mb-3">
                                    <label className="form-label fw-bold">Action à effectuer :</label>

                                    <div className="form-check mb-2">
                                        <input
                                            className="form-check-input"
                                            type="radio"
                                            name="action"
                                            id="act_validate"
                                            checked={validationAction === 'validate'}
                                            onChange={() => setValidationAction('validate')}
                                        />
                                        <label className="form-check-label" htmlFor="act_validate">
                                            ✅ Valider l'estimation automatique ({formatMinutes(selectedLog.estimated_minutes)})
                                        </label>
                                    </div>

                                    <div className="form-check mb-2">
                                        <input
                                            className="form-check-input"
                                            type="radio"
                                            name="action"
                                            id="act_correct"
                                            checked={validationAction === 'correct'}
                                            onChange={() => setValidationAction('correct')}
                                        />
                                        <label className="form-check-label" htmlFor="act_correct">
                                            ✏️ Corriger manuellement
                                        </label>
                                    </div>

                                    {validationAction === 'correct' && (
                                        <div className="ms-4 mb-2">
                                            <div className="input-group input-group-sm" style={{ width: '200px' }}>
                                                <input
                                                    type="number"
                                                    className="form-control"
                                                    value={correctionMinutes}
                                                    onChange={(e) => setCorrectionMinutes(e.target.value)}
                                                    placeholder="Minutes"
                                                />
                                                <span className="input-group-text">minutes</span>
                                            </div>
                                            <div className="form-text">
                                                480 min = 8h, 540 min = 9h
                                            </div>
                                        </div>
                                    )}

                                    <div className="form-check">
                                        <input
                                            className="form-check-input"
                                            type="radio"
                                            name="action"
                                            id="act_reject"
                                            checked={validationAction === 'reject'}
                                            onChange={() => setValidationAction('reject')}
                                        />
                                        <label className="form-check-label" htmlFor="act_reject">
                                            ❌ Rejeter (Marquer comme absent)
                                        </label>
                                    </div>
                                </div>

                                <div className="mb-3">
                                    <label className="form-label">Note (optionnelle)</label>
                                    <textarea
                                        className="form-control"
                                        rows="2"
                                        value={correctionNote}
                                        onChange={(e) => setCorrectionNote(e.target.value)}
                                        placeholder="Raison de la correction..."
                                    ></textarea>
                                </div>
                            </div>
                            <div className="modal-footer">
                                <button type="button" className="btn btn-secondary" onClick={() => setSelectedLog(null)}>Annuler</button>
                                <button
                                    type="button"
                                    className="btn btn-primary"
                                    onClick={handleValidate}
                                    disabled={processing}
                                >
                                    {processing ? 'Traitement...' : 'Confirmer'}
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default IncompleteLogsList;

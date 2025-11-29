import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import {
    LayoutDashboard,
    Users,
    ClipboardList,
    DollarSign,
    FileText,
    Calendar,
    Settings as SettingsIcon,
    Clock,
    ScrollText,
    Briefcase,
    Database,
    UserCog,
    Download,
    AlertCircle,
    LogOut,
    Eye
} from 'lucide-react';

const Sidebar = ({ isOpen, onClose }) => {
    const location = useLocation();
    const navigate = useNavigate();

    const handleLogout = () => {
        // Clear any stored authentication data
        localStorage.removeItem('user');
        localStorage.removeItem('token');
        sessionStorage.clear();

        // Redirect to login page
        navigate('/login');

        // Close sidebar on mobile
        onClose();
    };

    const links = [
        { to: '/', label: 'Dashboard', icon: LayoutDashboard },
        { to: '/employes', label: 'Employés', icon: Users },
        { to: '/postes', label: 'Postes', icon: Briefcase },
        { to: '/pointages', label: 'Pointages', icon: ClipboardList },
        { to: '/pointages/import-preview', label: 'Import Pointages', icon: Eye },
        { to: '/missions', label: 'Missions', icon: Clock },
        { to: '/avances', label: 'Avances', icon: DollarSign },
        { to: '/credits', label: 'Crédits', icon: DollarSign },
        { to: '/conges', label: 'Congés', icon: Calendar },
        { to: '/salaires', label: 'Salaires', icon: DollarSign },
        { to: '/logs', label: 'Logs', icon: ScrollText },
        { to: '/parametres', label: 'Paramètres', icon: SettingsIcon },
        { to: '/utilisateurs', label: 'Utilisateurs', icon: UserCog },
        { to: '/database-config', label: 'Base de données', icon: Database },
    ];

    return (
        <>
            {/* Mobile Overlay */}
            {isOpen && (
                <div
                    className="fixed inset-0 bg-black bg-opacity-50 z-20 md:hidden"
                    onClick={onClose}
                />
            )}

            {/* Sidebar */}
            <div className={`
                fixed inset-y-0 left-0 z-30 w-64 bg-gray-900 text-white transform transition-transform duration-300 ease-in-out flex flex-col h-full
                md:relative md:translate-x-0
                ${isOpen ? 'translate-x-0' : '-translate-x-full'}
            `}>
                <div className="flex items-center justify-between p-6 shrink-0">
                    <div className="text-2xl font-bold text-blue-400">HR System</div>
                    {/* Close button for mobile */}
                    <button
                        onClick={onClose}
                        className="md:hidden text-gray-400 hover:text-white focus:outline-none"
                    >
                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>

                <nav className="flex-1 px-4 space-y-2 mt-4 overflow-y-auto scrollbar-none [&::-webkit-scrollbar]:hidden">
                    {links.map((link) => {
                        const Icon = link.icon;
                        const isActive = location.pathname === link.to;
                        return (
                            <Link
                                key={link.to}
                                to={link.to}
                                onClick={() => onClose()} // Close sidebar on link click (mobile)
                                className={`flex items-center px-4 py-3 rounded-lg transition-colors ${isActive ? 'bg-blue-600 text-white' : 'text-gray-400 hover:bg-gray-800 hover:text-white'
                                    }`}
                            >
                                <Icon className="w-5 h-5 mr-3 shrink-0" />
                                {link.label}
                            </Link>
                        );
                    })}
                </nav>

                {/* Logout Button */}
                <div className="px-4 pb-4 shrink-0">
                    <button
                        onClick={handleLogout}
                        className="flex items-center w-full px-4 py-3 rounded-lg transition-colors text-gray-400 hover:bg-red-600 hover:text-white border border-gray-700 hover:border-red-600"
                    >
                        <LogOut className="w-5 h-5 mr-3 shrink-0" />
                        Déconnexion
                    </button>
                </div>

                <div className="p-4 border-t border-gray-800 text-xs text-gray-500 flex flex-col items-center space-y-1 shrink-0">
                    <div className="flex justify-between w-full">
                        <span>v2.3.0</span>
                        <span>© 2025</span>
                    </div>
                    <div className="text-blue-400 font-semibold tracking-wider pt-2 opacity-80 text-[10px]">
                        Powered by AIRBAND
                    </div>
                </div>
            </div>
        </>
    );
};

export default Sidebar;

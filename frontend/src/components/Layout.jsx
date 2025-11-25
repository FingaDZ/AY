import React, { useState } from 'react';
import Sidebar from './Sidebar';
import { Outlet } from 'react-router-dom';
import { Menu } from 'lucide-react';

const Layout = () => {
    const [isSidebarOpen, setIsSidebarOpen] = useState(false);

    return (
        <div className="flex h-screen bg-gray-100 font-sans overflow-hidden">
            <Sidebar isOpen={isSidebarOpen} onClose={() => setIsSidebarOpen(false)} />

            <div className="flex-1 flex flex-col h-full overflow-hidden">
                {/* Mobile Header */}
                <div className="md:hidden bg-white border-b border-gray-200 p-4 flex items-center justify-between shrink-0">
                    <div className="text-xl font-bold text-gray-800">HR System</div>
                    <button
                        onClick={() => setIsSidebarOpen(true)}
                        className="p-2 rounded-md text-gray-600 hover:bg-gray-100 focus:outline-none"
                    >
                        <Menu className="w-6 h-6" />
                    </button>
                </div>

                {/* Main Content */}
                <main className="flex-1 overflow-y-auto bg-gray-50 p-4 md:p-8">
                    <Outlet />
                </main>

                {/* Footer */}
                <footer className="border-t border-gray-200 bg-white px-4 py-3 shrink-0">
                    <div className="flex flex-col md:flex-row items-center justify-between text-xs text-gray-500">
                        <div className="mb-1 md:mb-0">
                            © 2025 HR System - v1.1.10
                        </div>
                        <div className="text-gray-400">
                            Powered by <span className="font-semibold text-gray-600">AIRBAND</span>
                        </div>
                    </div>
                </footer>
            </div>
        </div>
    );
};

export default Layout;

import { Link, useLocation } from 'react-router-dom';
import { Moon, Sun, LayoutDashboard, FileText, BarChart3 } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';

export default function Layout({ children }) {
  const { dark, toggle } = useTheme();
  const loc = useLocation();

  const nav = [
    { path: '/', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/claims', label: 'Claims', icon: FileText },
    { path: '/model', label: 'Model Info', icon: BarChart3 },
  ];

  return (
    <div className="min-h-screen flex flex-col">
      <nav className="bg-primary dark:bg-gray-800 text-white shadow-card">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-6">
              <Link to="/" className="font-bold text-lg flex items-center gap-2">
                <BarChart3 className="w-6 h-6 text-accent" />
                Fraud Detection
              </Link>
              <div className="hidden sm:flex gap-4">
                {nav.map(({ path, label, icon: Icon }) => (
                  <Link
                    key={path}
                    to={path}
                    className={`flex items-center gap-2 px-3 py-2 rounded-md transition ${
                      loc.pathname === path
                        ? 'bg-accent/20 text-accent'
                        : 'hover:bg-white/10'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    {label}
                  </Link>
                ))}
              </div>
            </div>
            <button
              onClick={toggle}
              className="p-2 rounded-md hover:bg-white/10 transition"
              aria-label="Toggle theme"
            >
              {dark ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
            </button>
          </div>
        </div>
      </nav>
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {children}
      </main>
    </div>
  );
}

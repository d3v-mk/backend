import { Link, Outlet, useLocation } from "react-router-dom";
import { useState, useEffect, useRef } from "react";
import { useAuth } from "../../hooks/useAuth";

const links = [
  { path: "/admin", label: "🏠 Dashboard" },
  { path: "/admin/criar", label: "➕ Criar Loja Promotor" },
  { path: "/admin/cargos", label: "👥 Cargos" },
  { path: "/admin/lista", label: "📋 Lista de Promotores" },
];

export function AdminLayout() {
  const { pathname } = useLocation();
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);
  const { logout } = useAuth();

  const handleLogout = async () => {
    try {
      await fetch("http://localhost:8000/logout", {
        method: "POST",
        credentials: "include",
      });
      logout(); // atualiza o contexto
      window.location.href = "/login";
    } catch (error) {
      console.error("Erro ao deslogar:", error);
    }
  };


  useEffect(() => {
    if (!menuOpen) return;

    function handleClickOutside(event: MouseEvent) {
      if (
        menuRef.current &&
        !menuRef.current.contains(event.target as Node) &&
        window.innerWidth < 768
      ) {
        setMenuOpen(false);
      }
    }

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [menuOpen]);

  useEffect(() => {
    setMenuOpen(false);
  }, [pathname]);

  return (
    <div className="flex min-h-screen bg-gray-900 text-white relative">
      {/* Botão hamburguer mobile */}
      <button
        onClick={() => setMenuOpen((o) => !o)}
        className="p-3 m-4 text-white bg-blue-600 rounded-md hover:bg-blue-700 fixed top-0 left-0 z-50 md:hidden"
        aria-label={menuOpen ? "Fechar menu" : "Abrir menu"}
        aria-expanded={menuOpen}
        aria-controls="admin-menu"
      >
        {menuOpen ? "✕" : "☰"}
      </button>

      {/* Overlay mobile */}
      {menuOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-40 md:hidden" />
      )}

      {/* Menu lateral */}
      <aside
        id="admin-menu"
        ref={menuRef}
        className={`
          fixed top-0 left-0 h-full w-64 bg-gray-800 p-6 space-y-4 shadow-lg z-50
          transform transition-transform duration-300 ease-in-out
          ${menuOpen ? "translate-x-0" : "-translate-x-full"}
          md:static md:translate-x-0 md:flex md:flex-col md:w-64 md:shadow-none md:bg-gray-800
          md:h-auto
        `}
      >
        <h2 className="text-2xl font-bold mb-6">⚙️ Admin</h2>
        {links.map(({ path, label }) => (
          <Link
            key={path}
            to={path}
            className={`
              block px-4 py-2 rounded hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-400
              ${pathname === path ? "bg-blue-700 font-semibold" : ""}
            `}
          >
            {label}
          </Link>
        ))}

        <button
          onClick={handleLogout}
          className="block w-full text-left px-4 py-2 rounded hover:bg-red-600 focus:outline-none focus:ring-2 focus:ring-red-400 mt-4 bg-red-700 font-semibold"
        >
          🚪 Sair
        </button>

      </aside>

      {/* Conteúdo principal */}
      <main className="flex-1 p-8 overflow-y-auto md:ml-0">
        <Outlet />
      </main>
    </div>
  );
}

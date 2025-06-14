import { useState, useEffect } from "react";
import { Outlet } from "react-router-dom";
import { Footer } from "../components/Footer";
import { SidebarMenu } from "../components/SidebarMenu";
import { Header } from "../components/Header";

export default function HomeLayout() {
  const [menuOpen, setMenuOpen] = useState(false);

  // Trava o scroll quando o menu está aberto
  useEffect(() => {
    document.body.style.overflow = menuOpen ? "hidden" : "";
  }, [menuOpen]);

  return (
    <div className="flex min-h-screen bg-gradient-to-b from-black via-gray-900 to-black text-white relative">
      {/* Sidebar sempre presente, mas oculta por padrão em desktop */}
      <SidebarMenu isOpen={menuOpen} onClose={() => setMenuOpen(false)} />

      {/* Overlay para fechar menu ao clicar fora */}
      {menuOpen && (
        <div
          className="fixed inset-0 z-30"
          onClick={() => setMenuOpen(false)}
          aria-hidden="true"
        />
      )}


      <div className="flex flex-col flex-1 min-h-screen z-0">
        <Header onMenuClick={() => setMenuOpen(true)} />
        <main className="flex-1 relative z-0">
          <Outlet />
        </main>
        <Footer />
      </div>
    </div>
  );
}

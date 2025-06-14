type SidebarMenuProps = {
  isOpen: boolean;
  onClose: () => void;
};

export function SidebarMenu({ isOpen, onClose }: SidebarMenuProps) {
  return (
    <aside
      className={`fixed top-0 left-0 h-full w-64 bg-black bg-opacity-90 border-r border-yellow-500 shadow-lg flex flex-col z-40 transform transition-transform duration-300 ${
        isOpen ? "translate-x-0" : "-translate-x-full"
      }`}
    >
      <div className="px-6 py-6 flex justify-between items-center">
        <a
          href="/"
          className="text-3xl font-bold tracking-wider text-yellow-400 hover:text-yellow-300 transition"
        >
          ♠ PanoPoker
        </a>
        <button
          onClick={onClose}
          className="text-yellow-400 hover:text-yellow-300"
        >
          ✖
        </button>
      </div>

      <nav className="flex-1 px-6 space-y-4 overflow-auto">
        <a href="/" className="block text-yellow-400 hover:text-yellow-300 font-semibold text-lg">🏠 Início</a>
        <a href="/jogo" className="block text-yellow-400 hover:text-yellow-300 font-semibold text-lg">🎮 Jogar</a>
        <a href="/promotores" className="block text-yellow-400 hover:text-yellow-300 font-semibold text-lg">📋 Promotores</a>
        <a href="/perfil" className="block text-yellow-400 hover:text-yellow-300 font-semibold text-lg">👤 Perfil</a>
      </nav>

      <div className="px-6 py-4 border-t border-yellow-500 text-yellow-400 text-sm">
        © 2025 PanoPoker
      </div>
    </aside>
  );
}

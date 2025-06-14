type User = {
  name: string;
  avatarUrl: string;
};

type SidebarMenuProps = {
  isOpen: boolean;
  onClose: () => void;
  user: User | null;
};

export function SidebarMenu({ isOpen, onClose, user }: SidebarMenuProps) {
  return (
    <aside
      aria-label="Sidebar de navegação"
      className={`fixed top-0 left-0 h-full w-72 flex flex-col z-50 transform transition-transform duration-300 ${
        isOpen ? "translate-x-0" : "-translate-x-full"
      }`}
      style={{
        backgroundColor: "transparent",
        backdropFilter: "blur(4px)",
        WebkitBackdropFilter: "blur(4px)",
      }}
    >
      <nav className="flex-1 px-6 py-8 flex flex-col justify-center items-center overflow-y-auto space-y-6">
        {!user ? (
          <a
            href="/login"
            className="
              block
              text-white
              font-bold
              text-xl
              rounded-md
              px-6
              py-4
              transition
              duration-300
              w-full
              max-w-xs
              text-center
              bg-gradient-to-r from-yellow-400 to-yellow-600
              border
              border-yellow-400
              hover:bg-gradient-to-r hover:from-yellow-500 hover:to-yellow-700
              hover:border-yellow-300
            "
            tabIndex={isOpen ? 0 : -1}
          >
            Login
          </a>
        ) : (
          <div className="flex flex-col items-center space-y-4 w-full max-w-xs">
            {/* Foto do perfil */}
            <img
              src={user.avatarUrl}
              alt={`Avatar de ${user.name}`}
              className="w-24 h-24 rounded-full object-cover border-2 border-yellow-500 shadow-md"
            />
            {/* Nome */}
            <p className="text-white font-bold text-xl">{user.name}</p>

            {/* Botões do perfil */}
            <div className="flex flex-col space-y-3 w-full">
              <a
                href="/perfil"
                className="block text-center bg-yellow-600 hover:bg-yellow-700 text-white font-semibold py-3 rounded-md transition"
                tabIndex={isOpen ? 0 : -1}
              >
                Perfil
              </a>
              <a
                href="/dashboard"
                className="block text-center bg-yellow-600 hover:bg-yellow-700 text-white font-semibold py-3 rounded-md transition"
                tabIndex={isOpen ? 0 : -1}
              >
                Dashboard
              </a>
              <button
                onClick={() => {
                  // sua lógica de logout aqui
                  alert("Logout acionado!"); 
                }}
                className="block w-full bg-red-700 hover:bg-red-800 text-white font-semibold py-3 rounded-md transition"
                tabIndex={isOpen ? 0 : -1}
              >
                Sair
              </button>
            </div>
          </div>
        )}
      </nav>

      <button
        onClick={onClose}
        aria-label="Fechar menu"
        className="absolute top-4 right-4 text-yellow-400 hover:text-yellow-300 focus:outline-none focus:ring-2 focus:ring-yellow-500 rounded-full p-1 transition-transform transform hover:rotate-90"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className="h-6 w-6"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={3}
        >
          <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </aside>
  );
}

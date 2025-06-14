type HeaderProps = {
  onMenuClick: () => void;
};

export function Header({ onMenuClick }: HeaderProps) {
  return (
    <div className="fixed top-4 right-4 z-50">
      <button
        onClick={onMenuClick}
        aria-label="Abrir menu"
        className="text-yellow-400 hover:text-yellow-300 focus:outline-none bg-black bg-opacity-70 p-2 rounded-full shadow-lg"
      >
        <svg
          className="w-8 h-8"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          viewBox="0 0 24 24"
        >
          <line x1="3" y1="7" x2="21" y2="7" />
          <line x1="3" y1="12" x2="21" y2="12" />
          <line x1="3" y1="17" x2="21" y2="17" />
        </svg>
      </button>
    </div>
  );
}

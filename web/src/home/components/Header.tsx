export function Header() {
  return (
    <header className="bg-black bg-opacity-90 border-b border-yellow-500 shadow-lg">
      <nav className="container mx-auto px-6 py-4 flex items-center justify-between">
        <a href="/" className="text-3xl font-bold tracking-wider text-yellow-400 hover:text-yellow-300 transition">
          ♠ PanoPoker
        </a>
      </nav>
    </header>
  );
}

// src/home/pages/HomePage.tsx
import { HeroSection } from "../components/HeroSection";

export default function HomePage() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-r from-purple-600 to-indigo-700 text-white p-8">
      <HeroSection />
    </main>
  );
}

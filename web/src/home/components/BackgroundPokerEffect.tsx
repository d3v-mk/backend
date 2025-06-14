import { useMemo } from "react";

export function BackgroundPokerEffect() {
  const suits = ["♥", "♦", "♠", "♣"] as const;
  const colors = {
    "♥": "text-red-600",
    "♦": "text-red-600",
    "♠": "text-gray-300",
    "♣": "text-gray-300",
  };

  const items = useMemo(() => {
    return [...Array(25)].map(() => {
      const suit = suits[Math.floor(Math.random() * suits.length)];
      const left = Math.random() * 100;
      const top = Math.random() * 100;
      const duration = 10 + Math.random() * 10;
      const delay = Math.random() * 10;
      const size = 14 + Math.random() * 18;

      return { suit, left, top, duration, delay, size };
    });
  }, []); // roda só 1 vez no mount

  return (
    <div
      className="fixed inset-0 pointer-events-none overflow-hidden"
      style={{ zIndex: -1 }}
    >
      {items.map(({ suit, left, top, duration, delay, size }, i) => (
        <div
          key={i}
          className={`absolute font-bold ${colors[suit]} text-opacity-60 select-none`}
          style={{
            fontSize: `${size}px`,
            left: `${left}%`,
            top: `${top}%`,
            animation: `floatSpinPulse ${duration}s ease-in-out infinite`,
            animationDelay: `${delay}s`,
            transformOrigin: "center",
            willChange: "transform, opacity",
            userSelect: "none",
          }}
        >
          {suit}
        </div>
      ))}

      <style>{`
        @keyframes floatSpinPulse {
          0%, 100% {
            transform: translateY(0) rotate(0deg) scale(1);
            opacity: 0.6;
          }
          50% {
            transform: translateY(-20px) rotate(180deg) scale(1.2);
            opacity: 1;
          }
        }
      `}</style>
    </div>
  );
}

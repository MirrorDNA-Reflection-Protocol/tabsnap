"use client";

import { useRef, useState } from "react";

type Props = { src: string };

export default function AudioPlayer({ src }: Props) {
  const audioRef = useRef<HTMLAudioElement>(null);
  const [playing, setPlaying] = useState(false);
  const [speed, setSpeed] = useState(1);
  const [loop, setLoop] = useState(false);

  const toggle = () => {
    const el = audioRef.current;
    if (!el) return;
    if (playing) {
      el.pause();
    } else {
      el.play();
    }
    setPlaying(!playing);
  };

  const changeSpeed = (rate: number) => {
    setSpeed(rate);
    if (audioRef.current) audioRef.current.playbackRate = rate;
  };

  const toggleLoop = () => {
    setLoop(!loop);
    if (audioRef.current) audioRef.current.loop = !loop;
  };

  return (
    <div
      style={{
        background: "#111",
        borderRadius: 8,
        padding: "1rem",
        marginBottom: "1.5rem",
      }}
    >
      <audio
        ref={audioRef}
        src={src}
        loop={loop}
        onEnded={() => setPlaying(false)}
      />
      <div style={{ display: "flex", gap: "0.75rem", alignItems: "center", flexWrap: "wrap" }}>
        <button onClick={toggle} style={btnStyle}>
          {playing ? "Pause" : "Play"}
        </button>
        {[1, 0.75, 0.5].map((r) => (
          <button
            key={r}
            onClick={() => changeSpeed(r)}
            style={{
              ...btnStyle,
              background: speed === r ? "#2563eb" : "#222",
            }}
          >
            {r === 1 ? "1x" : `${Math.round(r * 100)}%`}
          </button>
        ))}
        <button
          onClick={toggleLoop}
          style={{
            ...btnStyle,
            background: loop ? "#2563eb" : "#222",
          }}
        >
          Loop {loop ? "ON" : "OFF"}
        </button>
      </div>
    </div>
  );
}

const btnStyle: React.CSSProperties = {
  padding: "0.4rem 1rem",
  background: "#222",
  border: "1px solid #333",
  borderRadius: 6,
  color: "#e0e0e0",
  cursor: "pointer",
  fontSize: "0.85rem",
};

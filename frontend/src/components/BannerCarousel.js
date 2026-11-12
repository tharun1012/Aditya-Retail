import React, { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { BACKEND_URL } from '../config/api';
import { imgSrc } from '../utils/img';

const GAP = 14; // px between slides

const BannerCarousel = () => {
  const navigate = useNavigate();
  const [banners, setBanners] = useState([]);
  const [i, setI] = useState(0);
  const [paused, setPaused] = useState(false);
  const [broken, setBroken] = useState({});
  const [wide, setWide] = useState(typeof window !== 'undefined' && window.innerWidth >= 768);
  const seen = useRef(new Set());
  const touchX = useRef(null);
  const prevOff = useRef({});

  useEffect(() => {
    const onResize = () => setWide(window.innerWidth >= 768);
    window.addEventListener('resize', onResize);
    return () => window.removeEventListener('resize', onResize);
  }, []);

  useEffect(() => {
    fetch(`${BACKEND_URL}/api/banners/active/homepage`)
      .then((r) => r.json())
      .then((d) => setBanners((d.banners || []).filter((b) => b.image_url)))
      .catch(() => {});
  }, []);

  useEffect(() => {
    if (paused || banners.length < 2) return undefined;
    const t = setInterval(() => setI((p) => (p + 1) % banners.length), 5000);
    return () => clearInterval(t);
  }, [paused, banners.length]);

  useEffect(() => {
    const b = banners[i];
    if (b && !seen.current.has(b.id)) {
      seen.current.add(b.id);
      fetch(`${BACKEND_URL}/api/banners/${b.id}/track-view`, { method: 'POST' }).catch(() => {});
    }
  }, [i, banners]);

  const N = banners.length;
  const half = Math.floor(N / 2);
  const offsetOf = (n) => (((n - i + half) % N) + N) % N - half;

  useEffect(() => {
    const m = {};
    banners.forEach((b, n) => { m[b.id] = (((n - i + half) % N) + N) % N - half; });
    prevOff.current = m;
  });

  if (N === 0) return null;
  const go = (n) => setI((n + N) % N);

  const open = (b) => {
    fetch(`${BACKEND_URL}/api/banners/${b.id}/track-click`, { method: 'POST', keepalive: true }).catch(() => {});
    const u = b.link_url;
    if (!u) return;
    if (/^https?:/.test(u)) window.open(u, '_blank', 'noopener');
    else navigate(u);
  };

  const W = wide ? 'min(1240px, 80%)' : '88%';

  return (
    <div className="relative w-full mt-3 overflow-hidden select-none h-[170px] sm:h-[220px] md:h-[280px] lg:h-[300px]"
      onMouseEnter={() => setPaused(true)} onMouseLeave={() => setPaused(false)}
      onTouchStart={(e) => { touchX.current = e.touches[0].clientX; }}
      onTouchEnd={(e) => {
        if (touchX.current == null) return;
        const dx = e.changedTouches[0].clientX - touchX.current;
        if (Math.abs(dx) > 50) go(i + (dx < 0 ? 1 : -1));
        touchX.current = null;
      }}>
      {banners.map((b, n) => {
        const off = offsetOf(n);
        const active = off === 0;
        const prev = prevOff.current[b.id];
        const jump = prev !== undefined && Math.abs(off - prev) > 1; // wrapping slide: no slide-across animation
        return (
          <div key={b.id} data-slide="" role="link" aria-label={b.title}
            onClick={() => (active ? open(b) : go(n))}
            style={{
              position: 'absolute', top: 0, bottom: 0, left: '50%', width: W,
              marginLeft: `calc(${W} / -2)`,
              transform: `translateX(calc(${off} * (100% + ${GAP}px)))`,
              transition: jump ? 'none' : 'transform 500ms ease-out, opacity 500ms',
              opacity: active ? 1 : 0.55,
            }}
            className="overflow-hidden rounded-xl md:rounded-2xl cursor-pointer bg-gray-100">
            {broken[b.id] ? (
              <div className="absolute inset-0 bg-gradient-to-r from-amber-700 to-orange-500" />
            ) : (
              <img src={imgSrc(b.image_url)} alt={b.title} draggable={false}
                onError={() => setBroken((p) => ({ ...p, [b.id]: true }))}
                className="absolute inset-0 h-full w-full object-cover object-center" />
            )}
            <div className="absolute inset-0 bg-gradient-to-r from-black/60 via-black/20 to-transparent" />
            <div className="absolute inset-y-0 left-0 flex max-w-[85%] flex-col justify-center px-5 md:px-14 text-white">
              <h2 className="text-lg sm:text-2xl md:text-3xl font-bold leading-tight">{b.title}</h2>
              {b.description && <p className="mt-1 hidden md:block text-sm lg:text-base text-white/90 max-w-xl">{b.description}</p>}
              {b.link_url && (
                <span className="mt-3 inline-block self-start rounded-full bg-white px-4 py-1.5 text-xs md:text-sm font-semibold text-gray-900">
                  Shop now
                </span>
              )}
            </div>
          </div>
        );
      })}
      {N > 1 && (
        <>
          <button onClick={() => go(i - 1)} aria-label="Previous"
            className="absolute left-2 md:left-6 top-1/2 z-10 -translate-y-1/2 rounded-full bg-white/90 p-2 shadow-md hover:bg-white">
            <ChevronLeft className="h-5 w-5 md:h-6 md:w-6" />
          </button>
          <button onClick={() => go(i + 1)} aria-label="Next"
            className="absolute right-2 md:right-6 top-1/2 z-10 -translate-y-1/2 rounded-full bg-white/90 p-2 shadow-md hover:bg-white">
            <ChevronRight className="h-5 w-5 md:h-6 md:w-6" />
          </button>
          <div className="absolute bottom-3 left-1/2 z-10 flex -translate-x-1/2 gap-2">
            {banners.map((b, n) => (
              <button key={b.id} onClick={() => go(n)} aria-label={`Banner ${n + 1}`}
                className={`h-2 rounded-full transition-all ${n === i ? 'w-6 bg-white' : 'w-2 bg-white/60'}`} />
            ))}
          </div>
        </>
      )}
    </div>
  );
};

export default BannerCarousel;

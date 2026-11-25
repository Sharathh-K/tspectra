import React, { useEffect, useRef, useState } from 'react';

const destinations = [
  ['field-map', 'Field map', 'M3 6l6-3 6 3 6-3v15l-6 3-6-3-6 3z M9 3v15 M15 6v15'],
  ['field-summary', 'Field summary', 'M4 20V4 M4 20h16 M8 16v-4 M13 16V7 M18 16v-7'],
  ['map-layers', 'Map layers', 'M3 8l9-5 9 5-9 5z M3 12l9 5 9-5 M3 16l9 5 9-5'],
  ['pixel-inspector', 'Pixel inspector', 'M4 9V4h5 M15 4h5v5 M20 15v5h-5 M9 20H4v-5 M9 9h6v6H9z'],
];
const themeKey = 'terraspectra.theme';

function initialTheme() {
  try { return localStorage.getItem(themeKey) === 'light' ? 'light' : 'dark'; }
  catch { return 'dark'; }
}

export default function Navigation({ ready }) {
  const [theme, setTheme] = useState(initialTheme);
  const [open, setOpen] = useState(false);
  const [active, setActive] = useState(() => window.location.hash.slice(1) || 'field-map');
  const rail = useRef(null);
  const trigger = useRef(null);

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    try { localStorage.setItem(themeKey, theme); } catch { /* The current session still has a theme. */ }
  }, [theme]);

  useEffect(() => {
    const update = () => setActive(window.location.hash.slice(1) || 'field-map');
    window.addEventListener('hashchange', update);
    return () => window.removeEventListener('hashchange', update);
  }, []);

  useEffect(() => {
    if (!open) return;
    const escape = event => {
      if (event.key === 'Escape') {
        setOpen(false);
        trigger.current?.focus();
      }
    };
    const outside = event => {
      if (!rail.current?.contains(event.target)) setOpen(false);
    };
    document.addEventListener('keydown', escape);
    document.addEventListener('pointerdown', outside);
    return () => {
      document.removeEventListener('keydown', escape);
      document.removeEventListener('pointerdown', outside);
    };
  }, [open]);

  return <div className="rail" ref={rail}>
    <div className="rail-head">
      <div className="brand"><img src="/favicon.svg" width="34" height="34" alt=""/>TerraSpectra</div>
      <button ref={trigger} className="menu-trigger" type="button" aria-controls="field-menu"
        aria-expanded={open} onClick={() => setOpen(!open)}>Menu</button>
    </div>
    <div className={'rail-body' + (open ? ' is-open' : '')} id="field-menu">
      <nav aria-label="Field navigation">
        {ready && destinations.map(([id, label, path]) =>
          <a key={id} href={'#' + id} aria-current={active === id ? 'location' : undefined}
            onClick={() => { setOpen(false); document.getElementById(id)?.focus({preventScroll:true}); }}>
            <svg viewBox="0 0 24 24" width="19" height="19" fill="none" stroke="currentColor"
              strokeWidth="1.6" strokeLinejoin="round" strokeLinecap="round" aria-hidden="true"><path d={path}/></svg>
            {label}
          </a>)}
      </nav>
      <label className="appearance">Dark mode
        <input type="checkbox" role="switch" checked={theme === 'dark'}
          onChange={e => setTheme(e.target.checked ? 'dark' : 'light')}/>
      </label>
    </div>
  </div>;
}

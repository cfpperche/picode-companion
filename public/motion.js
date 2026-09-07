/* Shared kinematics for the viewer and offline verification. No hardware I/O. */
((root) => {
  'use strict';
  const ratio = 1.5;
  const R = 72 / Math.PI, r = 48 / Math.PI;
  let lo = R + r, hi = 100;
  for (let i = 0; i < 60; i++) {
    const c = (lo + hi) / 2;
    const a = Math.asin((R - r) / c);
    const length = 2 * Math.sqrt(c * c - (R - r) ** 2) + Math.PI * (R + r) + 2 * a * (R - r);
    if (length < 220) lo = c; else hi = c;
  }
  const driveX = -(lo + hi) / 2;
  function clamp(value) {
    if (!Number.isFinite(value)) throw new TypeError('Head angle must be finite');
    return Math.max(-180, Math.min(180, value));
  }
  function transform(point, joint, degrees) {
    const [x,y,z] = point;
    if (joint === 'fixed' || !joint) return [...point];
    const factor = joint === 'drive' ? 1 / ratio : joint === 'flex' ? Math.max(0, Math.min(1, (z - 42) / 46)) : 1;
    const a = clamp(degrees) * Math.PI / 180 * factor;
    const px = joint === 'drive' ? driveX : 0;
    return [px + Math.cos(a)*(x-px) - Math.sin(a)*(y-118), 118 + Math.sin(a)*(x-px) + Math.cos(a)*(y-118), z];
  }
  root.PiCodeMotion = Object.freeze({ratio,driveX,clamp,transform,servoDegrees: value => 150 + clamp(value) / ratio});
})(typeof window === 'undefined' ? globalThis : window);

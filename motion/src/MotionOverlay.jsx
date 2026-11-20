import React from 'react';
import {AbsoluteFill, Easing, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';

const themes = {
  clean: {
    accent: '#a8f0d1',
    accentGlow: 'rgba(76, 239, 188, 0.32)',
    card: 'rgba(15, 20, 27, 0.83)',
    kicker: 'QUICK EXPLAINER',
  },
  gta: {
    accent: '#21f4da',
    accentGlow: 'rgba(33, 244, 218, 0.45)',
    card: 'rgba(7, 12, 16, 0.78)',
    kicker: 'CLIP HIGHLIGHT',
  },
};

const safeInterpolate = (value, input, output) =>
  interpolate(value, input, output, {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.cubic),
  });

const Corner = ({style, color}) => (
  <div style={{position: 'absolute', width: 50, height: 50, borderColor: color, opacity: 0.8, ...style}} />
);

export const MotionOverlay = ({title, style = 'gta', durationSeconds = 20, captions = [], includeMotion = true}) => {
  const frame = useCurrentFrame();
  const {fps, width, height} = useVideoConfig();
  const theme = themes[style] ?? themes.gta;
  const durationFrames = Math.max(1, Math.round(durationSeconds * fps));
  const enter = spring({frame, fps, config: {damping: 18, stiffness: 130, mass: 0.7}});
  const cardOpacity = safeInterpolate(frame, [0, 8, 72, 96], [0, 1, 1, 0]);
  const cardY = interpolate(enter, [0, 1], [38, 0]);
  const railWidth = safeInterpolate(frame, [0, durationFrames - 1], [0, 1]);
  const now = frame / fps;
  const phrase = captions.find((item) => now >= item.start && now <= item.end);

  return (
    <AbsoluteFill style={{backgroundColor: 'transparent', fontFamily: 'Arial, sans-serif', color: '#fff'}}>
      {includeMotion && style === 'gta' && (
        <>
          <Corner color={theme.accent} style={{left: 42, top: 52, borderLeft: `5px solid ${theme.accent}`, borderTop: `5px solid ${theme.accent}`}} />
          <Corner color={theme.accent} style={{right: 42, top: 52, borderRight: `5px solid ${theme.accent}`, borderTop: `5px solid ${theme.accent}`}} />
          <Corner color={theme.accent} style={{left: 42, bottom: 102, borderLeft: `5px solid ${theme.accent}`, borderBottom: `5px solid ${theme.accent}`}} />
          <Corner color={theme.accent} style={{right: 42, bottom: 102, borderRight: `5px solid ${theme.accent}`, borderBottom: `5px solid ${theme.accent}`}} />
        </>
      )}

      {includeMotion && <div style={{
        position: 'absolute', left: 66, bottom: 360, width: width - 132, height: 202,
        boxSizing: 'border-box', padding: '28px 34px 24px 42px', background: theme.card,
        borderLeft: `10px solid ${theme.accent}`, boxShadow: `0 8px 28px ${theme.accentGlow}`,
        opacity: cardOpacity, transform: `translateY(${cardY}px) scale(${0.97 + enter * 0.03})`,
      }}>
        <div style={{fontSize: 28, fontWeight: 800, letterSpacing: 3, color: theme.accent, marginBottom: 18}}>
          {theme.kicker}
        </div>
        <div style={{fontSize: 76, lineHeight: 1.02, fontWeight: 900, letterSpacing: 1.5,
          textShadow: '0 3px 14px rgba(0,0,0,.55)', textTransform: 'uppercase'}}>
          {title}
        </div>
      </div>}

      {phrase && (
        <div style={{
          position: 'absolute', left: 54, right: 54, bottom: 210, minHeight: 92,
          display: 'flex', justifyContent: 'center', alignItems: 'center', flexWrap: 'nowrap',
          gap: 18, padding: '12px 24px', boxSizing: 'border-box',
          background: 'rgba(0,0,0,.46)', borderRadius: 16,
          fontSize: phrase.fontSize || 68, fontWeight: 900, letterSpacing: 1.2,
          lineHeight: 1.1, textAlign: 'center', textShadow: '0 4px 14px rgba(0,0,0,.9)',
          WebkitTextStroke: '1px rgba(0,0,0,.5)',
        }}>
          {phrase.words.map((word, index) => {
            const visible = now >= word.start;
            const active = visible && now < word.end;
            const progress = safeInterpolate(frame, [word.start * fps, word.start * fps + 8], [1.16, 1]);
            return (
              <span key={`${word.start}-${index}`} style={{
                color: active ? theme.accent : '#fff', opacity: visible ? 1 : 0,
                transform: `scale(${progress})`, display: 'inline-block',
              }}>{word.text}</span>
            );
          })}
        </div>
      )}

      {includeMotion && <div style={{position: 'absolute', left: 66, right: 66, bottom: 66, height: 4, background: 'rgba(255,255,255,.36)'}}>
        <div style={{width: `${railWidth * 100}%`, height: '100%', background: theme.accent, boxShadow: `0 0 12px ${theme.accentGlow}`}} />
      </div>}
    </AbsoluteFill>
  );
};

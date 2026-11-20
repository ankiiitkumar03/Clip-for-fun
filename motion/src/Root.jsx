import React from 'react';
import {Composition} from 'remotion';
import {MotionOverlay} from './MotionOverlay.jsx';

const defaults = {
  title: 'GAMEPLAY HIGHLIGHT',
  style: 'gta',
  durationSeconds: 20,
  captions: [],
};

export const RemotionRoot = () => (
  <Composition
    id="MotionOverlay"
    component={MotionOverlay}
    durationInFrames={600}
    fps={30}
    width={1080}
    height={1920}
    defaultProps={defaults}
    calculateMetadata={({props}) => ({
      durationInFrames: Math.max(1, Math.ceil((props.durationSeconds || 20) * (props.fps || 30))),
      fps: props.fps || 30,
      width: props.width || 1080,
      height: props.height || 1920,
    })}
  />
);

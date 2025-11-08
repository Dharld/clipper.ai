import { useEffect, useRef } from 'react';

interface WaveformVisualizerProps {
  amplitude?: number;
  speed?: number;
  color?: string;
}

export function WaveformVisualizer({ amplitude = 24, speed = 0.02, color = '#9d4dff' }: WaveformVisualizerProps) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const frameRef = useRef<number>();
  const phaseRef = useRef(0);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const context = canvas.getContext('2d');
    if (!context) return;

    const draw = () => {
      const { width, height } = canvas;
      context.clearRect(0, 0, width, height);
      context.lineWidth = 2;
      context.strokeStyle = color;
      context.beginPath();
      const mid = height / 2;
      for (let x = 0; x < width; x++) {
        const y = mid + Math.sin(x * 0.02 + phaseRef.current) * amplitude;
        context.lineTo(x, y);
      }
      context.stroke();
      phaseRef.current += speed * 10;
      frameRef.current = requestAnimationFrame(draw);
    };

    const resize = () => {
      const rect = canvas.getBoundingClientRect();
      canvas.width = rect.width * devicePixelRatio;
      canvas.height = rect.height * devicePixelRatio;
      context.scale(devicePixelRatio, devicePixelRatio);
    };

    resize();
    draw();

    return () => {
      if (frameRef.current) cancelAnimationFrame(frameRef.current);
    };
  }, [amplitude, color, speed]);

  return <canvas ref={canvasRef} className="h-24 w-full" role="img" aria-label="Waveform animation" />;
}

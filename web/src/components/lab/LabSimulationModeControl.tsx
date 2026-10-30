"use client";

export type LabSimulationMode = 'ground' | 'vertical-flight';

export function LabSimulationModeControl({ value, onChange }: { value: LabSimulationMode; onChange: (mode: LabSimulationMode) => void }) {
  return <div className="lab-simulation-mode" role="group" aria-label="Simulation mode">
    <span>Simulation mode</span>
    <button type="button" aria-pressed={value === 'ground'} onClick={() => onChange('ground')}>Ground exploration</button>
    <button type="button" aria-pressed={value === 'vertical-flight'} onClick={() => onChange('vertical-flight')}>Vertical flight verification</button>
  </div>;
}

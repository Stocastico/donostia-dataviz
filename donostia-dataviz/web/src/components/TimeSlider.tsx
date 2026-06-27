interface Props {
  periods: string[];
  index: number;
  onChange: (index: number) => void;
}

/** Year/period slider. Hidden when a metric has a single (snapshot) period. */
export function TimeSlider({ periods, index, onChange }: Props) {
  if (periods.length <= 1) {
    return (
      <div className="time-slider single">
        <span className="control-label">Periodo</span>
        <span className="period-value">{periods[0] ?? "—"}</span>
      </div>
    );
  }
  return (
    <div className="time-slider">
      <span className="control-label">
        Anno <strong>{periods[index]}</strong>
      </span>
      <input
        type="range"
        min={0}
        max={periods.length - 1}
        value={index}
        step={1}
        onChange={(e) => onChange(Number(e.target.value))}
        aria-label="Seleziona anno"
      />
      <div className="slider-ends">
        <span>{periods[0]}</span>
        <span>{periods[periods.length - 1]}</span>
      </div>
    </div>
  );
}

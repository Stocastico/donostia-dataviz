interface Props {
  periods: string[];
  index: number;
  onChange: (index: number) => void;
  playing?: boolean;
  onTogglePlay?: () => void;
}

/** Year/period slider, with an optional "▶ Play" button (VIZ-8) that steps
 * through every period automatically. Hidden when a metric has a single
 * (snapshot) period — there's nothing to slide or animate. */
export function TimeSlider({ periods, index, onChange, playing, onTogglePlay }: Props) {
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
      <div className="time-slider-row">
        {onTogglePlay && (
          <button
            type="button"
            className="play-button"
            onClick={onTogglePlay}
            aria-label={playing ? "Pausa" : "Riproduci l'evoluzione temporale"}
            aria-pressed={playing}
          >
            {playing ? "⏸" : "▶"}
          </button>
        )}
        <input
          type="range"
          min={0}
          max={periods.length - 1}
          value={index}
          step={1}
          onChange={(e) => onChange(Number(e.target.value))}
          aria-label="Seleziona anno"
        />
      </div>
      <div className="slider-ends">
        <span>{periods[0]}</span>
        <span>{periods[periods.length - 1]}</span>
      </div>
    </div>
  );
}

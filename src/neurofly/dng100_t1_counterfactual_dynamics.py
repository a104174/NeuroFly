"""Isolated six-state counterfactual rate model, never a biological sign authority."""

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class RateParameters:
    tau_s: float = 0.02
    gain: float = 1.0
    threshold: float = 7.5
    cap: float = 200.0

    def validate(self):
        values = [self.tau_s, self.gain, self.threshold, self.cap]
        if not np.isfinite(values).all() or any(x <= 0 for x in values):
            raise ValueError("invalid positive finite rate parameters")


def derivative(state, weights, drive, parameters):
    """Rows are postsynaptic; all derivatives use the same current state."""
    return (
        np.maximum(
            parameters.cap
            * np.tanh(
                parameters.gain
                / parameters.cap
                * (weights @ state + drive - parameters.threshold)
            ),
            0.0,
        )
        - state
    ) / parameters.tau_s


def rk4_step(state, weights, drive, parameters, dt):
    k1 = derivative(state, weights, drive, parameters)
    k2 = derivative(state + dt * k1 / 2, weights, drive, parameters)
    k3 = derivative(state + dt * k2 / 2, weights, drive, parameters)
    k4 = derivative(state + dt * k3, weights, drive, parameters)
    return state + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)


def simulate(weights, inputs, parameters, initial, dt, sample_dt, duration, interval):
    """Held input per interval; no clipping, fallback values or body actuation."""
    parameters.validate()
    state = np.array(initial, dtype=np.float64)
    w, b = np.asarray(weights), np.asarray(inputs)
    if (
        state.ndim != 1
        or w.shape != (len(state), len(state))
        or b.shape != (len(state), 2)
        or not all(np.isfinite(x).all() for x in (state, w, b))
        or np.any(state < 0)
        or np.any(state > parameters.cap)
    ):
        raise ValueError("invalid state/matrix")
    if (
        not np.isfinite([dt, sample_dt, duration, *interval]).all()
        or not 0 < dt <= sample_dt <= duration
        or not 0 <= interval[0] <= interval[1] <= duration
    ):
        raise ValueError("invalid time configuration")
    ratios = [sample_dt / dt, duration / sample_dt, *[t / dt for t in interval]]
    if any(abs(r - round(r)) > 1e-8 for r in ratios):
        raise ValueError("time boundaries must align with integration grid")
    stride, count = round(sample_dt / dt), round(duration / sample_dt)
    start, end = [round(t / dt) for t in interval]
    states = [state.tolist()]
    zero, active = np.zeros(len(state)), b @ np.full(2, 20.0)
    status = "COMPLETED"
    for tick in range(count * stride):
        drive = active if start <= tick < end else zero
        state = rk4_step(state, w, drive, parameters, dt)
        if (
            not np.isfinite(state).all()
            or np.any(state < -1e-8)
            or np.any(state > parameters.cap + 1e-8)
        ):
            status = "NUMERICAL_DIVERGENCE"
            break
        if (tick + 1) % stride == 0:
            states.append(state.tolist())
    times = np.arange(len(states)) * sample_dt
    source_rates = [
        [20.0, 20.0] if interval[0] <= t < interval[1] else [0.0, 0.0] for t in times
    ]
    last_drive = active if start <= count * stride - 1 < end else zero
    residual_by_neuron = (
        np.abs(derivative(state, w, last_drive, parameters)).tolist()
        if status == "COMPLETED"
        else None
    )
    residual = float(max(residual_by_neuron)) if status == "COMPLETED" else None
    return {
        "termination": status,
        "times_s": times.tolist(),
        "states": states,
        "prescribed_source_rates": source_rates,
        "final_residual": residual,
        "final_residual_by_neuron": residual_by_neuron,
    }


def cell_metrics(times, values, rules):
    """Independent temporal, spectral and recurrence checks, not a CPG claim."""
    t, y = np.asarray(times), np.asarray(values)
    if (
        t.ndim != 1
        or y.shape != t.shape
        or len(t) < 4
        or not np.isfinite(t).all()
        or not np.isfinite(y).all()
        or np.any(np.diff(t) <= 0)
        or not np.allclose(np.diff(t), t[1] - t[0], rtol=1e-8, atol=1e-12)
    ):
        raise ValueError("invalid sampled trace")
    mask = t >= rules["tail_start_s"]
    tail, tt = y[mask], t[mask]
    if len(tail) < 4:
        raise ValueError("insufficient tail")
    amplitude = float(np.ptp(tail))
    middle = len(tail) // 2
    a1, a2 = float(np.ptp(tail[:middle])), float(np.ptp(tail[middle:]))
    ratio = a2 / a1 if a1 > rules["amplitude_floor"] else None
    peaks = np.where((tail[1:-1] >= tail[:-2]) & (tail[1:-1] > tail[2:]))[0] + 1
    peaks = peaks[tail[peaks] >= np.min(tail) + amplitude / 2]
    periods = np.diff(tt[peaks])
    period = float(np.mean(periods)) if len(periods) else None
    cv = float(np.std(periods) / period) if period else None
    centered = tail - np.mean(tail)
    power = np.abs(np.fft.rfft(centered)) ** 2
    power[0] = 0
    peak_bin = int(np.argmax(power))
    spectral = (
        float(np.sum(power[max(1, peak_bin - 1) : peak_bin + 2]) / np.sum(power))
        if np.sum(power) > 0
        else 0.0
    )
    lag = round(period / (t[1] - t[0])) if period else 0
    autocorrelation = None
    if 0 < lag < len(tail) - 2:
        x, z = tail[:-lag], tail[lag:]
        if np.std(x) > 0 and np.std(z) > 0:
            autocorrelation = float(np.corrcoef(x, z)[0, 1])
    oscillation = bool(
        amplitude > rules["amplitude_floor"]
        and len(periods) >= rules["min_complete_cycles"]
        and rules["period_min_s"] <= period <= rules["period_max_s"]
        and cv <= rules["period_cv_max"]
        and ratio is not None
        and rules["half_amplitude_ratio_min"]
        <= ratio
        <= rules["half_amplitude_ratio_max"]
        and spectral >= rules["spectral_fraction_min"]
        and autocorrelation is not None
        and autocorrelation >= rules["autocorrelation_min"]
    )
    early = float(np.ptp(y[~mask]))
    return {
        "tail_amplitude": amplitude,
        "early_amplitude": early,
        "complete_cycles": len(periods),
        "period_s": period,
        "period_cv": cv,
        "half_amplitude_ratio": ratio,
        "spectral_fraction": spectral,
        "autocorrelation": autocorrelation,
        "sustained": oscillation,
    }


def classify(metrics, residual, rules):
    if any(x["sustained"] for x in metrics):
        return "SUSTAINED_MODEL_OSCILLATION"
    if all(x["tail_amplitude"] <= rules["amplitude_floor"] for x in metrics):
        if residual <= rules["fixed_residual_max"]:
            return "STABLE_FIXED_POINT"
    if all(
        x["tail_amplitude"] <= rules["amplitude_floor"]
        or x["tail_amplitude"] < 0.5 * x["early_amplitude"]
        for x in metrics
    ):
        return "TRANSIENT"
    return "INCONCLUSIVE"

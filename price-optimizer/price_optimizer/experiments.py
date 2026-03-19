"""Price experiment tracking stored in ~/.book-data/experiments.json."""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional
from .models import Experiment


def _load_experiments(path: str) -> List[Experiment]:
    """Load experiments from JSON file."""
    p = Path(path)
    if not p.exists():
        return []
    try:
        data = json.loads(p.read_text())
        experiments = []
        for e in data.get('experiments', []):
            experiments.append(Experiment(
                asin=e['asin'],
                prices=e.get('prices', []),
                duration_days=e.get('duration_days', 14),
                started_at=e.get('started_at', ''),
                current_price_index=e.get('current_price_index', 0),
                status=e.get('status', 'running'),
            ))
        return experiments
    except (json.JSONDecodeError, KeyError):
        return []


def _save_experiments(path: str, experiments: List[Experiment]):
    """Save experiments to JSON file."""
    data = {
        'experiments': [
            {
                'asin': e.asin,
                'prices': e.prices,
                'duration_days': e.duration_days,
                'started_at': e.started_at,
                'current_price_index': e.current_price_index,
                'status': e.status,
            }
            for e in experiments
        ]
    }
    Path(path).write_text(json.dumps(data, indent=2))


def start_experiment(path: str, asin: str, prices: List[float],
                     duration_days: int = 14) -> Experiment:
    """Start a new price experiment.

    Args:
        path: Path to experiments.json
        asin: Book ASIN
        prices: List of prices to test (each for duration_days)
        duration_days: Days to run each price

    Returns:
        The created Experiment
    """
    experiments = _load_experiments(path)

    # Check for existing running experiment on this ASIN
    for e in experiments:
        if e.asin == asin and e.status == 'running':
            raise ValueError(f'Experiment already running for {asin}. '
                           f'Cancel it first or wait for completion.')

    exp = Experiment(
        asin=asin,
        prices=prices,
        duration_days=duration_days,
        started_at=datetime.now().strftime('%Y-%m-%d'),
        current_price_index=0,
        status='running',
    )
    experiments.append(exp)
    _save_experiments(path, experiments)
    return exp


def get_experiments(path: str, asin: str = None,
                    status: str = None) -> List[Experiment]:
    """Get experiments, optionally filtered by ASIN and/or status."""
    experiments = _load_experiments(path)
    if asin:
        experiments = [e for e in experiments if e.asin == asin]
    if status:
        experiments = [e for e in experiments if e.status == status]
    return experiments


def update_experiment_status(path: str, experiments: List[Experiment] = None):
    """Check running experiments and update status based on dates.

    Auto-completes experiments where all price periods have elapsed.
    """
    if experiments is None:
        experiments = _load_experiments(path)

    today = datetime.now()
    changed = False

    for exp in experiments:
        if exp.status != 'running':
            continue

        try:
            start = datetime.strptime(exp.started_at, '%Y-%m-%d')
        except ValueError:
            continue

        total_days = exp.duration_days * len(exp.prices)
        end_date = start + timedelta(days=total_days)

        if today >= end_date:
            exp.status = 'completed'
            changed = True
        else:
            # Update current price index
            days_elapsed = (today - start).days
            new_index = min(days_elapsed // exp.duration_days,
                          len(exp.prices) - 1)
            if new_index != exp.current_price_index:
                exp.current_price_index = new_index
                changed = True

    if changed:
        _save_experiments(path, experiments)

    return experiments


def cancel_experiment(path: str, asin: str) -> bool:
    """Cancel a running experiment for the given ASIN.

    Returns True if an experiment was cancelled.
    """
    experiments = _load_experiments(path)
    cancelled = False
    for exp in experiments:
        if exp.asin == asin and exp.status == 'running':
            exp.status = 'cancelled'
            cancelled = True
    if cancelled:
        _save_experiments(path, experiments)
    return cancelled


def get_experiment_schedule(experiment: Experiment) -> List[dict]:
    """Get the schedule for an experiment showing price periods.

    Returns list of dicts with price, start_date, end_date, status.
    """
    schedule = []
    try:
        start = datetime.strptime(experiment.started_at, '%Y-%m-%d')
    except ValueError:
        return schedule

    today = datetime.now()

    for i, price in enumerate(experiment.prices):
        period_start = start + timedelta(days=i * experiment.duration_days)
        period_end = period_start + timedelta(days=experiment.duration_days)

        if today < period_start:
            status = 'upcoming'
        elif today >= period_end:
            status = 'completed'
        else:
            status = 'active'

        schedule.append({
            'price': price,
            'start_date': period_start.strftime('%Y-%m-%d'),
            'end_date': period_end.strftime('%Y-%m-%d'),
            'status': status,
        })

    return schedule

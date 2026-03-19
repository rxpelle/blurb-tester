"""Tests for price experiment tracking."""

import json
import os
import pytest
from datetime import datetime, timedelta
from price_optimizer.experiments import (
    start_experiment, get_experiments, update_experiment_status,
    cancel_experiment, get_experiment_schedule, _load_experiments,
    _save_experiments,
)
from price_optimizer.models import Experiment


class TestStartExperiment:

    def test_creates_experiment(self, experiments_file):
        exp = start_experiment(experiments_file, 'B0GMRN61MG', [2.99, 4.99], 14)
        assert exp.asin == 'B0GMRN61MG'
        assert exp.prices == [2.99, 4.99]
        assert exp.duration_days == 14
        assert exp.status == 'running'
        assert exp.current_price_index == 0

    def test_persists_to_file(self, experiments_file):
        start_experiment(experiments_file, 'B0GMRN61MG', [2.99, 4.99], 14)

        with open(experiments_file) as f:
            data = json.load(f)
        assert len(data['experiments']) == 1
        assert data['experiments'][0]['asin'] == 'B0GMRN61MG'

    def test_rejects_duplicate_running(self, experiments_file):
        start_experiment(experiments_file, 'B0GMRN61MG', [2.99, 4.99], 14)
        with pytest.raises(ValueError, match='already running'):
            start_experiment(experiments_file, 'B0GMRN61MG', [0.99, 2.99], 7)

    def test_allows_different_asin(self, experiments_file):
        start_experiment(experiments_file, 'B0GMRN61MG', [2.99, 4.99], 14)
        exp2 = start_experiment(experiments_file, 'B0TEST12345', [0.99, 2.99], 7)
        assert exp2.asin == 'B0TEST12345'

    def test_three_prices(self, experiments_file):
        exp = start_experiment(experiments_file, 'B0GMRN61MG', [0.99, 2.99, 4.99], 7)
        assert len(exp.prices) == 3

    def test_sets_start_date(self, experiments_file):
        exp = start_experiment(experiments_file, 'B0GMRN61MG', [2.99, 4.99], 14)
        assert exp.started_at == datetime.now().strftime('%Y-%m-%d')


class TestGetExperiments:

    def test_filter_by_asin(self, experiments_file_with_data):
        results = get_experiments(experiments_file_with_data, asin='B0GMRN61MG')
        assert len(results) == 1
        assert results[0].asin == 'B0GMRN61MG'

    def test_filter_by_status(self, experiments_file_with_data):
        results = get_experiments(experiments_file_with_data, status='completed')
        assert len(results) == 1
        assert results[0].asin == 'B0TEST12345'

    def test_no_filter(self, experiments_file_with_data):
        results = get_experiments(experiments_file_with_data)
        assert len(results) == 2

    def test_empty_file(self, experiments_file):
        results = get_experiments(experiments_file)
        assert results == []

    def test_nonexistent_file(self):
        results = get_experiments('/tmp/nonexistent_experiments.json')
        assert results == []


class TestUpdateStatus:

    def test_completes_expired_experiment(self, experiments_file):
        # Create an experiment that started long ago
        past_date = (datetime.now() - timedelta(days=100)).strftime('%Y-%m-%d')
        exp = Experiment(
            asin='B0TEST', prices=[2.99, 4.99],
            duration_days=14, started_at=past_date,
            current_price_index=0, status='running',
        )
        _save_experiments(experiments_file, [exp])

        results = update_experiment_status(experiments_file)
        assert results[0].status == 'completed'

    def test_keeps_running_if_not_expired(self, experiments_file):
        today = datetime.now().strftime('%Y-%m-%d')
        exp = Experiment(
            asin='B0TEST', prices=[2.99, 4.99],
            duration_days=14, started_at=today,
            current_price_index=0, status='running',
        )
        _save_experiments(experiments_file, [exp])

        results = update_experiment_status(experiments_file)
        assert results[0].status == 'running'

    def test_ignores_already_completed(self, experiments_file):
        exp = Experiment(
            asin='B0TEST', prices=[2.99, 4.99],
            duration_days=14, started_at='2025-01-01',
            current_price_index=1, status='completed',
        )
        _save_experiments(experiments_file, [exp])

        results = update_experiment_status(experiments_file)
        assert results[0].status == 'completed'


class TestCancelExperiment:

    def test_cancels_running(self, experiments_file_with_data):
        result = cancel_experiment(experiments_file_with_data, 'B0GMRN61MG')
        assert result is True

        exps = get_experiments(experiments_file_with_data, asin='B0GMRN61MG')
        assert exps[0].status == 'cancelled'

    def test_returns_false_if_not_found(self, experiments_file_with_data):
        result = cancel_experiment(experiments_file_with_data, 'B0NONEXISTENT')
        assert result is False

    def test_does_not_cancel_completed(self, experiments_file_with_data):
        result = cancel_experiment(experiments_file_with_data, 'B0TEST12345')
        assert result is False  # Already completed


class TestExperimentSchedule:

    def test_schedule_generation(self):
        exp = Experiment(
            asin='B0TEST', prices=[2.99, 4.99],
            duration_days=14, started_at='2026-01-01',
            current_price_index=0, status='running',
        )
        schedule = get_experiment_schedule(exp)
        assert len(schedule) == 2
        assert schedule[0]['price'] == 2.99
        assert schedule[0]['start_date'] == '2026-01-01'
        assert schedule[0]['end_date'] == '2026-01-15'
        assert schedule[1]['price'] == 4.99
        assert schedule[1]['start_date'] == '2026-01-15'
        assert schedule[1]['end_date'] == '2026-01-29'

    def test_all_completed_for_old_experiment(self):
        exp = Experiment(
            asin='B0TEST', prices=[2.99, 4.99],
            duration_days=14, started_at='2025-01-01',
            current_price_index=1, status='completed',
        )
        schedule = get_experiment_schedule(exp)
        for period in schedule:
            assert period['status'] == 'completed'

    def test_three_price_schedule(self):
        exp = Experiment(
            asin='B0TEST', prices=[0.99, 2.99, 4.99],
            duration_days=7, started_at='2026-01-01',
        )
        schedule = get_experiment_schedule(exp)
        assert len(schedule) == 3
        assert schedule[2]['start_date'] == '2026-01-15'
        assert schedule[2]['end_date'] == '2026-01-22'


class TestLoadSaveRoundtrip:

    def test_roundtrip(self, experiments_file):
        exps = [
            Experiment(asin='A', prices=[1.99, 2.99], duration_days=7,
                      started_at='2026-01-01', status='running'),
            Experiment(asin='B', prices=[4.99], duration_days=14,
                      started_at='2026-02-01', status='completed'),
        ]
        _save_experiments(experiments_file, exps)
        loaded = _load_experiments(experiments_file)

        assert len(loaded) == 2
        assert loaded[0].asin == 'A'
        assert loaded[0].prices == [1.99, 2.99]
        assert loaded[1].status == 'completed'

    def test_load_malformed_json(self, experiments_file):
        with open(experiments_file, 'w') as f:
            f.write('not json')
        result = _load_experiments(experiments_file)
        assert result == []

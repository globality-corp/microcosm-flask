from datetime import datetime, timedelta
from logging import Logger
from tracemalloc import start, take_snapshot

from microcosm.api import binding, defaults, typed
from microcosm.config.types import boolean


@binding("memory_profiler")
@defaults(
    enabled=typed(boolean, False),
    report_size_lines=typed(int, 10),
    sampling_interval_min=typed(int, 10),
)
class MemoryProfiler:
    logger: Logger

    def __init__(self, graph):
        self.enabled = graph.config.memory_profiler.enabled
        self.report_size_lines = graph.config.memory_profiler.report_size_lines
        self.logger = graph.logger

        self.sampling_interval_min = graph.config.memory_profiler.sampling_interval_min
        self.last_sampling_time_delta = timedelta(minutes=self.sampling_interval_min)

        self.last_sampling_time = datetime.now()

        if not self.enabled:
            self.logger.info("Skipping initialization because memory profiling is not enabled!")
            return

        start()
        self.origin_snapshot = take_snapshot()

    def snapshot_at_intervals(self, func):
        def maybe_snapshot(*args, **kwargs):
            result = func(*args, **kwargs)
            if not self.enabled:
                self.logger.debug("Memory profiling is disabled. Please enable to get snapshots.")
                return result

            now = self.get_now()
            if now - self.last_sampling_time > self.last_sampling_time_delta:
                self.take_snapshot(now)

            return result
        return maybe_snapshot

    def take_snapshot(self, current_time):
        latest_snapshot = take_snapshot()
        difference = latest_snapshot.compare_to(self.origin_snapshot, "lineno")
        top_ten = difference[:self.report_size_lines]
        worst_offenders = "\n".join([str(memory_item) for memory_item in top_ten])
        self.logger.info(f"Memory snapshot: \n {worst_offenders}")
        self.last_sampling_time = current_time

    def get_now(self):
        """
        Wrap datetime.now for easier mocking.
        """
        return datetime.now()

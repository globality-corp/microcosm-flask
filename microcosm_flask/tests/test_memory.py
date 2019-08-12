from datetime import datetime, timedelta
from unittest.mock import patch

from hamcrest import assert_that, equal_to, is_
from microcosm.api import create_object_graph, load_from_dict


def noop():
    pass


class TestMemorySampling:
    """
    Test capturing of memory info on API requests.

    """
    def setup(self):
        self.loader = load_from_dict(
            memory_profiler=dict(
                enabled="true",
            ),
        )
        self.graph = create_object_graph("example", testing=True, debug=True, loader=self.loader)
        self.graph.use(
            "flask",
            "memory_profiler",
        )

        self.now = datetime.now()
        self.last_sampling_time = self.now - timedelta(minutes=5)
        self.graph.memory_profiler.last_sampling_time = self.last_sampling_time
        print(self.graph.memory_profiler.last_sampling_time_delta)

    def test_should_take_snapshot(self):
        with patch.object(self.graph.memory_profiler, "get_now") as get_now:
            new_now = self.now + timedelta(minutes=15)
            get_now.return_value = new_now

            assert_that(self.graph.memory_profiler.last_sampling_time, is_(equal_to(self.last_sampling_time)))

            decorated = self.graph.memory_profiler.snapshot_at_intervals(noop)
            decorated()

            assert_that(self.graph.memory_profiler.last_sampling_time, is_(equal_to(new_now)))

    def test_should_not_take_snapshot(self):
        with patch.object(self.graph.memory_profiler, "get_now") as get_now:
            new_now = self.now + timedelta(minutes=1)
            get_now.return_value = new_now

            assert_that(self.graph.memory_profiler.last_sampling_time, is_(equal_to(self.last_sampling_time)))

            decorated = self.graph.memory_profiler.snapshot_at_intervals(noop)
            decorated()

            assert_that(self.graph.memory_profiler.last_sampling_time, is_(equal_to(self.last_sampling_time)))

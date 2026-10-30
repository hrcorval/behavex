import json
import os
import signal
import sys
import threading
from concurrent.futures import CancelledError, Future
from concurrent.futures.process import BrokenProcessPool

from behavex import host_messages
from behavex.conf_mgr import ConfigRun, get_param
from behavex.global_vars import global_vars
from behavex.outputs.report_json import get_feature_json_skeleton
from behavex.progress_bar import create_progress_bar
from behavex.run_state import state
from behavex.utils import (
    create_execution_complete_callback_function,
    get_feature_and_scenario_line,
    get_feature_order,
    get_scenario_order,
    print_parallel,
)
from behavex.worker import execute_tests


def _mark_run_stopped_if_requested() -> bool:
    if state.stop_requested:
        state.stopped = True
    return state.stop_requested


def _wait_for_futures(futures, execution_codes):
    """Helper function to wait for futures and handle exceptions"""
    for future in futures:
        if future.cancelled():
            state.stopped = True
            continue
        try:
            future.result()
        except (KeyboardInterrupt, SystemExit):
            # Allow KeyboardInterrupt (Ctrl+C) and SystemExit to propagate to top level
            raise
        except CancelledError:
            state.stopped = True
            continue
        except:
            e = sys.exc_info()[1]
            if isinstance(e, BrokenProcessPool):
                print_parallel('process.pool.broken.main', str(e))
                # Mark as failed execution but continue processing remaining futures
                execution_codes.append(2)
            else:
                print_parallel('parallel.process.error', str(e))
                execution_codes.append(2)
        future.bhx_reported.wait()


def _add_report_callback(future, execution_codes, json_reports):
    # set_result wakes result() before callbacks run, and a stopped pool's shutdown no longer joins them
    future.bhx_reported = threading.Event()
    future.add_done_callback(create_execution_complete_callback_function(
        execution_codes, json_reports, global_vars.progress_bar_instance))
    future.add_done_callback(lambda _: future.bhx_reported.set())


def _submit_unless_stopped(process_pool, fn, **kwargs):
    """Return None once BehaveXRunner.stop() was requested or the pool was shut down."""
    if state.stop_requested:
        state.stopped = True
        return None
    try:
        return process_pool.submit(fn, **kwargs)
    except BrokenProcessPool as error:
        # A worker died: the work fails as a running future does when its worker dies
        failed_future = Future()
        failed_future.set_exception(error)
        return failed_future
    except RuntimeError:
        state.stopped = True
        return None


def launch_by_feature(features,
                      process_pool,
                      lock,
                      show_progress_bar):
    """Launch tests by feature in parallel.

    Args:
        features (dict): Dictionary of features and their scenarios.
        process_pool (ProcessPoolExecutor): Process pool executor.
        lock (Lock): Multiprocessing lock.
        show_progress_bar (bool): Whether to show the progress bar.

    Returns:
        tuple: Execution codes and JSON reports.
    """
    json_reports = []
    execution_codes = []

    # Cache the order_tests parameter to avoid multiple get_param calls
    order_tests_enabled = get_param('order_tests')
    order_tests_strict = get_param('order_tests_strict')
    # If order_tests_strict is enabled, automatically enable order_tests
    order_tests_enabled = order_tests_enabled or order_tests_strict
    order_tag_prefix = get_param('order_tag_prefix') if order_tests_enabled else None

    serial_features = []
    parallel_features = []
    for features_path in features:
        feature = features[features_path][0].feature
        pure_feature_path, scenario_line = get_feature_and_scenario_line(features_path)
        feature_filename = feature.filename if not scenario_line else "{}:{}".format(pure_feature_path, scenario_line)

        feature_info = {"feature_filename": feature_filename,
                       "feature_json_skeleton": get_feature_json_skeleton(feature)}

        # Only calculate feature order if ordering is enabled
        if order_tests_enabled:
            # For feature-level execution, use ORDER tags from the feature itself
            feature_info["feature_order"] = get_feature_order(feature, order_tag_prefix)

        if 'SERIAL' in feature.tags:
            serial_features.append(feature_info)
        else:
            parallel_features.append(feature_info)
    # Sort features by execution order if enabled (only the categorized features that will actually run)
    if order_tests_enabled:
        serial_features.sort(key=lambda f: f.get("feature_order", 9999))
        parallel_features.sort(key=lambda f: f.get("feature_order", 9999))

    if show_progress_bar:
        total_features = len(serial_features) + len(parallel_features)
        global_vars.progress_bar_instance = create_progress_bar(parallel_scheme="feature",
                                                                       total_elements=total_features)
        if global_vars.progress_bar_instance:
            global_vars.progress_bar_instance.start()
    if serial_features:
        print_parallel('feature.serial_execution')
        for serial_feature in serial_features:
            if _mark_run_stopped_if_requested():
                break
            serial_result = _execute_serial_tests(features_path=None,
                                                     feature_filename=serial_feature["feature_filename"],
                                                     feature_json_skeleton=serial_feature["feature_json_skeleton"],
                                                     scenarios_to_run_in_feature=None,
                                                     scenario_line=None,
                                                     multiprocess=True,
                                                     config=ConfigRun(),
                                                     lock=None,
                                                     shared_removed_scenarios=None)
            if serial_result is None:
                break
            execution_code, map_json = serial_result
            json_reports += [map_json]
            execution_codes.append(execution_code)
            state.fire_report_progress(map_json)
            if global_vars.progress_bar_instance:
                global_vars.progress_bar_instance.update()
    print_parallel('feature.running_parallels')

    # Prepare features grouped by order
    if order_tests_strict:
        # Group features by their order value for strict sequential ordering
        features_by_order = {}
        for parallel_feature in parallel_features:
            order = parallel_feature.get("feature_order", 9999)
            if order not in features_by_order:
                features_by_order[order] = []
            features_by_order[order].append(parallel_feature)
    elif order_tests_enabled:
        # Sort features by order but allow parallel execution
        parallel_features.sort(key=lambda f: f.get("feature_order", 9999))
        features_by_order = {9999: parallel_features}
    else:
        # Put all features in a single group for original behavior
        features_by_order = {9999: parallel_features}

    # Execute features by order groups
    for order in sorted(features_by_order.keys()):
        feature_group = features_by_order[order]
        group_futures = []

        # Submit all features of the current order
        for parallel_feature in feature_group:
            feature_filename = parallel_feature["feature_filename"]
            feature_json_skeleton = parallel_feature["feature_json_skeleton"]
            future = _submit_unless_stopped(process_pool, execute_tests,
                                            features_path=None,
                                            feature_filename=feature_filename,
                                            feature_json_skeleton=feature_json_skeleton,
                                            scenarios_to_run_in_feature=None,
                                            scenario_line=None,
                                            multiprocess=True,
                                            config=ConfigRun(),
                                            lock=lock,
                                            shared_removed_scenarios=None)
            if future is None:
                break
            _add_report_callback(future, execution_codes, json_reports)
            group_futures.append(future)

        # Wait for completion of this order group before proceeding to the next
        _wait_for_futures(group_futures, execution_codes)
    return execution_codes, json_reports


def launch_by_scenario(selected_scenarios,
                       process_pool,
                       lock,
                       shared_removed_scenarios,
                       show_progress_bar):
    """Launch tests by scenario in parallel.

    Args:
        selected_scenarios (iterable): (features_path, scenario, scenario_tags) for each scenario to run.
        process_pool (ProcessPoolExecutor): Process pool executor.
        lock (Lock): Multiprocessing lock.
        shared_removed_scenarios (dict): Shared dictionary of removed scenarios.
        show_progress_bar (bool): Whether to show the progress bar.

    Returns:
        tuple: Execution codes and JSON reports.
    """
    json_reports = []
    execution_codes = []
    parallel_scenarios = []
    serial_scenarios = []
    duplicated_scenarios = {}
    total_scenarios_to_run = {}
    features_with_no_scen_desc = []

    # Cache the order_tests parameter to avoid multiple get_param calls
    order_tests_enabled = get_param('order_tests')
    order_tests_strict = get_param('order_tests_strict')
    # If order_tests_strict is enabled, automatically enable order_tests
    order_tests_enabled = order_tests_enabled or order_tests_strict
    order_tag_prefix = get_param('order_tag_prefix') if order_tests_enabled else None
    for features_path, scenario, scenario_tags in selected_scenarios:
        if scenario.name == "":
            features_with_no_scen_desc.append(scenario.filename)
        feature_json_skeleton = get_feature_json_skeleton(scenario)
        feature_filename = scenario.feature.filename
        scenario_information = {"features_path": features_path,
                                "feature_filename": feature_filename,
                                "feature_json_skeleton": feature_json_skeleton,
                                "scenario_line": scenario.line}

        if order_tests_enabled:
            scenario_information["scenario_order"] = get_scenario_order(scenario, order_tag_prefix)
        total_scenarios_to_run[feature_filename] = total_scenarios_to_run.setdefault(feature_filename, 0) + 1
        if 'SERIAL' in scenario_tags:
            if scenario_information in serial_scenarios:
                duplicated_scenarios.setdefault(scenario.filename, []).append(scenario.name)
            serial_scenarios.append(scenario_information)
        else:
            if scenario_information in parallel_scenarios:
                duplicated_scenarios.setdefault(scenario.filename, []).append(scenario.name)
            parallel_scenarios.append(scenario_information)
    state.progress_total = sum(total_scenarios_to_run.values())
    if show_progress_bar:
        global_vars.progress_bar_instance = create_progress_bar(parallel_scheme="scenario",
                                                                       total_elements=state.progress_total)
        if global_vars.progress_bar_instance:
            global_vars.progress_bar_instance.start()
    if duplicated_scenarios:
        print_parallel('scenario.duplicated_scenarios',
                       json.dumps(duplicated_scenarios, indent=4))
        exit(1)
    if features_with_no_scen_desc:
        print_parallel('feature.empty_scenario_descriptions',
                       '\n* '.join(features_with_no_scen_desc))
        exit(1)

    # Sort scenarios by execution order if enabled (only the filtered scenarios that will actually run)
    if order_tests_enabled:
        serial_scenarios.sort(key=lambda s: s.get("scenario_order", 9999))
        parallel_scenarios.sort(key=lambda s: s.get("scenario_order", 9999))

    if serial_scenarios:
        print_parallel('scenario.serial_execution')
        for scen_info in serial_scenarios:
            if _mark_run_stopped_if_requested():
                break
            scenarios_to_run_in_feature = total_scenarios_to_run[scen_info["feature_filename"]]
            serial_result = _execute_serial_tests(features_path=scen_info["features_path"],
                                                        feature_filename=scen_info["feature_filename"],
                                                        feature_json_skeleton=scen_info["feature_json_skeleton"],
                                                        scenarios_to_run_in_feature=scenarios_to_run_in_feature,
                                                        scenario_line=scen_info["scenario_line"],
                                                        multiprocess=True,
                                                        config=ConfigRun(),
                                                        lock=None,
                                                        shared_removed_scenarios=shared_removed_scenarios)
            if serial_result is None:
                break
            execution_code, json_report = serial_result
            execution_codes.append(execution_code)
            json_reports.append(json_report)
            state.fire_report_progress(json_report)
            if global_vars.progress_bar_instance:
                global_vars.progress_bar_instance.update()
    if parallel_scenarios:
        print_parallel('scenario.running_parallels')


        # Prepare scenarios grouped by order
        if order_tests_strict:
            # Group scenarios by their order value for strict sequential ordering
            scenarios_by_order = {}
            for scenario_info in parallel_scenarios:
                order = scenario_info.get("scenario_order", 9999)
                if order not in scenarios_by_order:
                    scenarios_by_order[order] = []
                scenarios_by_order[order].append(scenario_info)
        elif order_tests_enabled:
            # Sort scenarios by order but allow parallel execution
            parallel_scenarios.sort(key=lambda s: s.get("scenario_order", 9999))
            scenarios_by_order = {9999: parallel_scenarios}
        else:
            # Put all scenarios in a single group for original behavior
            scenarios_by_order = {9999: parallel_scenarios}

        # Execute scenarios by order groups
        for order in sorted(scenarios_by_order.keys()):
            scenario_group = scenarios_by_order[order]
            group_futures = []

            # Submit all scenarios of the current order
            for scenario_information in scenario_group:
                scenarios_to_run_in_feature = total_scenarios_to_run[scenario_information["feature_filename"]]
                features_path = scenario_information["features_path"]
                feature_filename = scenario_information["feature_filename"]
                feature_json_skeleton = scenario_information["feature_json_skeleton"]
                scenario_line = scenario_information["scenario_line"]
                future = _submit_unless_stopped(process_pool, execute_tests,
                                                features_path=features_path,
                                                feature_filename=feature_filename,
                                                feature_json_skeleton=feature_json_skeleton,
                                                scenarios_to_run_in_feature=scenarios_to_run_in_feature,
                                                scenario_line=scenario_line,
                                                multiprocess=True,
                                                config=ConfigRun(),
                                                lock=lock,
                                                shared_removed_scenarios=shared_removed_scenarios
                                                )
                if future is None:
                    break
                _add_report_callback(future, execution_codes, json_reports)
                group_futures.append(future)

            # Wait for completion of this order group before proceeding to the next
            _wait_for_futures(group_futures, execution_codes)
    return execution_codes, json_reports


def execute_tests_in_worker_forwarding_to_host(execute_tests_kwargs, manager):
    """Run execute_tests in the run's worker; its output and on_progress events reach this process live."""
    host_queue = manager.Queue()
    worker_messages_forwarder = threading.Thread(target=host_messages.forward_worker_messages, args=(host_queue,), daemon=True)
    worker_messages_forwarder.start()
    try:
        worker_future = state.active_executor.submit(execute_tests, host_queue=host_queue, **execute_tests_kwargs)
        try:
            return worker_future.result()
        except KeyboardInterrupt:
            # behave stops with the scenarios that ran once the worker gets it; a second Ctrl+C aborts
            _interrupt_worker_processes()
            return worker_future.result()
    except BrokenProcessPool as error:
        return _crashed_worker_result(error)
    finally:
        host_queue.put(None)
        worker_messages_forwarder.join()


def _execute_serial_tests(**execute_tests_kwargs):
    """Run in the run's worker when a BehaveXRunner host started the run, keeping behave's steps out of the host.

    Returns None when BehaveXRunner.stop() kept the work from starting.
    """
    if not state.run_active:
        return execute_tests(**execute_tests_kwargs)
    try:
        future = _submit_unless_stopped(state.active_executor, execute_tests, **execute_tests_kwargs)
        if future is None:
            return None
        return future.result()
    except CancelledError:
        state.stopped = True
        return None
    except BrokenProcessPool as error:
        return _crashed_worker_result(error)


def _crashed_worker_result(error):
    """The execution code and empty report a parallel run records for a worker that died."""
    print_parallel('process.pool.broken.main', str(error))
    return 2, {'environment': [], 'features': [], 'steps_definition': []}


def _interrupt_worker_processes():
    """Send SIGINT to the run's workers, which an interrupt of this process alone (as Jupyter's) misses."""
    if os.name != 'posix':
        # os.kill would terminate the worker on Windows, where a console Ctrl+C reaches it anyway
        return
    for worker_process in live_run_worker_processes():
        os.kill(worker_process.pid, signal.SIGINT)


def live_run_worker_processes():
    # active_children() also lists a BehaveXRunner host application's own processes
    return [worker_process for worker_process in list(state.active_executor_processes_by_pid.values())
            if worker_process.is_alive()]

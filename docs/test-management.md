# Test Management

## Muting Test Scenarios

Add the `@MUTE` tag to scenarios that are failing but not critical to the build. Muted scenarios are still executed, but their failures are excluded from JUnit reports. Results remain visible in the HTML report.

```gherkin
@MUTE
Scenario: Known flaky scenario
    Given ...
```

## Auto-Retry for Failing Scenarios

### @AUTORETRY Tag

For scenarios prone to intermittent failures, use the `@AUTORETRY` tag to automatically re-execute on failure. The latest execution result is the one reported.

```gherkin
@AUTORETRY
Scenario: Flaky integration test

@AUTORETRY_3
Scenario: Retry up to 3 times
```

Specify the number of retries as a suffix (e.g., `@AUTORETRY_3` retries up to 3 times).

## Rerunning Failed Scenarios

After a test run, BehaveX generates a `failing_scenarios.txt` file in the output folder listing all failed scenarios. Use it to rerun only the failures:

```bash
behavex -rf=./output/failing_scenarios.txt
# or
behavex --rerun-failures=./output/failing_scenarios.txt
```

Specify a different output folder to avoid overwriting the previous report:

```bash
behavex --rerun-failures=./output/failing_scenarios.txt -o=output_rerun
```

## Progress Bar in Console

Display a real-time progress bar during parallel test execution:

```bash
behavex --parallel-processes=3 --show-progress-bar
behavex -t=@TAG --parallel-processes=3 --show-progress-bar
```

If you print logs to the console, configure the progress bar to write each update on a new line to avoid conflicts:

```ini
[progress_bar]
print_updates_in_new_lines = True
```

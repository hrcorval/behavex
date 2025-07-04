Version History
===============================================================================

Version: 4.2.4
-------------------------------------------------------------------------------

ENHANCEMENTS:

* Improved formatter output directory management by implementing dynamic detection of formatter-specific output directories. This ensures consistent paths between evidence storage and formatter output, resolving issues where images and attachments were not appearing in reports.
* Standardized the formatter_manager architecture to support seamless integration of new custom formatters. Formatters can now define their preferred output directory through a `DEFAULT_OUTPUT_DIR` class attribute, enabling generic and extensible formatter loading without hardcoded dependencies.


Version: 4.2.3
-------------------------------------------------------------------------------

ENHANCEMENTS:

* Enhanced TeePrint stdout wrapper to support complete file-like interface, preventing AttributeError exceptions when test code calls methods like `isatty()`, `encoding`, `closed`, `fileno()`, etc. This ensures full compatibility with testing frameworks and libraries that expect complete stdout functionality.
* Improved handling of execution interruption (Ctrl+C) by properly propagating KeyboardInterrupt and SystemExit exceptions to allow graceful termination of test execution in both single-process and parallel execution modes.

CONTRIBUTIONS:

* Thanks to `bombsimon <https://github.com/bombsimon>`__ for helping us to fix the issue with the TeePrint stdout wrapper.


Version: 4.2.2
-------------------------------------------------------------------------------

ENHANCEMENTS:

* Adding "thread" label in Allure report formatter to allow associating the scenarios to parallel processes.

FIXES:

* Fixing an issue that caused incorrect XML report filenames when handling Windows paths or other edge-case feature paths.
* Enhanced robustness in before_scenario hook, to add error handling on every method that is called in this hook.
* Fixed exception handling in concurrent execution contexts to properly catch all exceptions including SystemExit, KeyboardInterrupt, and GeneratorExit, ensuring more robust parallel test execution.

CONTRIBUTIONS:

* Thanks to `withnale <https://github.com/withnale>`__ for contributing to the implementation of the "thread" label.
* Thanks to `AppeltansPieter <https://github.com/AppeltansPieter>`__ for reporting the issue with XML report filenames.


Version: 4.2.1
-------------------------------------------------------------------------------

ENHANCEMENTS:

* Adding support in the Allure formatter for parameters in Scenario Outlines.
* Adding a new `--no-formatter-attach-logs` command-line argument to allow disabling the attachment of scenario logs in the Allure report.

FIXES:

* Fixing an issue in the Allure formatter where the stack trace of a failed test was incorrectly categorized as a test parameter.
* Fixing an issue with the Allure formatter's output directory logic to correctly handle custom paths.
* Fixing an issue in the Allure formatter that caused incorrect package names to be generated in reports.


Version: 4.2.0
-------------------------------------------------------------------------------

ENHANCEMENTS:

* Adding support for allure reports, by providing a new formatter that will be an alternative to the default reporter.

CONTRIBUTIONS:

* Special thanks to `afritachi <https://github.com/afritachi>`__ for sponsoring BehaveX! Your support helps us keep improving and growing the project — we truly appreciate it!

Version: 4.1.2
-------------------------------------------------------------------------------

ENHANCEMENTS:

* Support for Python 3.13
* Improvement done to replace the htmlmin library with minify-html, as htmlmin is deprecated.


Version: 4.1.1
-------------------------------------------------------------------------------

ENHANCEMENTS:

* Improvement done when reporting exceptions, as despite the traceback is being reported, the exception message was not being displayed.
* Improvement done to display the correct exit code when execution crashes in environment hooks.


Version: 4.1.0
-------------------------------------------------------------------------------

ENHANCEMENTS:

* Cosmetic improvements in documentation

FIXES:

* Fixing issue when re-executing failing scenarios using the -rf option, as there where scenario outline examples not being considered in the re-execution

Version: 4.0.10
-------------------------------------------------------------------------------

ENHANCEMENTS:

* Enable multiple BehaveX processes to run at the same time, by creating unique execution output files in temporary folders for each process.

FIXES:

* Avoid executing environment.py hooks when a dry run is performed.

Version: 4.0.9
-------------------------------------------------------------------------------

ENHANCEMENTS:

* Adding support for latest Python versions (3.12)
* Performing cross-platform validations as part of github actions workflow (Linux, Windows and MacOS)
* Enabling adding scenario lines in feature paths when running BehaveX
* Fixing issue when performing dry runs, as internal @BHX_MANUAL_DRY_RUN tag was not removed from the scenario tags

FIXES:

* Fixing execution issues in Windows OS when running BehaveX with a feature path different than the current path.
* Fixing encoding issues in progress bar in Windows OS

Version: 4.0.8
-------------------------------------------------------------------------------
ENHANCEMENTS:

* Enhanced parallel scenario execution management by utilizing scenario lines over scenario names. This allows running scenarios that might change their name without causing issues in parallel executions.

FIXES:

* Avoid using the scenario name as part of the hash to generate output paths, as if the scenario name is changed, the path does not match. Instead, the feature filename and the line where the scenario is located is used to generate the hash.


Version: 4.0.7
-------------------------------------------------------------------------------
ENHANCEMENTS:

* Improved KeyboardInterrupt handling when running BehaveX in parallel, by terminating all child processes before exiting.
* Simplified library documentation (README.md)
* Added more tests to validate BehaveX is working as expected when using latest stable Behave version (1.2.6)
* Adding the possibility to copy the scenario name in the HTML report

FIXES:

* Fix done when generating the features path (if not specified, BehaveX will use the current path as features path)
* Fix done when managing tags in scenario outlines
* Fix done when analyzing empty features
* Fix done to remove ansi color codes from the log files and HTML reporter (`fd3c375 <https://github.com/hrcorval/behavex/commit/fd3c3756a13d9e47823f286022980e54e306d6da>`_)


Version: 4.0.5
-------------------------------------------------------------------------------
ENHANCEMENTS:

* Added the 'worker_id' context.config.userdata parameter to allow users to identify which worker is executing every feature or scenario when running tests in parallel. `PR #121 <https://github.com/hrcorval/behavex/pull/121>`_
* Adding the --parallel-delay argument, to enable setting a staggered execution when running tests in parallel. `Issue #142 <https://github.com/hrcorval/behavex/issues/142>`_

FIXES:

* Standardized XML report generation for parallel and single-process runs. `Issue #144 <https://github.com/hrcorval/behavex/issues/144>`_

CONTRIBUTIONS:

* Contributions from `JackHerRrer <https://github.com/JackHerRrer>`__, by providing the implementation to include the 'worker_id' context.config.userdata parameter (Thanks JackHerRrer!!)


Version: 4.0.2
-------------------------------------------------------------------------------
ENHANCEMENTS:

* Changed core implementation to use **concurrent.futures.ProcessPoolExecutor** for parallel executions, avoiding crashes when a test scenario fails. `Issue #114 <https://github.com/hrcorval/behavex/issues/114>`_
* Added information popup in HTML report, containing parallel execution settings and execution times (start time, end time, total time and scenarios duration).
* Displayed "Untested" scenarios in the HTML report.
* Updated progress bar to create a new line after completion.
* Included ENVIRONMENT_DETAILS environment variable to enable users to provide environment information in JSON and HTML reports.

FIXES:

* Fixed HTML report generation issue when running in parallel and a scenario crashed, causing BehaveX to hang.
* Updated JUnit reports to mark unexpectedly crashed scenarios as "failed" instead of "skipped".
* Corrected parallel execution summary to report the number of skipped scenarios accurately.
* Fixed progress bar issue when running tests in parallel by feature.
* Fixed issue when processing scenario tags, to always consider the tags associated with the scenario outline examples.

CONTRIBUTIONS:

* Contributions from `Zoran Lazarevic <https://github.com/lazareviczoran>`__, `Simon Sawert <https://github.com/bombsimon>`__, `Jonathan Bridger <https://github.com/jbridger>`__ for reporting and providing a solution to `Issue #114 <https://github.com/hrcorval/behavex/issues/114>`_. This is a significant improvement for this framework (Thanks!!)


Version: 3.3.0
-------------------------------------------------------------------------------
ENHANCEMENTS:

* Enabling BehaveX to attach screenshots to the HTML report (by incorporating the behavex-images library)
* Improvement in progress bar, to remove any trailing content displayed in console when printing the progress bar

CONTRIBUTIONS:

* Contribution from `Ana Mercado <https://github.com/abmercado19>`__ by providing the implementation of the `behavex-images <https://github.com/abmercado19/behavex-images>`__ library (Thanks Ana!!)


Version: 3.2.13
-------------------------------------------------------------------------------
ENHANCEMENTS:

* Adding a progress bar to the console when running in parallel to better track the execution progress (arguments: -spb or --show-progress-bar)
* Adding workflow to validate the BehaveX wrapper is properly installed in latest python versions (v3.8 to v3.11)
* Updated pre-commit hooks to use them in every commit
* Removing some parameters that are no longer used

FIXES:

* Fixed blank report issue reported in some cases when running tests in parallel
* Fixed issues when performing a dry-run when there are no features/scenarios tagged as MANUAL


Version: 3.2.0
-------------------------------------------------------------------------------
ENHANCEMENTS:

* Improvement done when rendering feature background steps in HTML report
* Reporting scenarios that crashed during execution as "Untested" in HTML report (scenarios that crashed were not reported in previous BehaveX versions)
* Enhancement in HTML Report to add feature tags to scenarios
* Contribution from `Axel Furlan <https://github.com/AxelFurlanF>`__ by fixing deprecation warning when using latest Behave version (1.2.6)  `PR 116 <https://github.com/hrcorval/behavex/pull/116>`_  (Thanks Axel!!)

FIXES:

* Fixed console summary, to properly report the number of scenarios executed
* Fix done when executing features in parallel, as not all features where considered for execution
* Fixed JUnit reports to properly report all executed scenarios (as some of them were missing)

Version: 3.0.0
-------------------------------------------------------------------------------
ENHANCEMENTS:

* Enable Behavex to execute features located in different paths (behavex <features_path1> <features_path2> ... <features_pathN>)
* Printing the HTML output report path in the console at the end of the test execution
* Printing the paths where the features are located when behavex execution is started  `Issue #88 <https://github.com/hrcorval/behavex/issues/88>`_
* Printing the execution summary when running tests in parallel
* Major improvement done to enable re-executing all failing scenarios in parallel
* Enable scenario outlines to be executed in parallel (running the outline examples in parallel)
* HTML Report layout improvements to properly render long gherkin steps and long failure messages.  `Issue #81 <https://github.com/hrcorval/behavex/issues/81>`_
* Improvement done when parallel execution cannot be launched due to duplicated scenario names, by throwing an error exit code  `Issue #86 <https://github.com/hrcorval/behavex/issues/86>`_

FIXES:

* Fix done when logging exceptions in environment.py module
* Fix done when processing the tags associated to scenario outline examples.  `Issue #85 <https://github.com/hrcorval/behavex/issues/85>`_
* Fix done to detect and process scenarios written in different languages (Scenario detection does not work for Non-English languages). `Issue #77 <https://github.com/hrcorval/behavex/issues/77>`_
* Fix done to properly render step.text in HTML report. `Issue #79 <https://github.com/hrcorval/behavex/issues/79>`_
* Fix done when parsing empty feature files.

CONTRIBUTORS:

* Contribution from `seb <https://github.com/sebns>`__ providing the fix to an issue when parsing tags associated to scenario outline examples (Thanks!!)

Version: 2.0.1
-------------------------------------------------------------------------------
ENHANCEMENTS:

* Enabling Behavex to execute features located in a different path by specifying the Features Path (Behavex <features_path>)
* Displaying the number of features in the "Feature" column
* Showing the number of unique steps and total step executions in the "Steps" chart

FIXES:

* Fix implemented when parsing scenario outlines containing names in examples
* Adding missing webhooks related to tags (before_tag and after_tag)

Version: 1.6.0
-------------------------------------------------------------------------------

ENHANCEMENTS:

* Improvement in the order in which the events are executed in environment.py. On every "before_<something>" event, the BehaveX event has precedence over the same event in testing solution, and the other way around should be on every "after_<something>" event
* Reusing FEATURES_PATH environment variable to indicate were features are located

FIXES:

* Fix implemented when scenarios are dynamically skipped or removed from the execution list
* Fix implemented in scenario outlines, as scenarios were not being published in execution reports when examples are part of scenario descriptions and contain white spaces

Version: 1.5.12
-------------------------------------------------------------------------------

ENHANCEMENTS:

* Reporting the average reusability of test steps in metrics
* Consider not only the scenario description but also the feature description when creating the evidence path, to avoid issues with duplicated scenario names
* Improvement done in HTML report to consider line breaks in reported error messages in failing steps

FIXES:

* Fixed issue when executing scenarios using the "--include" argument


Version: 1.5.11
-------------------------------------------------------------------------------

ENHANCEMENTS:

* Enable wrapper execution using the **main** method instead of the **behavex** executable: **"python -m behavex -t /<tag/> ..."**

Version: 1.5.10
-------------------------------------------------------------------------------

ENHANCEMENTS:

* Changes done to **rerun-failures** argument, to request the **failing_scenarios.txt** path as argument value

FIXES:

* Enable re-executing failing scenarios that contain blank spaces in path or filename


Version: 1.5.9
-------------------------------------------------------------------------------

FIXES:

* Another encoding fix applied to the HTML report to avoid breaking it on failing scenarios

NOTES:

* We apologize for all the previous versions that were generated in such a short period of  time. We have been working on including all requests from BehaveX users, and we were missing some of them (so we created new versions), and we did some mistakes in the meantime. We will organize to make it better next time

CONTRIBUTIONS:

* Contribution from `Ravi Salunkhe <https://github.com/salunkhe-ravi>`__ about sample project that instances the BehaveX wrapper: https://github.com/salunkhe-ravi/behavex-boilerplate-framework (Thanks Ravi!!)


Version: 1.5.8
-------------------------------------------------------------------------------

FIXES:

* Adding pending encoding fix to leave everything up and running smoothly


Version: 1.5.7
-------------------------------------------------------------------------------

FIXES:

* Reverting back implementation to normalize scenario names to be backward compatible
* Fixing additional encoding issues reported by customers


Version: 1.5.6
-------------------------------------------------------------------------------

FIXES:

* Fixing side efect with "--rerun-failures (or -rf)" argument that was not considered in local tests


Version: 1.5.5
-------------------------------------------------------------------------------

ENHANCEMENTS:

* Small refactoring over the "--rerun-failures (or -rf)" argument functionality, to store the file with failures into the root folder instead of the output folder, avoiding the file to get deleted after a re-execution.

DOCUMENTATION:

* Adding documentation to re-execute failing scenarios.

Version: 1.5.4
-------------------------------------------------------------------------------

ENHANCEMENTS:

* Fixed issue with scenario outlines containing quotes in description (scenario name not properly parsed)
* Fixed encoding issues with step descriptions in HTML report
* Enabled wrapper to run with latest python versions

Version: 1.5.3
-------------------------------------------------------------------------------

ENHANCEMENTS:

* Added support for examples arguments in scenario outline descriptions

DOCUMENTATION:

* Adding HTML report screenshots to documentation

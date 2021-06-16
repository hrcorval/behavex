# BehaveX
BehaveX is a test wrapper on top of Behave, that provides additional capabilites that are useful in testing pipelines.
Basically, using this wrapper you will be able to:
* Perform parallel test executions (multi-process executions)
  * By feature
  * By scenario
* Get additional test execution reports.
  * Friendly HTML report
  * JSON report (enable exporting|integrating test execution information)
* Provide additional evidence as part of execution reports
  * Any testing evidence you get, you can paste it to a predefined folder path (by scenario) to be part of the HTML report
* Generate test logs per scenario
  * Whatever you log in test steps using the logging library, it will generate an individual log report for each scenario
* Mute test scenarios in build servers
  * By just adding the @MUTE tag to test scenarios, they will be executed, but they will not be part of the JUnit reports
* Generate metrics in HTML report for the executed test suite
  * Automation Rate, Pass Rate and Steps executions & duration
* Execute dry runs and see the full list of scenarios into the HTML report
  * This is an override of the Behave dry run implementation

### Constraints

* BehaveX is currently implemented over Behave **v1.2.6**, and not all Behave arguments are yet supported.
* To perform parallel test executions the implementation triggers parallel Behave processes. So, whatever you have in the **before_all** and **after_all** methods in **environment.py** module, it will be re-executed on every parallel process. Also, the same will happen with the **before_feature** and **after_feature** methods when the parallel execution schema is set by scenario.
* The stop argument does not work when performing parallel test executions.
* The JUnit reports have been replaced by the ones created by the test wrapper, just to support muting tests
* The library is provided as is, and no tests over the framework have been implemented yet (there were tests at the beginning but they got deprecated). Any contribution on that end will help on delivering with confidence new library versions.
* Some english translations might not be correct (even in docstrings) so we will be working on fixing this.

### Supported Behave arguments
The following Behave arguments are currently supported:
* no_color
* color
* define
* exclude
* include
* no_snippets
* no_capture
* name
* capture
* no_capture_stderr
* capture_stderr
* no_logcapture
* logcapture
* logging_level
* summary
* quiet
* stop
* tags
* tags-help

There might be more arguments that can be supported, it is just a matter of adapting the wrapper implementation to use these.

### Additional BehaveX arguments
* output_folder
  * Specifies the output folder for all execution reports
    * JUnit: <output_folfer>/behave/*.xml
    * HTML: <output_folfer>/report.html
    * JSON: <output_folfer>/report.json
* dry-run
  * Overwrites the Behave dry-run implementation
  * Performs a dry-run by listing the scenarios as part of the output reports
* parallel_processes
  * Specifies the number of parallel Behave processes
* parallel_scheme
  * Performs the parallel test execution by [scenario|feature]

### Parallel test executions
Parallel test implementation is based on parallel Behave instances executed in multiple processes.

As mentioned as part of the wrapper constraints, this approach implies that whatever you have in the Python Behave hooks in **environment.py** module, it will be re-executed on every parallel process.

BehaveX will be in charge of managing each parallel process, and consolidate all the information into the execution reports

Parallel test executions can be performed by **feature** or by **scenario**.

Examples:
> behavex -t \<TAG\> --parallel-processes 2 --parallel-schema scenario

> behavex -t \<TAG\> --parallel-processes 5 --parallel-schema feature

When the parallel-schema is set by **feature**, all tests within each feature will be run sequentially.

### Additional test execution reports


### Additional evidence
### Metrics
### Dry runs
### Mute test scenarios

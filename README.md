# BehaveX
BehaveX is a test wrapper on top of Behave, that provides additional capabilites that are useful in testing pipelines.
Basically, using this wrapper you will be able to:
* Perform parallel test executions (multi-process executions)
  * By feature
  * By scenario
* Get additional test execution reports.
  * Friendly HTML report
  * JSON report (to enable exporting test execution information)
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

There might be probably more arguments that can be supported, is just a matter of adapting the wrapper implementation to use it.

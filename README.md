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

It is important to mention that this wrapper is currently implemented over Behave 1.2.6, and not all Behave arguments are yet supported.

Version History
===============================================================================

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

CONTRIBUTIONS:

* Contribution from `Ravi Salunkhe <https://github.com/salunkhe-ravi>`__ about sample project that instances the BehaveX wrapper: https://github.com/salunkhe-ravi/behavex-boilerplate-framework (Thanks Ravi!!)

Version: 1.5.3
-------------------------------------------------------------------------------

ENHANCEMENTS:

* Added support for examples arguments in scenario outline descriptions

DOCUMENTATION:

* Adding HTML report screenshots to documentation


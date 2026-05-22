# Getting Started

## Installation

```bash
pip install behavex
```

### Behave Version Compatibility

BehaveX is compatible with the following Behave versions:

- **Behave 1.2.6** (stable, widely tested)
- **Behave >= 1.3.0**

BehaveX automatically installs a compatible version of Behave. If you need a specific version:

```bash
# For Behave 1.2.6 (stable)
pip install behavex behave==1.2.6

# For Behave 1.3.0 or newer (latest)
pip install behavex behave>=1.3.0
```

## Quick Start

Run BehaveX from the command line the same way as Behave:

```bash
# Run all scenarios
behavex

# Run scenarios tagged @smoke with 4 parallel processes
behavex -t=@smoke --parallel-processes=4

# Run and output reports to a specific folder
behavex -t=@smoke -o=test-results
```

## Execution Examples

- **Run scenarios tagged as `TAG_1` but not `TAG_2`:**
  ```bash
  # v1 syntax (all Behave versions)
  behavex -t=@TAG_1 -t=~@TAG_2

  # v2 syntax (Cucumber Style, Behave 1.3.0+)
  behavex -t="@TAG_1 and not @TAG_2"
  ```

- **Run scenarios tagged as `TAG_1` or `TAG_2`:**
  ```bash
  # v1 syntax
  behavex -t=@TAG_1,@TAG_2

  # v2 syntax
  behavex -t="@TAG_1 or @TAG_2"
  ```

- **Run scenarios with 4 parallel processes:**
  ```bash
  behavex -t=@TAG_1 --parallel-processes=4 --parallel-scheme=scenario
  ```

- **Run scenarios from specific folders:**
  ```bash
  behavex features/features_folder_1 features/features_folder_2 --parallel-processes=2
  ```

- **Run scenarios from a specific feature file:**
  ```bash
  behavex features_folder_1/sample_feature.feature --parallel-processes=2
  ```

- **Perform a dry run and generate the HTML report:**
  ```bash
  behavex -t=@TAG_1 --dry-run
  ```

- **Run with execution ordering enabled:**
  ```bash
  behavex -t=@TAG_1 --order-tests --parallel-processes=2
  ```

- **Run complex tag expressions (Behave 1.3.0+):**
  ```bash
  behavex -t="(@api or @ui) and @high_priority and not @flaky" --parallel-processes=4
  ```

See [Tag Expressions](tag-expressions.md) for the full filtering reference.

## Migration to BehaveX 4.5.0 + Behave >= 1.3.0

When upgrading to BehaveX 4.5.0 with Behave 1.3.0 or newer, be aware of the following:

### Breaking Changes in Behave >= 1.3.0

- **Case-sensitive step definitions**: Step definitions are now case-sensitive. Mismatches between feature files and step definitions cause "undefined step" errors.

- **Trailing colons in steps**: Steps with trailing colons (`:`) are no longer automatically cleaned by Behave and may not be detected properly.

- **Relative imports**: Using relative paths in imports may cause issues. Update to absolute import paths.

### BehaveX 4.5.0 Changes

- **Error status preservation**: BehaveX now preserves the original "error" status from Behave instead of converting it to "failed" (except in HTML reports). This may affect tools expecting the previous behavior.

### Resources

- [Behave Documentation — What's New](https://behave.readthedocs.io/en/latest/new_and_noteworthy/)

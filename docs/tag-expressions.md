# Tag Expressions

BehaveX supports two types of tag expressions for filtering test scenarios.

## Tag Expressions v1 (Legacy Format)

Tag Expressions v1 use a simple syntax compatible with all Behave versions:

```bash
# Run scenarios with a specific tag
behavex -t=@smoke

# Exclude scenarios with a tag
behavex -t=~@slow

# Multiple conditions (AND logic)
behavex -t=@smoke -t=~@slow

# Multiple tags (OR logic)
behavex -t=@smoke,@regression
```

**Advanced v1 examples:**
```bash
# Smoke tests excluding slow ones
behavex -t=@smoke -t=~@slow

# Regression or integration tests
behavex -t=@regression,@integration

# Critical tests excluding known issues
behavex -t=@critical -t=~@known_issue

# Multiple exclusions
behavex -t=@api -t=~@slow -t=~@flaky
```

## Tag Expressions v2 (Cucumber Style)

> **Note:** Tag Expressions v2 require **Behave 1.3.0 or newer**. BehaveX automatically detects v2 syntax and uses Behave's native parser.

### Boolean Operators

```bash
# AND logic
behavex -t="@smoke and @api"

# OR logic
behavex -t="@smoke or @regression"

# NOT logic
behavex -t="not @slow"

# Combinations
behavex -t="@smoke and not @slow"
```

### Parentheses Grouping

```bash
behavex -t="(@smoke or @regression) and not @slow"
behavex -t="(@smoke and @api) or (@regression and @ui)"
behavex -t="(((@smoke or @regression) and @api) or @critical) and not @slow"
```

### Wildcard Matching

```bash
# Prefix matching
behavex -t="@smoke*"        # Matches @smoke, @smoke_test, @smoke_api

# Suffix matching
behavex -t="@*_test"        # Matches @api_test, @ui_test, @smoke_test

# Substring matching
behavex -t="@*smoke*"       # Matches @smoke, @smoke_test, @test_smoke

# Wildcard combinations
behavex -t="@smoke* and not @*_slow"
behavex -t="@*_api or @*_ui"
```

### Advanced v2 Examples

```bash
# Production-ready filtering
behavex -t="(@smoke or @regression) and not (@slow or @flaky)"

# Environment-specific
behavex -t="@api and (@staging or @production) and not @experimental"

# Feature-based with wildcards
behavex -t="@user* and (@*_positive or @*_critical) and not @*_slow"

# Complex business logic
behavex -t="((@smoke and @high_priority) or @critical) and not (@known_issue or @skip)"
```

### Multiple `-t` Arguments

Multiple `-t` arguments are combined with AND logic:

```bash
behavex -t="@smoke or @regression" -t="not @slow"
# Equivalent to: (@smoke or @regression) and (not @slow)
```

## Version Compatibility

| Feature | Behave 1.2.6 | Behave 1.3.0+ |
|---------|--------------|----------------|
| Tag Expressions v1 | ✅ Full Support | ✅ Full Support |
| Tag Expressions v2 | ❌ Not Supported | ✅ Full Support |
| Boolean operators (and, or, not) | ❌ | ✅ |
| Parentheses grouping | ❌ | ✅ |
| Wildcard matching | ❌ | ✅ |

## Migration from v1 to v2

```bash
# v1 Format                              v2 Equivalent
behavex -t=@smoke -t=~@slow          →  behavex -t="@smoke and not @slow"
behavex -t=@smoke,@regression        →  behavex -t="@smoke or @regression"
behavex -t=@api -t=~@slow -t=~@flaky →  behavex -t="@api and not @slow and not @flaky"
```

## Best Practices

- **Use quotes** around v2 expressions to prevent shell interpretation
- **Test expressions** with `--dry-run` to verify scenario selection before running
- **Prefer v2 syntax** for better readability when using Behave 1.3.0+
- **Use wildcards** to reduce maintenance when tag naming follows patterns
- **Group complex logic** with parentheses for clarity

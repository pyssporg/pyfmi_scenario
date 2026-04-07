# Scenario Data Format

The Scenario FMU receives its behavior through the string parameter
`scenario_input`.

Each line defines one output series.

## Format

```text
name;interpolation;time_0,value_0;time_1,value_1;...
```

Multiple series are separated by newlines:

```text
speed;L;0,0;5,10;10,10
mode;ZOH;0,0;3,1;7,2
lane;NN;0,1;10,2
```

## Fields

- `name`: Output variable name exposed in `modelDescription.xml`
- `interpolation`: Interpolation mode used by the FMU
- `time_i,value_i`: One sample point in the series

## Supported Interpolation Codes

The repository currently uses these interpolation codes in tests and examples:

- `L`: Linear interpolation
- `ZOH`: Zero-order hold
- `NN`: Nearest-neighbor interpolation

## Example

```text
var1;L;1,0;3,0.5;5,4;9,2
var2;ZOH;2,0;3,0.5;5,4;9,2
var3;NN;0,0;1,0.5;2,4;3,2
```

This creates three FMU outputs:

- `var1`
- `var2`
- `var3`

The corresponding FMI value references start at `1`. Value reference `0` is
reserved for the string parameter `scenario_input`.

## Behavior Model

The FMU:

- Stores the raw string through `fmi2SetString`
- Parses the series during `fmi2ExitInitializationMode`
- Advances internal time during `fmi2DoStep`
- Evaluates outputs at the current time when `fmi2GetReal` is called

## Authoring Guidance

- Use one signal per line.
- Keep timestamps monotonic within a series.
- Use explicit decimal points when possible to avoid ambiguity.
- Keep names stable, because they become FMU output variable names.

## Common Patterns

Constant value with `ZOH`:

```text
enable;ZOH;0,1
```

Ramp with `L`:

```text
speed;L;0,0;2,4;4,8
```

Discrete mode switches:

```text
mode;NN;0,0;5,1;10,2
```

## Where This Is Used

You can supply this format through:

- `scenario-fmu-package --scenario-data ...`
- `scenario-fmu-ssv --scenario-data ...`
- `scenario-fmu-run --scenario-input ...`
- Direct FMI parameter setting on `scenario_input`

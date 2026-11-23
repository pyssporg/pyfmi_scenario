/*
 * Model behaviour for the scenario FMU.
 *
 * This file is copied over the generated scenario_model.cpp by
 * pyfmu_scenario.codegen. It implements the five hooks declared in
 * scenario_hooks.h against the generated scenario_Instance and vr_map.
 *
 * The runtime contract is one String parameter, scenario_input, holding the
 * scenario grammar documented in docs/scenario-format.md. The grammar is
 * parsed once in fmi2ExitInitializationMode, stored in user_data, and every
 * declared output is evaluated at the communication point.
 *
 * FMI 2.0 Co-Simulation only. Cubic interpolation is declared by the grammar
 * but unsupported, exactly as in the Python reference evaluator.
 */

#include "scenario_hooks.h"

#include <cctype>
#include <cerrno>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <exception>
#include <new>
#include <string>
#include <vector>

#include "scenario_scenario_data.h"

namespace {

enum class Interpolation {
  Linear,
  ZeroOrderHold,
  NearestNeighbour,
};

struct Sample {
  double time;
  double value;
};

struct Series {
  std::string name;
  Interpolation interpolation;
  std::vector<Sample> samples;
};

struct State {
  std::vector<Series> series;
};

/*
 * The hooks receive only the instance, so they cannot reach the
 * fmi2CallbackFunctions logger that the generated runtime holds. A rejected
 * parameter is reported on stderr and returned as fmi2Error; the runtime adds
 * its own status log for the failed FMI call.
 */
void report(const char* message) {
  std::fprintf(stderr, "[scenario] %s\n", message);
}

void report(const std::string& message) {
  report(message.c_str());
}

std::string trim(const std::string& text) {
  std::size_t first = 0;
  while (first < text.size() &&
         std::isspace(static_cast<unsigned char>(text[first])) != 0) {
    ++first;
  }
  std::size_t last = text.size();
  while (last > first &&
         std::isspace(static_cast<unsigned char>(text[last - 1])) != 0) {
    --last;
  }
  return text.substr(first, last - first);
}

std::vector<std::string> split(const std::string& text, char separator) {
  std::vector<std::string> fields;
  std::string current;
  for (char character : text) {
    if (character == separator) {
      fields.push_back(current);
      current.clear();
    } else {
      current.push_back(character);
    }
  }
  fields.push_back(current);
  return fields;
}

std::vector<std::string> split_lines(const std::string& text) {
  std::vector<std::string> lines;
  std::string current;
  for (std::size_t index = 0; index < text.size(); ++index) {
    const char character = text[index];
    if (character == '\r') {
      lines.push_back(current);
      current.clear();
      if (index + 1 < text.size() && text[index + 1] == '\n') {
        ++index;
      }
    } else if (character == '\n') {
      lines.push_back(current);
      current.clear();
    } else {
      current.push_back(character);
    }
  }
  if (!current.empty()) {
    lines.push_back(current);
  }
  return lines;
}

bool parse_number(const std::string& token, double& value) {
  if (token.empty()) {
    return false;
  }
  // strtod also accepts C hexadecimal floats, which Python's float() does not.
  if (token.find('x') != std::string::npos ||
      token.find('X') != std::string::npos) {
    return false;
  }
  errno = 0;
  char* end = nullptr;
  const char* begin = token.c_str();
  value = std::strtod(begin, &end);
  if (end == begin || *end != '\0' || errno == ERANGE ||
      !std::isfinite(value)) {
    return false;
  }
  return true;
}

bool parse_interpolation(
    const std::string& token, Interpolation& interpolation,
    std::string& error) {
  if (token == "L") {
    interpolation = Interpolation::Linear;
    return true;
  }
  if (token == "ZOH") {
    interpolation = Interpolation::ZeroOrderHold;
    return true;
  }
  if (token == "NN") {
    interpolation = Interpolation::NearestNeighbour;
    return true;
  }
  if (token == "C") {
    error =
        "cubic interpolation ('C') is declared by the scenario grammar but "
        "is not implemented";
    return false;
  }
  error = "unknown interpolation '" + token + "'; expected 'L', 'ZOH', or 'NN'";
  return false;
}

bool parse_series(
    const std::string& line, std::size_t line_number, Series& series,
    std::string& error) {
  const std::vector<std::string> raw = split(line, ';');
  if (raw.size() < 3) {
    error = "line " + std::to_string(line_number) +
            ": expected 'name;interpolation;time,value[;time,value...]'";
    return false;
  }

  series.name = trim(raw[0]);
  if (series.name.empty()) {
    error = "line " + std::to_string(line_number) + ": series name is empty";
    return false;
  }

  const std::string interpolation = trim(raw[1]);
  if (interpolation.empty()) {
    error =
        "line " + std::to_string(line_number) + ": interpolation is empty";
    return false;
  }
  if (!parse_interpolation(interpolation, series.interpolation, error)) {
    error = "line " + std::to_string(line_number) + ": " + error;
    return false;
  }

  series.samples.clear();
  for (std::size_t index = 2; index < raw.size(); ++index) {
    const std::string field = trim(raw[index]);
    const std::vector<std::string> coordinates = split(field, ',');
    if (coordinates.size() != 2 || trim(coordinates[0]).empty() ||
        trim(coordinates[1]).empty()) {
      error = "line " + std::to_string(line_number) + ": sample '" + field +
              "' is not 'time,value'";
      return false;
    }
    Sample sample{0.0, 0.0};
    if (!parse_number(trim(coordinates[0]), sample.time)) {
      error = "line " + std::to_string(line_number) + ": time '" +
              coordinates[0] + "' must be a finite number";
      return false;
    }
    if (!parse_number(trim(coordinates[1]), sample.value)) {
      error = "line " + std::to_string(line_number) + ": value '" +
              coordinates[1] + "' must be a finite number";
      return false;
    }
    if (!series.samples.empty() &&
        sample.time <= series.samples.back().time) {
      error = "line " + std::to_string(line_number) + ": series '" +
              series.name + "' times must be strictly increasing";
      return false;
    }
    series.samples.push_back(sample);
  }
  return true;
}

bool parse_scenario(const std::string& text, State& state, std::string& error) {
  const std::string body = trim(text);
  if (body.empty()) {
    error = "scenario text is empty";
    return false;
  }

  const std::vector<std::string> lines = split_lines(body);
  state.series.clear();
  for (std::size_t index = 0; index < lines.size(); ++index) {
    if (trim(lines[index]).empty()) {
      error = "line " + std::to_string(index + 1) + ": empty series";
      return false;
    }
    Series series;
    if (!parse_series(lines[index], index + 1, series, error)) {
      return false;
    }
    for (const Series& existing : state.series) {
      if (existing.name == series.name) {
        error = "duplicate series name '" + series.name + "'";
        return false;
      }
    }
    state.series.push_back(series);
  }
  return true;
}

bool matches_declared_outputs(const State& state, std::string& error) {
  if (state.series.size() != scenario_output_count) {
    error = "scenario defines " + std::to_string(state.series.size()) +
            " series but the FMU exposes " +
            std::to_string(scenario_output_count) + " outputs";
    return false;
  }
  for (std::size_t index = 0; index < scenario_output_count; ++index) {
    const char* name = scenario_outputs[index].name;
    bool found = false;
    for (const Series& series : state.series) {
      if (series.name == name) {
        found = true;
        break;
      }
    }
    if (!found) {
      error = std::string("scenario does not define the declared output '") +
              name + "'";
      return false;
    }
  }
  return true;
}

const Series* find_series(const State& state, const char* name) {
  for (const Series& series : state.series) {
    if (series.name == name) {
      return &series;
    }
  }
  return nullptr;
}

double evaluate(const Series& series, double time) {
  const std::vector<Sample>& samples = series.samples;
  if (time < samples.front().time) {
    return 0.0;
  }
  if (time >= samples.back().time) {
    return samples.back().value;
  }

  // Rightmost sample with time <= current time.
  std::size_t low = 0;
  std::size_t high = samples.size();
  while (low < high) {
    const std::size_t middle = low + (high - low) / 2;
    if (samples[middle].time <= time) {
      low = middle + 1;
    } else {
      high = middle;
    }
  }
  const std::size_t index = low - 1;
  const Sample& left = samples[index];
  if (time == left.time) {
    return left.value;
  }
  const Sample& right = samples[index + 1];

  switch (series.interpolation) {
    case Interpolation::ZeroOrderHold:
      return left.value;
    case Interpolation::NearestNeighbour:
      if (std::fabs(time - left.time) <= std::fabs(time - right.time)) {
        return left.value;
      }
      return right.value;
    case Interpolation::Linear:
      break;
  }
  const double span = right.time - left.time;
  const double fraction = (time - left.time) / span;
  return left.value + fraction * (right.value - left.value);
}

fmi2Status apply(scenario_Instance* instance, const State& state, double time) {
  for (std::size_t index = 0; index < scenario_output_count; ++index) {
    const scenario_OutputBinding& binding = scenario_outputs[index];
    const Series* series = find_series(state, binding.name);
    if (series == nullptr) {
      report(std::string("missing parsed series '") + binding.name + "'");
      return fmi2Error;
    }
    if (binding.vr >= scenario_VrCount) {
      report("declared output value reference is out of range");
      return fmi2Error;
    }
    scenario_VrMapping& mapping = instance->vr_map[binding.vr];
    if (mapping.data == nullptr || mapping.type != SCENARIO_DATA_REAL) {
      report(std::string("output '") + binding.name +
             "' has no Real storage");
      return fmi2Error;
    }
    *static_cast<fmi2Real*>(mapping.data) =
        static_cast<fmi2Real>(evaluate(*series, time));
  }
  return fmi2OK;
}

void free_state(scenario_Instance* instance) {
  if (instance == nullptr) {
    return;
  }
  delete static_cast<State*>(instance->user_data);
  instance->user_data = nullptr;
}

State* state_of(scenario_Instance* instance) {
  return static_cast<State*>(instance->user_data);
}

}  // namespace

fmi2Status scenario_model_initialize(scenario_Instance* instance) {
  if (instance == nullptr) {
    report("initialize: null instance");
    return fmi2Error;
  }
  free_state(instance);

  State* state = new (std::nothrow) State();
  if (state == nullptr) {
    report("initialize: cannot allocate model state");
    return fmi2Error;
  }

  try {
    std::string error;
    if (!parse_scenario(instance->scenario_input, *state, error)) {
      report("initialize: " + error);
      delete state;
      return fmi2Error;
    }
    if (!matches_declared_outputs(*state, error)) {
      report("initialize: " + error);
      delete state;
      return fmi2Error;
    }

    instance->user_data = state;
    const fmi2Status status = apply(instance, *state, 0.0);
    if (status != fmi2OK) {
      free_state(instance);
    }
    return status;
  } catch (const std::exception& exception) {
    report(std::string("initialize: ") + exception.what());
    delete state;
    instance->user_data = nullptr;
    return fmi2Error;
  } catch (...) {
    report("initialize: unknown exception");
    delete state;
    instance->user_data = nullptr;
    return fmi2Error;
  }
}

fmi2Status scenario_model_do_step(
    scenario_Instance* instance, fmi2Real current_communication_point,
    fmi2Real communication_step_size) {
  if (instance == nullptr) {
    report("do_step: null instance");
    return fmi2Error;
  }
  State* state = state_of(instance);
  if (state == nullptr) {
    report("do_step: model was not initialized");
    return fmi2Error;
  }
  try {
    return apply(instance, *state,
                 current_communication_point + communication_step_size);
  } catch (const std::exception& exception) {
    report(std::string("do_step: ") + exception.what());
    return fmi2Error;
  } catch (...) {
    report("do_step: unknown exception");
    return fmi2Error;
  }
}

fmi2Status scenario_model_terminate(scenario_Instance* instance) {
  if (instance == nullptr) {
    report("terminate: null instance");
    return fmi2Error;
  }
  return fmi2OK;
}

fmi2Status scenario_model_reset(scenario_Instance* instance) {
  if (instance == nullptr) {
    report("reset: null instance");
    return fmi2Error;
  }
  // The runtime restores user_data after the reset, so drop the pointer here.
  free_state(instance);
  return fmi2OK;
}

fmi2Status scenario_model_free(scenario_Instance* instance) {
  if (instance == nullptr) {
    report("free: null instance");
    return fmi2Error;
  }
  free_state(instance);
  return fmi2OK;
}

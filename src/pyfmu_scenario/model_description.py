"""Build the scenario FMU's FMI 2.0 ``modelDescription.xml``.

The document is a ``pyssp_standard`` FMI 2 object; it is serialized through
``pyfmi_interfaces``' annotation-aware codec and validated when the installed
``pyssp_standard`` exposes a validator. No XML is assembled by hand.

The FMI capability flags are spelled exactly as the reference FMU does,
including the explicit ``false`` values. ``pyssp_standard`` emits a known
boolean only when it is true, so the false spellings travel in
``extra_attributes``; this keeps the document structurally equal to
``repos/ssp_references/models/fmu/scenario/fmu/modelDescription.xml``.
"""

from __future__ import annotations

from pyfmi_interfaces import ModelDescription, ModelDescriptionXmlCodec
from pyssp_standard.standard.fmi2.model import (
    Fmi2DefaultExperiment,
    Fmi2ElementInfo,
    Fmi2InterfaceAttributes,
    Fmi2ModelDescriptionDocument,
    Fmi2ModelStructure,
    Fmi2ScalarVariable,
    Fmi2Unknown,
)

from .grammar import Scenario
from .model import (
    AUTHOR,
    DEFAULT_EXPERIMENT,
    DEFAULT_GUID,
    GENERATION_TOOL,
    MODEL_IDENTIFIER,
    MODEL_NAME,
    VERSION,
    build_variables,
)

try:
    from pyssp_standard.standard.fmi2.validation import (
        Fmi2ModelDescriptionValidator,
    )
except ImportError:  # pragma: no cover - depends on the installed standard
    Fmi2ModelDescriptionValidator = None


_CO_SIMULATION_ATTRIBUTES = {
    "canHandleVariableCommunicationStepSize": "true",
    "canInterpolateInputs": "false",
    "providesDirectionalDerivative": "false",
    "needsExecutionTool": "false",
    "canBeInstantiatedOnlyOncePerProcess": "false",
}


def build_document(
    scenario: Scenario,
    *,
    guid: str = DEFAULT_GUID,
) -> Fmi2ModelDescriptionDocument:
    """The FMI 2.0 document for one scenario, before serialization."""
    variables = build_variables(scenario)
    scalar_variables = [
        Fmi2ScalarVariable(
            name=variable.name,
            value_reference=variable.value_reference,
            type_name=variable.type_name,
            description=variable.description,
            causality=variable.causality,
            variability=variable.variability,
            start=variable.start_text,
        )
        for variable in variables
    ]
    return Fmi2ModelDescriptionDocument(
        root=Fmi2ElementInfo(tag="fmiModelDescription"),
        fmi_version="2.0",
        model_name=MODEL_NAME,
        guid=guid,
        description=None,
        author=AUTHOR,
        version=VERSION,
        generation_tool=GENERATION_TOOL,
        generation_date_and_time=None,
        variable_naming_convention="structured",
        number_of_event_indicators=0,
        interface_type="CoSimulation",
        capabilities=Fmi2InterfaceAttributes(
            model_identifier=MODEL_IDENTIFIER,
            provides_directional_derivative=False,
            needs_execution_tool=False,
            can_be_instantiated_only_once_per_process=False,
            can_not_use_memory_management_functions=True,
            extra_attributes=dict(_CO_SIMULATION_ATTRIBUTES),
        ),
        variables=scalar_variables,
        model_structure=Fmi2ModelStructure(
            outputs=[
                Fmi2Unknown(index=variable.index)
                for variable in variables
                if variable.causality == "output"
            ]
        ),
        default_experiment=Fmi2DefaultExperiment(
            start_time=DEFAULT_EXPERIMENT.start_time,
            stop_time=DEFAULT_EXPERIMENT.stop_time,
            tolerance=DEFAULT_EXPERIMENT.tolerance,
        ),
    )


def build_model_description(
    scenario: Scenario,
    *,
    guid: str = DEFAULT_GUID,
) -> str:
    """Serialize and validate the XML text for one scenario."""
    document = build_document(scenario, guid=guid)
    xml = ModelDescriptionXmlCodec().serialize(ModelDescription(document))
    if Fmi2ModelDescriptionValidator is not None:
        Fmi2ModelDescriptionValidator().validate(document, xml)
    return xml


__all__ = ["build_document", "build_model_description"]
